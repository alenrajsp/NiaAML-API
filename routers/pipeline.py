from fastapi import APIRouter
from objects.PipelineJob import PipelineJob
from worker.PipelineWorker import run_pipeline, pipeline_queue
from fastapi import File, UploadFile, Response
from fastapi.responses import FileResponse
import uuid
from niaaml import PipelineOptimizer
from niaaml.data import CSVDataReader
from database import con, cur
from objects.PipelineOptimizer import WebPipelineOptimizer, WebPipelineOptimizerRun
from objects.PipelineResult import PipelineResult
from objects.UploadCsvResult import UploadCsvResult
from pathlib import Path
from os import sep

router = APIRouter(prefix="/pipeline", tags=["pipeline"])


@router.post('/uploadCsv')
def upload_csv(response: Response, csv_file: UploadFile = File(...)):
    """
    Method for uploading CSV file on the server. Step 1/3 of the API workflow.
    """
    try:
        if ".csv" in csv_file.filename:
            generated_uuid = uuid.uuid4()
            filename = f"{generated_uuid}.csv"
            file_location = f"{Path(__file__).parent.parent}{sep}data{sep}csvfiles{sep}{filename}"
            with open(file_location, "wb+") as file_object:
                file_object.write(csv_file.file.read())
            cur.execute("""INSERT INTO jobs (csv, created_at, uuid) VALUES(1, datetime('now'), ?);""",
                        (f"{generated_uuid}",))
            con.commit()
            return UploadCsvResult(file_id=filename, result="Success")
        else:
            response.status_code = 400
            return UploadCsvResult(file_id="/", result="Invalid file type")
    except Exception as inst:
        print(inst)
        response.status_code = 400
        return UploadCsvResult(file_id="/", result="Something went wrong")


@router.post('/run')
async def run_csv(web_pipeline_optimizer: WebPipelineOptimizer,
                  web_pipeline_optimizer_run: WebPipelineOptimizerRun,
                  data_id: str,
                  wait_to_execution: bool):
    """
    Method for running the NiaAML pipeline. Step 2/3 of the API workflow.
    """
    wpo = web_pipeline_optimizer
    file_location = f"{Path(__file__).parent.parent}{sep}data{sep}csvfiles{sep}{data_id}.csv"
    data_reader = CSVDataReader(src=file_location, contains_classes=True, has_header=True)
    pipeline_optimizer = PipelineOptimizer(data=data_reader,
                                           classifiers=wpo.classifiers,
                                           feature_selection_algorithms=wpo.feature_selection_algorithms,
                                           feature_transform_algorithms=wpo.feature_transform_algorithms,
                                           categorical_features_encoder=wpo.categorical_features_encoder)
    if wait_to_execution is True:
        run_pipeline(data_id, pipeline_optimizer, web_pipeline_optimizer_run)
        return PipelineResult(file_id=data_id, result="Completed!")
    else:
        pipeline_job = PipelineJob(data_id, pipeline_optimizer, web_pipeline_optimizer_run)
        pipeline_queue.put(pipeline_job)
        return PipelineResult(file_id=data_id, result="Running in background!")


@router.post('/export/text')
def get_ppln_text(data_id: str):
    """
    Method for exporting the .txt of computed results. Step 3A/3 of the API workflow.
    """
    cur.execute("""SELECT * FROM jobs WHERE uuid=?;""", (data_id,))
    job = cur.fetchall()
    if len(job) < 1:
        return {'Job not found'}
    if len(job) > 1:
        return {'Database conflict.'}
    if len(job) == 1:
        cur.execute("""SELECT * FROM jobs WHERE uuid=? AND completed=?;""", (data_id, True))
        job = cur.fetchall()
        if len(job) == 1:
            return FileResponse(path=f"{Path(__file__).parent.parent}{sep}data{sep}pipelineResults{sep}{data_id}.txt",
                                filename=data_id+'.txt')
        else:
            return {'not completed'}


@router.post('/export/ppln')
def get_ppln_text(data_id: str):
    """
        Method for exporting the .txt of computed results. Step 3B/3 of the API workflow.
    """
    cur.execute("""SELECT * FROM jobs WHERE uuid=?;""", (data_id,))
    job = cur.fetchall()
    if len(job) < 1:
        return {'Job not found'}
    if len(job) > 1:
        return {'Database conflict.'}
    if len(job) == 1:
        cur.execute("""SELECT * FROM jobs WHERE uuid=? AND completed=?;""", (data_id, True))
        job = cur.fetchall()
        if len(job) == 1:
            return FileResponse(path=f"{Path(__file__).parent.parent}{sep}data{sep}pipelineResults{sep}{data_id}.ppln",
                                filename=data_id+'.ppln')
        else:
            return {'not completed'}
