import os
import unittest
from main import app
from fastapi.testclient import TestClient
from database import LiteDatabase
from pathlib import Path

from tests.helper_methods import upload_file, run
from worker.PipelineWorker import run_pipeline

class TestManagementApi(unittest.TestCase):
    data_id1:str = ""
    data_id2:str = ""
    data_id3:str = ""

    @classmethod
    def setUpClass(cls) -> None:

        client = TestClient(app)
        ldb = LiteDatabase()
        response = client.post(url='/management/flush')

        response_file1 = upload_file(client)
        TestManagementApi.data_id1 = response_file1.json()["data_id"]
        run(client, TestManagementApi.data_id1)

        response_file2 = upload_file(client)
        TestManagementApi.data_id2 = response_file2.json()["data_id"]
        run(client, TestManagementApi.data_id2)

        response_file3 = upload_file(client)
        TestManagementApi.data_id3 = response_file3.json()["data_id"]
        run(client, TestManagementApi.data_id3)

        job1 = ldb.fetchall_queue("SELECT * from queue WHERE started_at IS NULL AND csv=?;", (TestManagementApi.data_id1,))[0]
        job2 = ldb.fetchall_queue("SELECT * from queue WHERE started_at IS NULL AND csv=?;", (TestManagementApi.data_id2,))[0]
        job3 = ldb.fetchall_queue("SELECT * from queue WHERE started_at IS NULL AND csv=?;", (TestManagementApi.data_id3,))[0]

        run_pipeline(job1)
        run_pipeline(job2)
        run_pipeline(job3)

    def setUp(self) -> None:
        self.client = TestClient(app)
        self.ldb = LiteDatabase()

    def test1_get_all_jobs(self):
        response = self.client.get('/management/jobs')
        self.assertEqual(response.status_code, 200, "Request successful")
        self.assertEqual(len(response.json()), 3, "Wrong number of all jobs")

    def test2_get_job(self):
        response = self.client.get(f"""/management/jobs?id={TestManagementApi.data_id2}""")

        self.assertEqual(response.status_code, 200, "Request successful")
        self.assertEqual(len(response.json()), 1, "Queried job found")

        response = self.client.get(f"""/management/jobs?id=doesnotexistandisnotauuid""")
        self.assertEqual(response.status_code, 200, "Request successful")
        self.assertEqual(len(response.json()), 0, "Job should not be found")




    def test3_flush(self):
        folder_csvfiles = f"{Path(__file__).parent.parent}{os.sep}data{os.sep}csvfiles{os.sep}"
        folder_pipeline_results = f"{Path(__file__).parent.parent}{os.sep}data{os.sep}pipelineResults{os.sep}"

        csv_files_before=os.listdir(folder_csvfiles)
        pipeline_results_files_before=os.listdir(folder_pipeline_results)

        self.assertEqual(len(csv_files_before), 3, "CSV Upload failed")
        self.assertEqual(len(pipeline_results_files_before), 6, "Export failed")
        response = self.client.post(url='/management/flush')
        self.assertEqual(response.status_code, 200, "Request failed")
        csv_files_after=os.listdir(folder_csvfiles)
        pipeline_results_files_after = os.listdir(folder_pipeline_results)

        self.assertEqual(len(csv_files_after), 0, "Flush failed (csvfiles)")
        self.assertEqual(len(pipeline_results_files_after), 0, "Flush failed (pipelineResults)")



if __name__ == '__main__':
    unittest.main()
