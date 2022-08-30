import requests
from fastapi.testclient import TestClient

def upload_file(client:TestClient) -> requests.Response:
    with open('./data/data.csv', 'rb') as f:
        file = {'csv_file': f}
        return client.post(
            url="/pipeline/uploadCsv",
            files=file
        )

def run(client:TestClient, data_id:str) -> requests.Response:
    wpo = {'classifiers': ['AdaBoost'],
           'feature_selection_algorithms': ['SelectKBest'],
           'feature_transform_algorithms': ['Normalizer'],
           'categorical_features_encoder': 'OneHotEncoder',
           'imputer': 'SimpleImputer',
           'log': False,
           'log_verbose': False,
            'log_output_file': None}
    wpor = {
        'fitness_name': 'Accuracy',
        'pipeline_population_size': 5,
        'inner_population_size': 5,
        'number_of_pipeline_evaluations': 5,
        'number_of_inner_evaluations': 5,
        'optimization_algorithm': 'ParticleSwarmAlgorithm',
        'inner_optimization_algorithm': 'ParticleSwarmAlgorithm'
    }

    return client.post(url=f"""/pipeline/run?data_id={data_id}""",
                json={'web_pipeline_optimizer':wpo, 'web_pipeline_optimizer_run':wpor})

def export_ppln(client: TestClient, export:str):
    return client.post(url=f"""/pipeline/export/text?data_id={export}""")

def export_text(client: TestClient, export:str):
    return client.post(url=f"""/pipeline/export/ppln?data_id={export}""")
