"""
pip install "ray[data,train,tune,serve]"==2.9.0
pip install torch torchvision
"""
import os
import tempfile

import torch
from torch.nn import CrossEntropyLoss
from torch.optim import Adam
from torch.utils.data import DataLoader
from torchvision.models import resnet18
from torchvision.datasets import FashionMNIST
from torchvision.transforms import ToTensor, Normalize, Compose

import ray
from ray.train.torch import TorchTrainer
import ray.train.torch

print(ray.__version__)

"""
Run a port forwarding to the Ray head service:

$ kubectl port-forward svc/raycluster-kuberay-head-svc 10001:10001 -n default
"""

runtime_env = {
    "pip": ["torch", "torchvision"],
}

ray.init(address="ray://localhost:10001", runtime_env=runtime_env)
print(ray.cluster_resources())


def train_func(config):
    # Model, Loss, Optimizer
    model = resnet18(num_classes=10)
    model.conv1 = torch.nn.Conv2d(
        1, 64, kernel_size=(7, 7), stride=(2, 2), padding=(3, 3), bias=False
    )
    # model.to("cuda")  # This is done by `prepare_model`
    # [1] Prepare model.
    model = ray.train.torch.prepare_model(model)
    criterion = CrossEntropyLoss()
    optimizer = Adam(model.parameters(), lr=0.001)

    # Data
    transform = Compose([ToTensor(), Normalize((0.5,), (0.5,))])
    data_dir = os.path.join(tempfile.gettempdir(), "data")
    train_data = FashionMNIST(root=data_dir, train=True, download=True, transform=transform)
    train_loader = DataLoader(train_data, batch_size=64, shuffle=True)
    # [2] Prepare dataloader.
    train_loader = ray.train.torch.prepare_data_loader(train_loader)

    # Training
    n_epochs = 4
    for epoch in range(n_epochs):
        for images, labels in train_loader:
            # This is done by `prepare_data_loader`!
            # images, labels = images.to("cuda"), labels.to("cuda")
            outputs = model(images)
            loss = criterion(outputs, labels)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        # [3] Report metrics and checkpoint.
        metrics = {"loss": loss.item(), "epoch": epoch}
        with tempfile.TemporaryDirectory() as temp_checkpoint_dir:
            torch.save(
                model.module.state_dict(),
                os.path.join(temp_checkpoint_dir, "model.pt")
            )
            ray.train.report(
                metrics,
                checkpoint=ray.train.Checkpoint.from_directory(temp_checkpoint_dir),
            )
        if ray.train.get_context().get_world_rank() == 0:
            print(metrics)


# Configure scaling and resource requirements.
scaling_config = ray.train.ScalingConfig(num_workers=2, use_gpu=False)

run_config = ray.train.RunConfig(
    storage_path="/home/ray/nfs",
    name="nfs",
)
# --------------------

# Distributed training job.
trainer = ray.train.torch.TorchTrainer(
    train_func,
    scaling_config=scaling_config,
    run_config=run_config,
)
# Launch training.
result = trainer.fit()
