import multiprocessing
import os
import socket
import sys
import threading
import webbrowser
import uvicorn

if __name__ == "__main__":
    multiprocessing.freeze_support()
    if getattr(sys,"frozen",False) and not os.getenv("PDFSUITE_FRONTEND_DIR"):
        os.environ["PDFSUITE_FRONTEND_DIR"]=os.path.join(sys._MEIPASS,"frontend")
    requested=os.getenv("PDFSUITE_PORT")
    if requested: port=int(requested)
    else:
        probe=socket.socket(); probe.bind(("127.0.0.1",0)); port=probe.getsockname()[1]; probe.close()
        threading.Timer(2.0,lambda:webbrowser.open(f"http://127.0.0.1:{port}")).start()
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=port,
        workers=1,
        log_config=None,
        access_log=False,
    )
