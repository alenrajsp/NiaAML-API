from niaaml import PipelineOptimizer
from objects.PipelineOptimizer import WebPipelineOptimizerRun


class PipelineJob:
    def __init__(self, data_id: str, pipeline_optimizer: PipelineOptimizer,
                 pipeline_optimizer_run: WebPipelineOptimizerRun):
        self.data_id: str = data_id
        self.pipeline_optimizer: PipelineOptimizer = pipeline_optimizer
        self.pipeline_optimizer_run: WebPipelineOptimizerRun = pipeline_optimizer_run
