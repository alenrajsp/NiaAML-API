from pathlib import Path
from os import sep
import uvicorn
from fastapi import FastAPI

# Create folders if they do not exist.
Path(f"{Path(__file__).parent}{sep}data{sep}").mkdir(parents=True, exist_ok=True)
Path(f"{Path(__file__).parent}{sep}data{sep}csvfiles{sep}").mkdir(parents=True, exist_ok=True)
Path(f"{Path(__file__).parent}{sep}data{sep}pipelineJobsBackup{sep}").mkdir(parents=True, exist_ok=True)
Path(f"{Path(__file__).parent}{sep}data{sep}pipelineResults{sep}").mkdir(parents=True, exist_ok=True)

from routers import pipeline, management


app = FastAPI()

app.include_router(pipeline.router)
app.include_router(management.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
