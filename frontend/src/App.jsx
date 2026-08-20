import { useCallback,useEffect,useMemo,useRef,useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { motion } from 'framer-motion'
import { Archive,ArrowDown,ArrowUp,Download,FileImage,FileOutput,FilePlus2,FileText,Info,Layers3,LockKeyhole,Moon,Scissors,ShieldCheck,Sun,UploadCloud,X } from 'lucide-react'
import axios from 'axios'
import toast from 'react-hot-toast'
import PropTypes from 'prop-types'

const MODES=[
 {id:'pdf-to-images',name:'PDF a imágenes',icon:FileImage,accept:{'application/pdf':['.pdf']}},
 {id:'images-to-pdf',name:'Imágenes a PDF',icon:FilePlus2,accept:{'image/*':['.png','.jpg','.jpeg','.bmp','.tiff','.webp']}},
 {id:'merge',name:'Unir PDFs',icon:Layers3,accept:{'application/pdf':['.pdf']}},
 {id:'split',name:'Dividir PDFs',icon:Scissors,accept:{'application/pdf':['.pdf']}},
 {id:'compress',name:'Comprimir PDFs',icon:Archive,accept:{'application/pdf':['.pdf']}},
 {id:'protect',name:'Proteger PDFs',icon:LockKeyhole,accept:{'application/pdf':['.pdf']}},
 {id:'watermark',name:'Marca de agua',icon:ShieldCheck,accept:{'application/pdf':['.pdf']}},
 {id:'extract',name:'PDF a Word/Excel',icon:FileOutput,accept:{'application/pdf':['.pdf']}},
 {id:'metadata',name:'Metadatos',icon:Info,accept:{'application/pdf':['.pdf']}},
]
const INITIAL={format:'png',dpi:150,quality:85,split_mode:'each',ranges:'1-3,4',password:'',allow_copy:false,watermark:'CONFIDENCIAL',opacity:.2,target:'word'}

export default function App(){
 const [dark,setDark]=useState(()=>localStorage.theme!=='light'),[mode,setMode]=useState(MODES[0]),[files,setFiles]=useState([]),[options,setOptions]=useState(INITIAL),[job,setJob]=useState(null)
 const abortRef=useRef(null),timerRef=useRef(null)
 useEffect(()=>{document.documentElement.classList.toggle('dark',dark);localStorage.theme=dark?'dark':'light'},[dark])
 useEffect(()=>()=>{abortRef.current?.abort();clearInterval(timerRef.current)},[])
 const onDrop=useCallback(accepted=>{setFiles(current=>[...current,...accepted].slice(0,50));setJob(null)},[])
 const drop=useDropzone({onDrop,accept:mode.accept,maxSize:100*1024*1024,multiple:true,onDropRejected:()=>toast.error('Archivo no admitido o mayor de 100 MB')})
 const total=useMemo(()=>files.reduce((sum,file)=>sum+file.size,0),[files])
 function choose(next){if(next.id!==mode.id){setMode(next);setFiles([]);setJob(null)}}
 function move(index,direction){setFiles(current=>{const next=[...current],target=index+direction;if(target<0||target>=next.length)return current;[next[index],next[target]]=[next[target],next[index]];return next})}
 function patch(key,value){setOptions(current=>({...current,[key]:value}))}
 async function run(){
  if(!files.length)return
  if(mode.id==='merge'&&files.length<2)return toast.error('Selecciona al menos dos PDFs')
  abortRef.current=new AbortController();const body=new FormData();files.forEach(file=>body.append('files',file));body.append('operation',mode.id);body.append('options',JSON.stringify(options))
  try{
   setJob({status:'subiendo',progress:1})
   const {data}=await axios.post('/api/jobs',body,{signal:abortRef.current.signal,onUploadProgress:event=>setJob({status:'subiendo',progress:Math.min(20,Math.round(event.loaded/(event.total||total)*20))})})
   setJob({...data,progress:data.cached?100:20});if(data.cached){toast.success('Resultado recuperado de caché');return}
   timerRef.current=setInterval(async()=>{try{const response=await axios.get(`/api/jobs/${data.job_id}`,{signal:abortRef.current.signal});const next={...response.data,job_id:data.job_id};setJob(next);if(['completed','failed','cancelled'].includes(next.status)){clearInterval(timerRef.current);next.status==='completed'?toast.success('Lote completado'):toast.error(next.error||'Proceso cancelado')}}catch(error){clearInterval(timerRef.current);if(error.code!=='ERR_CANCELED')toast.error('Se perdió la conexión')}},600)
  }catch(error){if(error.code!=='ERR_CANCELED')toast.error(error.response?.data?.detail||'No se pudo iniciar el trabajo');setJob(null)}
 }
 async function cancel(){if(job?.job_id)await axios.delete(`/api/jobs/${job.job_id}`);abortRef.current?.abort();clearInterval(timerRef.current);setJob(current=>({...current,status:'cancelled',progress:0}))}
 const busy=job&&!['completed','failed','cancelled'].includes(job.status)
 return <main className="min-h-screen bg-slate-50 text-slate-900 transition-colors dark:bg-ink dark:text-white">
  <header className="mx-auto flex max-w-7xl items-center justify-between px-5 py-5"><div className="flex items-center gap-3"><div className="grid h-10 w-10 place-items-center rounded-xl bg-cyan text-ink"><FileText size={22}/></div><div><b>VECTOR</b><span className="ml-1 font-light">PDF SUITE</span><p className="text-[10px] tracking-[.22em] text-slate-500">BATCH · PRIVATE · FAST</p></div></div><button aria-label="Cambiar tema" onClick={()=>setDark(v=>!v)} className="rounded-full border border-slate-300 p-2.5 dark:border-white/10">{dark?<Sun size={18}/>:<Moon size={18}/>}</button></header>
  <section className="mx-auto max-w-7xl px-5 pb-14 pt-5"><div className="mb-8"><h1 className="text-3xl font-black tracking-tight sm:text-5xl">Todo lo que necesitas para tus PDFs.</h1><p className="mt-2 text-slate-500">Procesa hasta 50 archivos a la vez, sin bloquear la interfaz.</p></div>
   <div className="grid gap-6 lg:grid-cols-[245px_1fr]"><nav className="grid grid-cols-2 gap-2 sm:grid-cols-3 lg:block">{MODES.map(item=><button key={item.id} onClick={()=>choose(item)} className={`mb-2 flex w-full items-center gap-3 rounded-xl px-3 py-3 text-left text-sm transition ${mode.id===item.id?'bg-cyan font-semibold text-ink shadow-glow':'text-slate-500 hover:bg-slate-200/70 dark:text-slate-400 dark:hover:bg-white/5'}`}><item.icon size={17}/>{item.name}</button>)}</nav>
    <motion.div key={mode.id} initial={{opacity:0,y:8}} animate={{opacity:1,y:0}} className="rounded-3xl border border-slate-200 bg-white p-5 shadow-2xl shadow-slate-200/50 dark:border-white/10 dark:bg-white/[.035] dark:shadow-black/20 sm:p-8">
     <h2 className="text-2xl font-bold">{mode.name}</h2><p className="mb-6 text-sm text-slate-500">Los archivos se procesan en el orden mostrado.</p>
     <div {...drop.getRootProps()} className={`cursor-pointer rounded-2xl border-2 border-dashed p-8 text-center transition ${drop.isDragActive?'border-cyan bg-cyan/10':'border-slate-300 hover:border-cyan dark:border-white/15'}`}><input {...drop.getInputProps()}/><UploadCloud className="mx-auto mb-3 text-cyan" size={38}/><p className="font-semibold">Arrastra uno o varios archivos aquí</p><p className="mt-1 text-sm text-slate-500">Hasta 50 archivos · 100 MB cada uno · 500 MB por lote</p></div>
     {files.length>0&&<div className="mt-4 max-h-56 space-y-2 overflow-auto pr-1">{files.map((file,index)=><div key={`${file.name}-${file.lastModified}-${index}`} className="flex items-center gap-3 rounded-xl bg-slate-100 p-3 dark:bg-white/5"><FileText className="shrink-0 text-cyan" size={19}/><div className="min-w-0 flex-1"><p className="truncate text-sm font-semibold">{index+1}. {file.name}</p><p className="text-xs text-slate-500">{(file.size/1048576).toFixed(2)} MB</p></div><button aria-label="Subir" onClick={()=>move(index,-1)}><ArrowUp size={16}/></button><button aria-label="Bajar" onClick={()=>move(index,1)}><ArrowDown size={16}/></button><button aria-label="Quitar" onClick={()=>setFiles(current=>current.filter((_,i)=>i!==index))}><X size={17}/></button></div>)}</div>}
     <p className="mt-3 text-right text-xs text-slate-500">{files.length} archivo(s) · {(total/1048576).toFixed(2)} MB</p>
     <Options mode={mode.id} options={options} patch={patch}/>
     {job&&<div className="mt-5"><div className="mb-2 flex justify-between text-xs"><span className="capitalize">{job.status}</span><span>{job.progress||0}%</span></div><div className="h-2 overflow-hidden rounded-full bg-slate-200 dark:bg-white/10"><motion.div animate={{width:`${job.progress||0}%`}} className="h-full bg-cyan"/></div>{job.error&&<p className="mt-2 text-sm text-red-500">{job.error}</p>}</div>}
     <div className="mt-6 flex gap-3">{job?.status==='completed'?<a href={`/api/jobs/${job.job_id}/download`} className="flex flex-1 items-center justify-center gap-2 rounded-xl bg-emerald-400 py-3.5 font-bold text-ink"><Download size={19}/>Descargar resultado</a>:<button disabled={!files.length||busy} onClick={run} className="flex flex-1 items-center justify-center gap-2 rounded-xl bg-cyan py-3.5 font-bold text-ink disabled:cursor-not-allowed disabled:opacity-40"><mode.icon size={19}/>{busy?'Procesando…':'Procesar lote'}</button>}{busy&&<button onClick={cancel} className="rounded-xl border border-red-400 px-5 text-red-500">Cancelar</button>}</div>
    </motion.div></div>
  </section>
  <footer className="border-t border-slate-200/70 px-5 py-5 text-center text-[11px] tracking-wide text-slate-400 dark:border-white/5 dark:text-slate-600">Powered by Ingeniero José Carlos Malacara Espinosa · Hecho con cariño para alumnos y docentes</footer>
 </main>
}

function Options({mode,options,patch}){
 const input="rounded-xl border border-slate-200 bg-slate-50 px-3 py-3 text-sm normal-case text-slate-900 outline-none focus:border-cyan dark:border-white/10 dark:bg-white/5 dark:text-white"
 if(mode==='pdf-to-images')return <div className="mt-6 grid gap-4 sm:grid-cols-3"><label className="field">Formato<select value={options.format} onChange={e=>patch('format',e.target.value)}><option>png</option><option>jpg</option><option>bmp</option><option>tiff</option></select></label><label className="field">Resolución<select value={options.dpi} onChange={e=>patch('dpi',Number(e.target.value))}><option value="150">150 DPI</option><option value="300">300 DPI</option><option value="600">600 DPI</option></select></label><label className="field">Calidad · {options.quality}%<input type="range" min="10" max="100" value={options.quality} onChange={e=>patch('quality',Number(e.target.value))}/></label></div>
 if(mode==='images-to-pdf')return <div className="mt-6"><label className="field">Resolución<select value={options.dpi} onChange={e=>patch('dpi',Number(e.target.value))}><option value="150">150 DPI</option><option value="300">300 DPI</option></select></label></div>
 if(mode==='split')return <div className="mt-6 grid gap-4 sm:grid-cols-2"><label className="field">Método<select value={options.split_mode} onChange={e=>patch('split_mode',e.target.value)}><option value="each">Una página por PDF</option><option value="ranges">Rangos personalizados</option></select></label>{options.split_mode==='ranges'&&<label className="field">Rangos<input className={input} value={options.ranges} onChange={e=>patch('ranges',e.target.value)} placeholder="1-3,4,5-7"/></label>}</div>
 if(mode==='protect')return <div className="mt-6 grid gap-4 sm:grid-cols-2"><label className="field">Contraseña<input className={input} type="password" value={options.password} onChange={e=>patch('password',e.target.value)} minLength="4"/></label><label className="mt-7 flex items-center gap-2 text-sm"><input type="checkbox" checked={options.allow_copy} onChange={e=>patch('allow_copy',e.target.checked)}/>Permitir copiar contenido</label></div>
 if(mode==='watermark')return <div className="mt-6 grid gap-4 sm:grid-cols-2"><label className="field">Texto<input className={input} value={options.watermark} onChange={e=>patch('watermark',e.target.value)}/></label><label className="field">Opacidad · {Math.round(options.opacity*100)}%<input type="range" min="5" max="100" value={options.opacity*100} onChange={e=>patch('opacity',Number(e.target.value)/100)}/></label></div>
 if(mode==='extract')return <div className="mt-6"><label className="field">Destino<select value={options.target} onChange={e=>patch('target',e.target.value)}><option value="word">Word (.docx)</option><option value="excel">Excel (.xlsx)</option></select></label></div>
 return null
}
Options.propTypes={mode:PropTypes.string.isRequired,options:PropTypes.object.isRequired,patch:PropTypes.func.isRequired}
