# submit_run.py
import os
import kfp
import sys

sys.path.append('../src')
from pipelines.pipeline_definitions.pipeline_definition import pipeline
from pipelines.pipeline_arg.pipeline_arg import arguments

KFP_ENDPOINT = "http://localhost:8080"

def submit_pipeline():
    client = kfp.Client(host=KFP_ENDPOINT)

    if os.environ.get("GITHUB_ACTIONS") == "true":
        ci_platform = "github-actions"
    elif os.environ.get("CI") == "true":
        ci_platform = "gitlab-ci"
    else:
        ci_platform = "local"

    # Branch name: GitLab uses CI_COMMIT_BRANCH, GitHub uses GITHUB_REF_NAME
    branch = (
        os.environ.get("CI_COMMIT_BRANCH")       # GitLab
        or os.environ.get("GITHUB_REF_NAME")      # GitHub
        or "unknown-branch"
    )

    # Define your experiment and run name
    experiment_name = "demo-experiment"
    run_name = f"demo-run-through-{ci_platform}-on-OSS-MLOps-platform-in-{branch}-environment"
    print(f"Experiment Name: {experiment_name}")
    print(f"Run Name: {run_name}")

    # Submit the pipeline run
    print("🚀 Submitting pipeline...")
    result = client.create_run_from_pipeline_func(
        pipeline_func=pipeline,
        arguments=arguments,
        run_name=run_name,
        experiment_name=experiment_name,
        mode=kfp.dsl.PipelineExecutionMode.V2_COMPATIBLE,
        enable_caching=False,
        namespace="kubeflow-user-example-com"
    )
    print(f"✅ Pipeline submitted successfully! Run ID: {result.run_id}")

if __name__ == "__main__":
    submit_pipeline()