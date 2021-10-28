# NiaAML API

NiaAML API is a Python library for using [NiaAML](https://github.com/lukapecnik/NiaAML) as an FastAPI based web API.

## Installation

1. Download project
2. Install dependencies with Poetry
```bash
poetry install
```
3. Navigate to project folder and run server in terminal.
```bash
uvicorn main:app --reload
```

## How to use (locally)
1. Run server
2. Navigate to [Swagger docs](localhost:8000/docs) to see how to use.


## How to use (Docker)
1. Use the official image from DockerHub repository 
   (alenrajsp/niaamlapi:0.1)[https://hub.docker.com/r/alenrajsp/niaamlapi]
2. Run from terminal with 
   `docker run -p <PORT>:80 alenrajsp/niaamlapi:0.1`. 
   The **\<PORT>** variable is the port from which you want to access the container.
3. If data is to be preserved the **/src/data** folder needs to be made into a volume. 
   The **data** folder contains the following subfolders and files:

| Folder / file      | Description |
| ----------- | ----------- |
| /csvfiles      | Folder where all uploaded csv files are saved.       |
| /pipelineJobsBackup   | Folder where all pipeline parameters are backed up (when tasks are uploaded to the worker queue)        |
| /pipelineResults   | Folder where **.ppln** and **.txt** files of results are saved        |
| jobs.db   | SQLite3 database where all executed and current jobs are saved.        |



### Workflow
#### CSV upload
Only CSV type pipelines from NiaAML are currently supported. To create a remote job call the [/pipeline/uploadCsv](http://localhost:8000/docs) method.
Upload a csv file (with last column of the CSV file as a class). The method returns a **uuid** which is needed in the next step.
### Running the pipeline
To run the pipeline you need to call the [/pipeline/run](http://localhost:8000/docs) method. 
The **data_id** parameter represents the **uuid** returned from the CSV upload method. 
**wait_to_execution** parameter represents if the client is going to wait for the pipeline to complete (**=true**) if the job is meant to be sent over to worker queue (**=false**).

To execute the [example](https://github.com/lukapecnik/NiaAML#example-of-usage) shown in NiaAML documentation the following request is needed.

```
POST http://localhost:8000/pipeline/run?data_id=50e7e53e-f85c-4361-b52a-a31422719743&wait_to_execution=false
REQUEST BODY: {
  "web_pipeline_optimizer": {
    "classifiers": [
      ['AdaBoost', 'Bagging', 'MultiLayerPerceptron', 'RandomForest', 'ExtremelyRandomizedTrees', 'LinearSVC']
    ],
    "feature_selection_algorithms": ['SelectKBest', 'SelectPercentile', 'ParticleSwarmOptimization', 'VarianceThreshold'],
    "feature_transform_algorithms": ['Normalizer', 'StandardScaler'],
    "categorical_features_encoder": null,
    "imputer": null,
    "log": true,
    "log_verbose": true,
    "log_output_file": null
  },
  "web_pipeline_optimizer_run": {
    "fitness_name": "Accuracy",
    "pipeline_population_size": 15,
    "inner_population_size": 15,
    "number_of_pipeline_evaluations": 300,
    "number_of_inner_evaluations": 300,
    "optimization_algorithm": "ParticleSwarmAlgorithm",
    "inner_optimization_algorithm": "ParticleSwarmAlgorithm"
  }
}
```

### Retrieving the results

Once jobs are completed the **.ppln** and **.txt** files can be retrieved using the following two requests:


**.txt result files**
```
POST http://localhost:8000/pipeline/export/text?data_id=50e7e53e-f85c-4361-b52a-a31422719743
```

**.ppln result files**
```
POST http://localhost:8000/pipeline/export/ppln?data_id=50e7e53e-f85c-4361-b52a-a31422719743
```

## Licence

This package is distributed under the MIT License. This license can be found online at <http://www.opensource.org/licenses/MIT>.

## Disclaimer

This framework is provided as-is, and there are no guarantees that it fits your purposes or that it is bug-free. Use it at your own risk!

##References

L. Pečnik, I. Fister Jr. "[NiaAML: AutoML framework based on stochastic population-based nature-inspired algorithms](https://joss.theoj.org/papers/10.21105/joss.02949)." Journal of Open Source Software 6.61 (2021): 2949.