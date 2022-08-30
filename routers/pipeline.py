from fastapi import APIRouter
from fastapi import File, UploadFile, Response
from fastapi.responses import FileResponse
import uuid
from niaaml.data import CSVDataReader
from database import LiteDatabase
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
    ldb = LiteDatabase()
    try:
        if ".csv" in csv_file.filename:
            generated_uuid = uuid.uuid4()
            filename = f"{generated_uuid}.csv"
            file_location = f"{Path(__file__).parent.parent}{sep}data{sep}csvfiles{sep}{filename}"
            with open(file_location, "wb+") as file_object:
                file_object.write(csv_file.file.read())
            ldb.execute("""INSERT INTO jobs (csv, created_at, uuid) VALUES(1, datetime('now'), ?);""",
                        (f"{generated_uuid}",))
            return UploadCsvResult(data_id=str(generated_uuid), result="Success")
        else:
            response.status_code = 400
            return UploadCsvResult(data_id="/", result="Invalid file type")
    except Exception as inst:
        print(inst)
        response.status_code = 400
        return UploadCsvResult(data_id="/", result="Something went wrong")


@router.post('/run')
async def run_csv(web_pipeline_optimizer: WebPipelineOptimizer,
                  web_pipeline_optimizer_run: WebPipelineOptimizerRun,
                  data_id: str):
    """
    Method for running the NiaAML pipeline. Step 2/3 of the API workflow.
    """
    wpo = web_pipeline_optimizer
    file_location = f"{Path(__file__).parent.parent}{sep}data{sep}csvfiles{sep}{data_id}.csv"
    file_exists = Path(file_location).is_file()

    if(file_exists):
        data_reader = CSVDataReader(src=file_location, contains_classes=True, has_header=True)

        ldb = LiteDatabase()

        export = str(uuid.uuid4())

        ldb.add_to_queue(data_id, web_pipeline_optimizer, web_pipeline_optimizer_run, export)
        return PipelineResult(file_id=data_id, result="Added to queue!", export=export)
    else:
        return PipelineResult(file_id="/", result=f"File [{data_id}] not found!")

@router.post('/export/text')
def get_ppln_text(data_id: str):
    """
    Method for exporting the .txt of computed results. Step 3A/3 of the API workflow.
    """
    ldb = LiteDatabase()
    job=ldb.fetch_all("""SELECT * FROM jobs WHERE export=?;""", (data_id,))
    if len(job) < 1:
        return {'Job not found'}
    if len(job) > 1:
        return {'Database conflict.'}
    if len(job) == 1:
        job = ldb.fetch_all("""SELECT * FROM jobs WHERE export=? AND status=?;""", (data_id, "completed"))
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
    ldb = LiteDatabase()
    job = ldb.fetch_all("""SELECT * FROM jobs WHERE uuid=?;""", (data_id,))
    if len(job) < 1:
        return {'Job not found'}
    if len(job) > 1:
        return {'Database conflict.'}
    if len(job) == 1:
        job = ldb.fetch_all("""SELECT * FROM jobs WHERE uuid=? AND status=?;""", (data_id, "completed"))
        if len(job) == 1:
            return FileResponse(path=f"{Path(__file__).parent.parent}{sep}data{sep}pipelineResults{sep}{data_id}.ppln",
                                filename=data_id+'.ppln')
        else:
            return {'not completed'}
