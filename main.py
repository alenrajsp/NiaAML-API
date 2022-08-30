import threading
from pathlib import Path
from os import sep
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import LiteDatabase
from worker.PipelineWorker import PipelineWorker
from routers import pipeline, management


# Create folders if they do not exist.
Path(f"{Path(__file__).parent}{sep}data{sep}").mkdir(parents=True, exist_ok=True)
Path(f"{Path(__file__).parent}{sep}data{sep}csvfiles{sep}").mkdir(parents=True, exist_ok=True)
Path(f"{Path(__file__).parent}{sep}data{sep}pipelineResults{sep}").mkdir(parents=True, exist_ok=True)


app = FastAPI()
origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pipeline.router)
app.include_router(management.router)

if __name__ == "__main__":
    ldb = LiteDatabase()
    ldb.create_tables_if_not_exist()

    ldb.execute("""UPDATE jobs SET status = 'interrupted' WHERE status='running pipeline';""")
    ldb.execute_queue("""UPDATE queue SET status = 'Interrupted', error='Pipeline did not complete' WHERE started_at IS NOT NULL;""")

    print("Starting worker")
    pplworker = PipelineWorker()
    thread = threading.Thread(target=pplworker.worker, daemon=True)
    thread.start()
    pplworker.status="Thread running"

    print("Running app")
    uvicorn.run(app, host="0.0.0.0", port=8000)
