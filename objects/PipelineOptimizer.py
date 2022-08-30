from typing import Optional
from pydantic import BaseModel


class WebPipelineOptimizer(BaseModel):
    """JSON model for niaaml.PipelineOptimizer class"""
    classifiers: list[str]
    feature_selection_algorithms: Optional[list[str]]
    feature_transform_algorithms: Optional[list[str]]
    categorical_features_encoder: Optional[str]
    imputer: Optional[str]
    log: Optional[bool]
    log_verbose: Optional[bool]
    log_output_file: Optional[str]


class WebPipelineOptimizerRun(BaseModel):
    """JSON model for niaaml.PipelineOptimizer.run(*) class method"""
    fitness_name: str
    pipeline_population_size: int
    inner_population_size: int
    number_of_pipeline_evaluations: int
    number_of_inner_evaluations: int
    optimization_algorithm: str
    inner_optimization_algorithm: Optional[str]
