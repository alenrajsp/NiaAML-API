# NiaAML API

NiaAML API is a Python library for using [NiaAML](https://github.com/lukapecnik/NiaAML) as an FastAPI based web API.
The currently used version of **NiaAML** is **1.1.10**.

## Installation

1. Download project
2. Install dependencies with Poetry
```bash
poetry install
```
3. Navigate to project folder and run server in terminal.
* ```bash uvicorn main:app --reload```
or
* run the ```main.py``` script of the project

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
| /pipelineResults   | Folder where **.ppln** and **.txt** files of results are saved        |
| jobs.db   | SQLite3 database where all executed and current jobs are saved.        |
| jobs.db   | SQLite3 database where all job queues are saved.        |


### Workflow
#### CSV upload
Only CSV type pipelines from NiaAML are currently supported. To create a remote job call the [/pipeline/uploadCsv](http://localhost:8000/docs) method.
Upload a csv file (with last column of the CSV file as a class). The method returns a **uuid** which is needed in the next step.
### Running the pipeline
To run the pipeline you need to call the [/pipeline/run](http://localhost:8000/docs) method. 
The **data_id** parameter represents the **uuid** returned from the CSV upload method. 

To execute the [example](https://github.com/lukapecnik/NiaAML#example-of-usage) shown in NiaAML documentation the following request is needed.

```
POST http://localhost:8000/pipeline/run?data_id=50e7e53e-f85c-4361-b52a-a31422719743
REQUEST BODY: {
  "web_pipeline_optimizer": {
    "classifiers": [
      "AdaBoost"
    ],
    "feature_selection_algorithms": [
      "SelectKBest"
    ],
    "feature_transform_algorithms": [
      "Normalizer"
    ],
    "categorical_features_encoder": "OneHotEncoder",
    "imputer": "SimpleImputer",
    "log": false,
    "log_verbose": false,
    "log_output_file": ""
  },
  "web_pipeline_optimizer_run": {
    "fitness_name": "Accuracy",
    "pipeline_population_size": 5,
    "inner_population_size": 5,
    "number_of_pipeline_evaluations": 5,
    "number_of_inner_evaluations": 5,
    "optimization_algorithm": "ParticleSwarmAlgorithm",
    "inner_optimization_algorithm": "ParticleSwarmAlgorithm"
  }
}
```

The returned response should look something like:
``` JSON
{
  "file_id": "2e4b64b1-e192-4f24-b5c7-045bb51aee67",
  "result": "Added to queue!",
  "export": "85486cf6-f760-4556-9f73-460c1aa0b80d"
}
```
Where the **export** attribute is the input parameter for the *data_id* of */pipeline/export* methods, since more than one pipeline can be created from a CSV file.

### Retrieving the results

Once jobs are completed the **.ppln** and **.txt** files can be retrieved using the following two requests:


**.txt result files** - *note data_id = **export** value of **/pipeline/run** method.
```
POST http://localhost:8000/pipeline/export/text?data_id=50e7e53e-f85c-4361-b52a-a31422719743
```

**.ppln result files**
```
POST http://localhost:8000/pipeline/export/ppln?data_id=50e7e53e-f85c-4361-b52a-a31422719743
```

## Tests
All of the endpoints have functional tests avaliable for them in the **tests** directory. You can also check the tests to better understand how to make requests with the client.

## License
[MIT](https://choosealicense.com/licenses/mit/)