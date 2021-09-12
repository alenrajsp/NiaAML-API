import os
import threading
import queue
from os import sep
from database import con, cur
from objects.PipelineJob import PipelineJob
from pathlib import Path
import pickle


def worker():
    while True:
        global stop_threads
        item: PipelineJob
        item = pipeline_queue.get()
        pickle_path = f"{Path(__file__).parent.parent}{sep}data{sep}pipelineJobsBackup{sep}{item.data_id}.pickle"
        if os.path.exists(pickle_path) is False:
            with open(pickle_path, 'wb') as handle:
                pickle.dump(item, handle, protocol=pickle.HIGHEST_PROTOCOL)
        print(f'Working on {item}')
        run_pipeline(item.data_id, item.pipeline_optimizer, item.pipeline_optimizer_run)
        os.remove(path=pickle_path)
        print(f'Finished {item}')
        pipeline_queue.task_done()


def start_previous_jobs():
    count_jobs = 0
    jobs_folder = f"{Path(__file__).parent.parent}{sep}data{sep}pipelineJobsBackup{sep}"
    for filename in os.listdir(jobs_folder):
        if filename.endswith(".pickle"):
            count_jobs += 1
            with open(jobs_folder + filename, 'rb') as handle:
                item = pickle.load(handle)
                pipeline_queue.put(item)
    print(f"Found {count_jobs} queued jobs. Resuming.")


def run_pipeline(data_id, pipeline_optimizer, web_pipeline_optimizer_run):
    """
    Actual function that calls the PipelineOptimizer from NiaAML
    :param data_id:
    :param pipeline_optimizer:
    :param web_pipeline_optimizer_run:
    :return:
    """
    print(f"Running {data_id}")
    cur.execute("""UPDATE jobs SET status='running pipeline', task_started_at=datetime('now') WHERE uuid=?;""",
                (data_id,))
    con.commit()
    pipeline = pipeline_optimizer.run(web_pipeline_optimizer_run.fitness_name,
                                      web_pipeline_optimizer_run.pipeline_population_size,
                                      web_pipeline_optimizer_run.inner_population_size,
                                      web_pipeline_optimizer_run.number_of_pipeline_evaluations,
                                      web_pipeline_optimizer_run.number_of_inner_evaluations,
                                      web_pipeline_optimizer_run.optimization_algorithm,
                                      web_pipeline_optimizer_run.inner_optimization_algorithm)
    pipeline.export(f"{Path(__file__).parent.parent}{sep}data{sep}pipelineResults{sep}{data_id}.ppln")
    pipeline.export_text(f"{Path(__file__).parent.parent}{sep}data{sep}pipelineResults{sep}{data_id}.txt")
    cur.execute(
        """UPDATE jobs SET ppln_text=1, ppln=1, status='completed', completed_at=datetime('now') WHERE uuid=?;""",
        (data_id,))
    con.commit()


pipeline_queue = queue.Queue()
thread = threading.Thread(target=worker, daemon=True)
thread.start()
start_previous_jobs()
print('PipelineWorker started')
