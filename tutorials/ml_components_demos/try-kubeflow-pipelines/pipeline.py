import kfp

train_op = kfp.components.load_component_from_file('component.yaml')

@kfp.dsl.pipeline(name='Example Kubeflow pipeline', description='Pipeline to test an example component')
def pipeline():
    train_task = train_op()

def compile():
    kfp.compiler.Compiler().compile(
        pipeline_func=pipeline,
        package_path='pipeline.yaml'
    )

if __name__ == '__main__':
    compile()
