import os
import unittest

import requests

from main import app
from fastapi.testclient import TestClient
from database import LiteDatabase
from pathlib import Path
from os import sep

from tests.helper_methods import upload_file, export_text, export_ppln, run
from worker.PipelineWorker import run_pipeline



class TestPipelineApi(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.file_location = ""
        self.ldb = LiteDatabase()
        self.data_id = "id"

    def test_csv_upload(self):
        response = upload_file(self.client)
        self.assertEqual(response.status_code, 200, "Request failed!")
        self.assertEqual(response.json()["result"], "Success", "Request failed!")
        self.data_id = response.json()["data_id"]
        self.file_location = f"{Path(__file__).parent.parent}{sep}data{sep}csvfiles{sep}{self.data_id}.csv"
        file_exists = Path(self.file_location).is_file()
        self.assertEqual(file_exists, True, "File has not been found in the predicted folder")

    def test_run_pipeline(self):
        response_upload = upload_file(self.client)
        self.data_id = response_upload.json()["data_id"]
        self.file_location = f"{Path(__file__).parent.parent}{sep}data{sep}csvfiles{sep}{self.data_id}.csv"
        response_run = run(self.client, self.data_id)
        self.assertEqual(response_run.status_code, 200, "Unsuccesful run")

    def test_run_pipeline_export(self):
        response_upload = upload_file(self.client)
        self.data_id = response_upload.json()["data_id"]
        self.file_location = f"{Path(__file__).parent.parent}{sep}data{sep}csvfiles{sep}{self.data_id}.csv"
        response_run = run(self.client, self.data_id)
        self.assertEqual(response_run.status_code, 200, "Unsuccesful run")

        jobs = self.ldb.fetchall_queue("SELECT * from queue WHERE started_at IS NULL AND csv=?;", (self.data_id,))
        try:
            run_pipeline(jobs[0])
        except Exception as e:
            self.assertEqual(False, "Exception with running pipeline", "Exception with running pipeline")

        file_txt_res = export_text(client=self.client, export=response_run.json()["export"])
        self.assertEqual(file_txt_res.status_code, 200, "TXT file export failed")

        file_ppln_res = export_ppln(client=self.client, export=response_run.json()["export"])
        self.assertEqual(file_ppln_res.status_code, 200, "PPLN file export failed")

        a=100


    def tearDown(self) -> None:
        os.remove(self.file_location)

        jobs = self.ldb.fetch_all("SELECT * FROM jobs WHERE uuid = ? AND export IS NOT NULL;", (self.data_id,))

        for job in jobs:
            file_txt = f"{Path(__file__).parent.parent}{sep}data{sep}pipelineResults{sep}{job[-1]}.txt"
            file_ppln = f"{Path(__file__).parent.parent}{sep}data{sep}pipelineResults{sep}{job[-1]}.ppln"
            os.remove(file_txt)
            os.remove(file_ppln)

        self.ldb.execute("DELETE FROM jobs WHERE uuid = ?;", (self.data_id,))
        self.ldb.execute_queue("DELETE FROM queue WHERE csv = ?;", (self.data_id,))


        a=100


if __name__ == '__main__':
    unittest.main()
