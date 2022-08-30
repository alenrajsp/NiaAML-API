import datetime
import multiprocessing
import queue
from os import sep
import time
import traceback
from niaaml import PipelineOptimizer
from niaaml.data import CSVDataReader

from database import LiteDatabase
from objects.PipelineJob import PipelineJob
from pathlib import Path
import pickle
from concurrent.futures import ProcessPoolExecutor


def run_pipeline(item):
    """
    Actual function that calls the PipelineOptimizer from NiaAML
    :param data_id:
    :param pipeline_optimizer:
    :param web_pipeline_optimizer_run:
    :return:
    """

    print(f'Working on {item}')
    ldb = LiteDatabase()
    file_location = f"{Path(__file__).parent.parent}{sep}data{sep}csvfiles{sep}{item[1]}.csv"
    file_exists = Path(file_location).is_file()

    ldb.execute(
        f"""UPDATE jobs SET ppln=1, ppln_text=1, task_started_at='{str(datetime.datetime.now())}', status='running' WHERE uuid='{item[1]}';""")

    ldb.execute("""UPDATE jobs SET status='running pipeline' WHERE uuid=?;""",
                (item[0],))

    try:
        if file_exists:
            is_error = False
            classifiers = feature_selection_algorithms = feature_transform_algorithms = categorical_features_encoder = None
            imputer = log = log_verbose = log_output_file = fitness_name = pipeline_population_size = None
            number_of_pipeline_evaluations = number_of_inner_evaluations = inner_population_size = None
            try:
                classifiers = eval(item[2])
                feature_selection_algorithms = eval(item[3])
                feature_transform_algorithms = eval(item[4])
                categorical_features_encoder = item[5]
                imputer = item[6]
                log = item[7]
                if log==1:
                    log=True
                else:
                    log=False
                log_verbose = item[8]
                if log_verbose== 1:
                    log_verbose=True
                else:
                    log_verbose=False
                log_output_file=item[9]
                fitness_name=item[10]
                pipeline_population_size=item[11]
                inner_population_size=item[12]
                number_of_pipeline_evaluations=item[13]
                number_of_inner_evaluations=item[14] #fixx
                optimization_algorithm=item[15]
                inner_optimization_algorithm=item[16]
                export=item[22]
            except Exception as e:
                ldb.execute_queue("UPDATE queue SET error=?, status=? WHERE id=?;",
                                  ("Parsing file failed", "Interrupted", item[0]))
                is_error = True

            if is_error == True:
                print(item)
                raise AttributeError("Assigning values from item failed")

            data_reader = None
            try:
                data_reader = CSVDataReader(src=file_location, contains_classes=True, has_header=True)
            except Exception as e:
                is_error=True
                ldb.execute_queue("UPDATE queue SET error=?, status=? WHERE id=?;",
                                  ("Creating CSVDataReader failed", "Interrupted", item[0]))
            if is_error == True:
                print(item)
                raise ValueError("Failed to create CSVDataReader")

            pipeline_optimizer = None

            try:
                pipeline_optimizer = PipelineOptimizer(data=data_reader,
                                                       classifiers=classifiers,
                                                       feature_selection_algorithms=feature_selection_algorithms,
                                                       feature_transform_algorithms=feature_transform_algorithms,
                                                       categorical_features_encoder=categorical_features_encoder,
                                                       imputer=imputer, log=log, log_verbose=log_verbose, log_output_file=log_output_file)
            except Exception as e:
                print(item)
                ldb.execute_queue("UPDATE queue SET error=?, status=? WHERE id=?;",
                                  ("Creating PipelineOptimizer failed", "Interrupted", item[0]))
                is_error=True

            if is_error:
                print(item)
                raise ValueError("Failed to create PipelineOptimizer")


            pipeline = None
            try:
                ldb.execute_queue("UPDATE queue SET status=? WHERE id=?;",
                                  ("Running pipeline", item[0]))
                pipeline=pipeline_optimizer.run(fitness_name, pipeline_population_size, inner_population_size,number_of_pipeline_evaluations, number_of_inner_evaluations, optimization_algorithm, inner_optimization_algorithm)
                ldb.execute_queue("UPDATE queue SET status=? WHERE id=?;",
                                  ("Pipeline completed", item[0]))

            except Exception as e:
                print(item)
                ldb.execute_queue("UPDATE queue SET error=?, status=? WHERE id=?;",
                                  ("Running PipelineOptimizer failed", "Interrupted", item[0]))
                is_error=True

            if is_error == True:
                print(item)
                raise RuntimeError("Failed to run PipelineOptimizer")

            try:
                pipeline.export(f"{Path(__file__).parent.parent}{sep}data{sep}pipelineResults{sep}{export}.ppln")
                pipeline.export_text(f"{Path(__file__).parent.parent}{sep}data{sep}pipelineResults{sep}{export}.txt")
            except Exception as e:
                ldb.execute_queue("UPDATE queue SET error=?, status=? WHERE id=?;",
                                  ("Exporting pipeline result failed", "Interrupted", item[0]))
                is_error=True

            if is_error:
                raise Exception("Export failed")

            ldb.execute_queue("UPDATE queue SET status=?, export=?, completed_at=? WHERE id=?;",("Completed", str(export), str(datetime.datetime.now()), item[0]))
            ldb.execute(f"""UPDATE jobs SET ppln=1, ppln_text=1, completed_at='{str(datetime.datetime.now())}', export='{str(export)}', status='completed' WHERE uuid='{item[1]}';""")

            print(f'Finished {item}')
        else:
            ldb.execute_queue("UPDATE queue SET error=?, status=? WHERE id=?;",
                              ("File not found", "Interrupted", item[0]))
            print("File not found!")
    except Exception as e:
        print(traceback.format_exc())
        print("Pipeline failed -- reason:")
        ldb.execute(
            f"""UPDATE jobs SET status='interrupted' WHERE uuid='{item[1]}';""")
        print(e)

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]



class PipelineWorker(object):
    """
    Class that handles the ProcessPool for concurrent running of pipelines.
    """
    __metaclass__ = Singleton


    def __init__(self):
        print("Creating PipelineWorker")
        self.status="Initialised"
        self.pipeline_queue = queue.Queue()
        cpu_count = multiprocessing.cpu_count()
        if cpu_count>1:
            cpu_count-=1
        self.pool= ProcessPoolExecutor(cpu_count)

    def worker(self):
        while True:
            item: PipelineJob
            ldb = LiteDatabase()
            jobs = ldb.fetchall_queue("SELECT * from queue WHERE started_at IS NULL;")

            for job in jobs:
                print("Submitting job to pool")
                ldb.execute_queue("UPDATE queue SET started_at=? WHERE started_at IS NULL AND id=?;",
                                  (str(datetime.datetime.now()), job[0]))
                self.pool.submit(run_pipeline, job)
            time.sleep(10) #check for tasks every 10 seconds
            #self.pool.submit(run_pipeline, (item))



