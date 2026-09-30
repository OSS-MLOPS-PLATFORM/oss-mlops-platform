# pull_data_component.py
from kfp.v2.dsl import component, Output, Dataset

@component(
    base_image="python:3.10",
    packages_to_install=["numpy~=1.26.4", "pandas~=1.4.2"],
    output_component_file='src/components_yaml/pull_data_component.yaml',
)
def pull_data(url: str, data: Output[Dataset]):
    """
    Pull data component.
    """
    import pandas as pd

    df = pd.read_csv(url, sep=";")
    df.to_csv(data.path, index=None)