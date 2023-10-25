# Helper script to create new users

This is a helper script for adding new users to the cluster and giving them access.

It was created following the step indicated in the
[6_Access_management.md](/tutorials/local_deployment/06_Access_Management.md) tutorial.

## Usage

```bash
# e.g. ./create_user.sh john users
./create_user.sh <user_name> <group_name>
```

It will create a kubeconfig file named `<username>-kubeconfig`. This file can be sent to the user, so that he can use it to access the cluster.