import shutil

from fastapi import APIRouter
from database import LiteDatabase
import os
from pathlib import Path
from typing import Union

router = APIRouter(prefix="/management", tags=['management'])


@router.get("/jobs")
async def jobs(id:Union[str, None]=None):
    """
    Returns list of jobs uploaded on the server. If id is passed, returns the queried job.
    """
    ldb = LiteDatabase()
    rows = None
    if id == None:
        rows = ldb.fetch_all("SELECT * FROM jobs;")
    else:
        rows = ldb.fetch_all("SELECT * FROM jobs WHERE uuid = ?;", (id,))
    jobs = []
    for row in rows:
        jobs.append({'ppln_text': row[0], 'ppln': row[1], 'csv': row[2], 'uuid': row[3], 'status': row[4],
                     'created_at': row[5], 'task_started_at': row[6], 'completed_at': row[7], 'export':row[8] })
    return jobs

def remove_files_from_folder(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

@router.post("/flush")
async def flush():
    """ Clears the database and all current pipeline and csv files on the server."""
    ldb = LiteDatabase()
    count_queue = ldb.fetch_one("""SELECT COUNT(*) FROM jobs;""")
    count_jobs = ldb.fetch_one_queue("""SELECT COUNT(*) FROM queue;""")

    ldb.execute("""DELETE FROM jobs;""")
    ldb.execute_queue("""DELETE FROM queue;""")

    import os, shutil

    folder_csvfiles = f"{Path(__file__).parent.parent}{os.sep}data{os.sep}csvfiles{os.sep}"
    folder_pipeline_results = f"{Path(__file__).parent.parent}{os.sep}data{os.sep}pipelineResults{os.sep}"

    try:
        remove_files_from_folder(folder_csvfiles)
        remove_files_from_folder(folder_pipeline_results)
    except Exception as e:
        print(e)



    return {"result": "Succesfully deleted database", "total_jobs_removed": count_jobs, "total_queue_removed": count_queue}