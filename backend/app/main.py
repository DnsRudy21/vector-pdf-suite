import asyncio, hashlib, json, logging, os, shutil, signal, tempfile, time, uuid
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from .cache import DiskCache
from .config import settings
from .converter import PDFConverter

logging.basicConfig(level=logging.INFO,format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger=logging.getLogger("pdfsuite")
cache=DiskCache(settings.data_dir,settings.cache_ttl_seconds,settings.cache_max_bytes)
jobs:dict[str,dict]={}; tasks:dict[str,asyncio.Task]={}
workers=asyncio.Semaphore(max(1,(os.cpu_count() or 2)-1))
PDF_OPS={"pdf-to-images","merge","split","compress","protect","watermark","extract","metadata"}
IMAGE_TYPES={"image/jpeg","image/png","image/bmp","image/tiff","image/webp"}
METHODS={"pdf-to-images":"pdf_to_images","images-to-pdf":"images_to_pdf","merge":"merge","split":"split","compress":"optimize","protect":"protect","watermark":"watermark","extract":"extract","metadata":"metadata"}

@asynccontextmanager
async def lifespan(_:FastAPI):
    await asyncio.to_thread(cache.cleanup); yield
    for task in tasks.values(): task.cancel()

app=FastAPI(title=settings.app_name,version="2.0.0",lifespan=lifespan)
app.add_middleware(CORSMiddleware,allow_origins=["http://localhost:5173","http://localhost:8080","file://"],allow_methods=["*"],allow_headers=["*"])

class JobResponse(BaseModel):
    job_id:str; status:str; cached:bool=False

def clean_jobs()->None:
    cutoff=time.time()-86400
    for job_id in [key for key,value in jobs.items() if value.get("updated",0)<cutoff]: jobs.pop(job_id,None); tasks.pop(job_id,None)

async def persist_uploads(uploads:list[UploadFile],operation:str,directory:Path)->tuple[list[Path],str]:
    if not uploads or len(uploads)>50: raise HTTPException(400,"Selecciona entre 1 y 50 archivos")
    if operation=="merge" and len(uploads)<2: raise HTTPException(400,"Unir requiere al menos dos PDFs")
    digest=hashlib.sha256(); paths=[]; total=0
    for index,upload in enumerate(uploads):
        content_type=(upload.content_type or "").lower()
        if operation in PDF_OPS and content_type!="application/pdf" and not (upload.filename or "").lower().endswith(".pdf"): raise HTTPException(415,"Esta herramienta solo acepta PDFs")
        if operation=="images-to-pdf" and content_type not in IMAGE_TYPES: raise HTTPException(415,"Formato de imagen no admitido")
        name=Path(upload.filename or f"file-{index}").name; target=directory/f"{index:03d}-{name}"
        file_size=0
        with target.open("wb") as stream:
            while chunk:=await upload.read(1024*1024):
                chunk_size=len(chunk); total+=chunk_size; file_size+=chunk_size
                if total>settings.max_upload_bytes*5 or file_size>settings.max_upload_bytes: raise HTTPException(413,"Máximo 100 MB por archivo y 500 MB por lote")
                digest.update(chunk); stream.write(chunk)
        if operation in PDF_OPS:
            with target.open("rb") as saved:
                if saved.read(5)!=b"%PDF-": raise HTTPException(415,"Uno de los archivos no es un PDF válido")
        paths.append(target); digest.update(name.encode("utf-8",errors="ignore"))
    return paths,digest.hexdigest()

async def execute(job_id:str,sources:list[Path],operation:str,options:dict,key:str,directory:Path)->None:
    jobs[job_id].update(status="queued",progress=2,updated=time.time())
    suffix=".pdf" if operation in {"merge","images-to-pdf"} else ".json" if operation=="metadata" else ".zip"
    try:
        async with workers:
            jobs[job_id].update(status="processing",progress=5,updated=time.time())
            output=directory/f"result{suffix}"
            def update(value:int)->None:
                if jobs[job_id].get("cancel_requested"): raise InterruptedError("Trabajo cancelado")
                jobs[job_id].update(progress=max(5,min(value,98)),updated=time.time())
            method=getattr(PDFConverter,METHODS[operation])
            await asyncio.wait_for(asyncio.to_thread(method,sources,output,options,update),timeout=settings.task_timeout_seconds)
            cached=await asyncio.to_thread(cache.put,key,output,suffix)
            jobs[job_id].update(status="completed",progress=100,result=str(cached),filename=f"vector-{operation}{suffix}",updated=time.time())
    except asyncio.CancelledError:
        jobs[job_id].update(status="cancelled",progress=0,updated=time.time()); raise
    except Exception as exc:
        if isinstance(exc,InterruptedError): jobs[job_id].update(status="cancelled",progress=0,updated=time.time())
        else: logger.exception("Operation %s failed",operation); jobs[job_id].update(status="failed",progress=0,error=str(exc),updated=time.time())
    finally: shutil.rmtree(directory,ignore_errors=True)

@app.get("/api/health")
async def health()->dict: return {"status":"ok","service":settings.app_name,"version":app.version,"workers":workers._value}

@app.get("/api/capabilities")
async def capabilities()->dict: return {"operations":list(METHODS),"max_files":50,"max_file_mb":100,"max_batch_mb":500}

@app.post("/api/desktop/shutdown",include_in_schema=False)
async def desktop_shutdown(token:str)->dict:
    expected=os.getenv("PDFSUITE_SHUTDOWN_TOKEN")
    if not expected or token!=expected: raise HTTPException(403,"No autorizado")
    asyncio.get_running_loop().call_later(.25,lambda:os.kill(os.getpid(),signal.SIGTERM))
    return {"status":"shutting-down"}

@app.post("/api/jobs",response_model=JobResponse,status_code=202)
async def create_job(files:Annotated[list[UploadFile],File()],operation:Annotated[str,Form()],options:Annotated[str,Form()]="{}")->JobResponse:
    clean_jobs()
    if operation not in METHODS: raise HTTPException(400,"Operación no admitida")
    try: parsed=json.loads(options)
    except json.JSONDecodeError as exc: raise HTTPException(400,"Opciones JSON inválidas") from exc
    directory=Path(tempfile.mkdtemp(prefix="pdfsuite-job-"))
    try: sources,content_hash=await persist_uploads(files,operation,directory)
    except Exception: shutil.rmtree(directory,ignore_errors=True); raise
    key=hashlib.sha256(f"{content_hash}:{operation}:{json.dumps(parsed,sort_keys=True)}".encode()).hexdigest()
    hit=await asyncio.to_thread(cache.get,key); job_id=uuid.uuid4().hex
    if hit:
        shutil.rmtree(directory,ignore_errors=True); jobs[job_id]={"status":"completed","progress":100,"result":str(hit),"filename":f"vector-{operation}{hit.suffix}","updated":time.time()}
        return JobResponse(job_id=job_id,status="completed",cached=True)
    jobs[job_id]={"status":"queued","progress":0,"operation":operation,"files":len(sources),"updated":time.time()}
    tasks[job_id]=asyncio.create_task(execute(job_id,sources,operation,parsed,key,directory))
    return JobResponse(job_id=job_id,status="queued")

@app.post("/api/convert/pdf-to-images",response_model=JobResponse,status_code=202)
async def legacy_convert(file:Annotated[UploadFile,File()],image_format:Annotated[str,Form()]="png",dpi:Annotated[int,Form()]=150,quality:Annotated[int,Form()]=85)->JobResponse:
    return await create_job([file],"pdf-to-images",json.dumps({"format":image_format,"dpi":dpi,"quality":quality}))

@app.get("/api/jobs/{job_id}")
async def job_status(job_id:str)->dict:
    if job_id not in jobs: raise HTTPException(404,"Trabajo no encontrado")
    return {key:value for key,value in jobs[job_id].items() if key not in {"result","updated"}}

@app.delete("/api/jobs/{job_id}")
async def cancel_job(job_id:str)->dict:
    if job_id not in jobs: raise HTTPException(404,"Trabajo no encontrado")
    task=tasks.get(job_id)
    if task and not task.done(): jobs[job_id]["cancel_requested"]=True; jobs[job_id]["status"]="cancelling"
    return {"status":jobs[job_id]["status"]}

@app.get("/api/jobs/{job_id}/download")
async def download(job_id:str)->FileResponse:
    job=jobs.get(job_id)
    if not job or job.get("status")!="completed": raise HTTPException(404,"El resultado no está listo")
    path=Path(job["result"])
    if not path.exists(): raise HTTPException(410,"El resultado expiró")
    media={".pdf":"application/pdf",".json":"application/json",".zip":"application/zip"}.get(path.suffix,"application/octet-stream")
    return FileResponse(path,media_type=media,filename=job["filename"])

frontend_dir=os.getenv("PDFSUITE_FRONTEND_DIR")
if frontend_dir and Path(frontend_dir).is_dir():
    app.mount("/",StaticFiles(directory=frontend_dir,html=True),name="frontend")
