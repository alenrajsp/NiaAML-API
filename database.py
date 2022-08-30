import datetime
import sqlite3
from pathlib import Path
from os import sep

from objects.PipelineOptimizer import WebPipelineOptimizerRun, WebPipelineOptimizer

"""
This script creates a local SQLite 3 database for managing and tracking NiaAML jobs.
"""

class LiteDatabase():
    """
    Class for handling the queries with the SQLite database.
    """
    def execute(self,  *args, **kwargs):
        """
        Method that executes a query to the SQLite jobs database. Same as **sqlite3.cursor().execute(*args, **kwargs)**

        :param args:
        :param kwargs:
        :return: void
        """
        con = sqlite3.connect(f"{Path(__file__).parent}{sep}data{sep}jobs.db", check_same_thread=False, timeout=10)
        cur = con.cursor()
        cur.execute(*args, **kwargs)
        con.commit()
        cur.close()
        con.close()
    def fetch_all(self, *args, **kwargs):
        """
        Method that executes a query to the SQLite jobs database with a return fetchall statement.
        Same as **sqlite3.cursor().execute(*args, **kwargs); return = cur.fetchall()**

        :param args:
        :param kwargs:
        :return: list
        """
        con = sqlite3.connect(f"{Path(__file__).parent}{sep}data{sep}jobs.db", check_same_thread=False, timeout=10)
        cur = con.cursor()
        cur.execute(*args, **kwargs)
        job = cur.fetchall()
        cur.close()
        con.close()
        return job
    def fetch_one(self, *args, **kwargs):
        """
        Method that executes a query to the SQLite jobs database with a return fetchall statement.
        Same as **sqlite3.cursor().execute(*args, **kwargs); return = cur.fetchall()**

        :param args:
        :param kwargs:
        :return: list
        """
        con = sqlite3.connect(f"{Path(__file__).parent}{sep}data{sep}jobs.db", check_same_thread=False, timeout=10)
        cur = con.cursor()
        cur.execute(*args, **kwargs)
        job = cur.fetchone()
        cur.close()
        con.close()
        return job
    def add_to_queue(self, data_id, wpo:WebPipelineOptimizer, wpr: WebPipelineOptimizerRun, export:str):
        """
        Adds entry to jobs queue in the SQLite queue database.

        :param data_id:
        :param wpo:
        :param wpr:
        :return: void
        """
        con = sqlite3.connect(f"{Path(__file__).parent}{sep}data{sep}queue.db", check_same_thread=False, timeout=10)
        cur = con.cursor()

        cur.execute("""INSERT INTO queue (csv, wpo_classifiers, wpo_feature_selection_algorithms, 
        wpo_feature_transform_algorithms, wpo_imputer, wpo_categorical_features_encoder, wpo_log, wpo_log_verbose, 
        wpo_log_output_file, wpr_fitness_name, wpr_pipeline_population_size, wpr_inner_population_size, 
        wpr_number_of_pipeline_evaluations, wpr_number_of_inner_pipeline_evaluations, wpr_optimization_algorithm,
        wpr_inner_optimization_algorithm, created_at, status, export) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? );""",
                    (data_id, str(wpo.classifiers), str(wpo.feature_selection_algorithms),
                     str(wpo.feature_transform_algorithms), str(wpo.imputer), wpo.categorical_features_encoder, wpo.log,
                     wpo.log_verbose, wpo.log_output_file,  wpr.fitness_name, wpr.pipeline_population_size,
                     wpr.inner_population_size, wpr.number_of_pipeline_evaluations, wpr.number_of_inner_evaluations,
                     wpr.optimization_algorithm, wpr.inner_optimization_algorithm, str(datetime.datetime.now()), "started", export))
        con.commit()
        cur.close()
        con.close()

    def execute_queue(self, *args, **kwargs):
        con = sqlite3.connect(f"{Path(__file__).parent}{sep}data{sep}queue.db", check_same_thread=False, timeout=10)
        cur = con.cursor()
        cur.execute(*args, **kwargs)
        con.commit()
        cur.close()
        con.close()

    def fetchall_queue(self, *args, **kwargs):
        con = sqlite3.connect(f"{Path(__file__).parent}{sep}data{sep}queue.db", check_same_thread=False, timeout=10)
        cur = con.cursor()
        cur.execute(*args, **kwargs)
        queue = cur.fetchall()
        cur.close()
        con.close()
        return queue

    def fetch_one_queue(self, *args, **kwargs):
        """
        Method that executes a query to the SQLite jobs database with a return fetchall statement.
        Same as **sqlite3.cursor().execute(*args, **kwargs); return = cur.fetchall()**

        :param args:
        :param kwargs:
        :return: list
        """
        con = sqlite3.connect(f"{Path(__file__).parent}{sep}data{sep}queue.db", check_same_thread=False, timeout=10)
        cur = con.cursor()
        cur.execute(*args, **kwargs)
        job = cur.fetchone()
        cur.close()
        con.close()
        return job


    def create_tables_if_not_exist(self):
        """
        Creates jobs and queue database tables if they do not previously exist.
        :return: void
        """
        self.execute("""CREATE TABLE IF NOT EXISTS jobs 
                       (ppln_text INTEGER DEFAULT 0, 
                       ppln INTEGER DEFAULT 0, 
                       csv INTEGER DEFAULT 0, 
                       uuid text,
                       status TEXT DEFAULT 'csv uploaded',
                       created_at TEXT,
                       task_started_at TEXT,
                       completed_at TEXT)""")

        self.execute_queue("""CREATE TABLE IF NOT EXISTS "queue" (
        "id"	INTEGER,
        "csv"	TEXT NOT NULL,
        "wpo_classifiers"	TEXT,
        "wpo_feature_selection_algorithms"	TEXT,
        "wpo_feature_transform_algorithms"	TEXT,
        "wpo_categorical_features_encoder"	TEXT,
        "wpo_imputer"	TEXT,
        "wpo_log"	INTEGER NOT NULL,
        "wpo_log_verbose"	INTEGER,
        "wpo_log_output_file"	TEXT,
        "wpr_fitness_name"	TEXT,
        "wpr_pipeline_population_size"	INTEGER,
        "wpr_inner_population_size"	INTEGER,
        "wpr_number_of_pipeline_evaluations"	INTEGER,
        "wpr_number_of_inner_pipeline_evaluations"	INTEGER,
        "wpr_optimization_algorithm"	TEXT,
        "wpr_inner_optimization_algorithm"	TEXT,
        "created_at"	TEXT,
        "started_at"	TEXT,
        "completed_at"	TEXT,
        "status"	TEXT,
        "error"	TEXT,
        "export"	TEXT,
        PRIMARY KEY("id" AUTOINCREMENT)
        );""")

