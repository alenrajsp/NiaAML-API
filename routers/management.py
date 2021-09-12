from fastapi import APIRouter
from database import cur, con
import os

router = APIRouter(prefix="/management", tags=['management'])


@router.get("/jobs")
async def all_jobs():
    """
    Returns list of all jobs uploaded on the server.
    """
    cur.execute("SELECT * FROM jobs;")
    rows = cur.fetchall()
    jobs = []
    for row in rows:
        jobs.append({'ppln_text': row[0], 'ppln': row[1], 'csv': row[2], 'status': row[3], 'created_at': row[4],
                     'task_started_at': row[5], 'completed_at': row[6]})

    return jobs


''' TO DO
@router.post("/flush")
async def flush():
    """ Clears the database and all current pipeline and csv files on the server."""
    count_jobs = cur.execute("""SELECT COUNT(*) FROM jobs;""").fetchone()[0]

    os.remove()

    cur.execute("""DELETE FROM jobs;""")
    con.commit()
    return {"result": "Succesfully deleted jobs", "total_jobs_removed": count_jobs}
'''