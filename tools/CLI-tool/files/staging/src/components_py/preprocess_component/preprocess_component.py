# preprocess_component.py
from kfp.v2.dsl import Input, Output, Dataset, Artifact, component

@component(
    base_image="python:3.10",
    packages_to_install=["numpy~=1.26.4", "pandas~=1.4.2", "scikit-learn~=1.0.2"],
    output_component_file='src/components_yaml/preprocess_component.yaml',
)
def preprocess(
    data: Input[Dataset],
    scaler_out: Output[Artifact],
    train_set: Output[Dataset],
    test_set: Output[Dataset],
    target: str = "quality",
):
    """
    Preprocess component.
    """
    import pandas as pd
    import pickle
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler

    data = pd.read_csv(data.path)

    # Split the data into training and test sets. (0.75, 0.25) split.
    train, test = train_test_split(data)

    scaler = StandardScaler()

    train[train.drop(target, axis=1).columns] = scaler.fit_transform(train.drop(target, axis=1))
    test[test.drop(target, axis=1).columns] = scaler.transform(test.drop(target, axis=1))

    with open(scaler_out.path, 'wb') as fp:
        pickle.dump(scaler, fp, pickle.HIGHEST_PROTOCOL)

    train.to_csv(train_set.path, index=None)
    test.to_csv(test_set.path, index=None)