# Ray

![ray-logo.png](../../resources/img/ray-logo.png)

## TOC
  - [What is Ray?](#what-is-ray)
  - [Tutorials](#tutorials)
  - [Notebooks](#notebooks)

## What is Ray?

[Ray](https://docs.ray.io/en/latest/index.html) is an open-source framework designed to scale and distribute Python and AI applications easily. Developed at the UC Berkeley RISELab, it provides a simple, universal API to build applications that can run across a cluster of machines. Key features and aspects of Ray include:

- Parallel and Distributed Computing: Ray simplifies the process of writing and running code that executes in parallel across multiple cores and machines. It automatically handles the distribution of data and scheduling of tasks.

- Scalability: Designed for high-performance computing, Ray can scale from a single machine to large clusters with minimal changes to the code. It's efficient for both fine-grained tasks (like functions) and large-scale applications.

- Flexible: Ray is flexible and can be used for a wide range of applications, from machine learning and AI to general-purpose Python scripting. It supports integration with popular libraries like TensorFlow, PyTorch, and scikit-learn.

- Ecosystem: Ray comes with a rich ecosystem of libraries and tools specifically designed for machine learning and AI tasks. This includes libraries for hyperparameter tuning (Ray Tune), reinforcement learning (RLlib), and distributed training (Ray SGD).

- Fault Tolerance: Ray provides fault tolerance through automatic restarting of failed tasks and nodes, making it robust for long-running and mission-critical applications.

- Easy to Use: Despite its powerful capabilities, Ray is designed to be easy to use, with a Pythonic API that feels natural for Python developers. You can parallelize existing code with minimal changes.

In summary, Ray is a powerful framework for building complex, high-performance, distributed applications and workflows, particularly in the domain of AI and machine learning, but also more broadly for any Python-based parallel computing tasks.

## Tutorials

- [Ray Setup](./01_Ray_setup.md)
- [Ray Usage](./02_Ray_usage.md)

## Notebooks

- [Ray basic 1](./notebooks/ray_basic_1.ipynb)
- [Ray basic 2](./notebooks/ray_basic_2.ipynb)
- [Ray-Kubeflow](./notebooks/ray_kubeflow.ipynb)
- [Ray Train](ray_train/README.md)