import sqlite3
from pathlib import Path
from os import sep

"""
This script creates a local SQLite 3 database for managing and tracking NiaAML jobs.
"""
print('Connecting and initialising  SQLite database!')
con = sqlite3.connect(f"{Path(__file__).parent}{sep}data{sep}jobs.db", check_same_thread=False)
cur = con.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS jobs 
               (ppln_text INTEGER DEFAULT 0, 
               ppln INTEGER DEFAULT 0, 
               csv INTEGER DEFAULT 0, 
               uuid text,
               status TEXT DEFAULT 'csv uploaded',
               created_at TEXT,
               task_started_at TEXT,
               completed_at TEXT)""")
print('Connected to "Pipeline jobs database"!')

cur.execute("""UPDATE jobs SET status = 'interrupted' WHERE status='running pipeline';""")
con.commit()
