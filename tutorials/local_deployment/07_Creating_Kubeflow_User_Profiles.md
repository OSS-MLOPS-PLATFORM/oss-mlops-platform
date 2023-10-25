# Creating new Kubeflow user profiles

This guide shows how to:

- create new Kubeflow user profiles so that they can authenticate and use Kubeflow.
- manage their access to the other services/tools in the cluster

## Creating a new profile

```yaml
# profile.yaml
apiVersion: kubeflow.org/v1beta1
kind: Profile
metadata:
  name: profileName   # replace with the name of profile you want, this will be user's namespace name
spec:
  owner:
    kind: User
    name: userid@email.com   # replace with the email of the user

  resourceQuotaSpec:    # resource quota can be set optionally
   hard:
     cpu: "2"
     memory: 2Gi
     requests.nvidia.com/gpu: "1"
     persistentvolumeclaims: "1"
     requests.storage: "5Gi"
```

Run the following command to create the corresponding profile resource:

```sh
kubectl apply -f profile.yaml
```

The above command creates a profile named profileName. The profile owner is userid@email.com and has view and modify access to that profile. The following resources are created as part of the profile creation:

- A Kubernetes namespace that shares the same name with the corresponding profile.
- Kubernetes RBAC (Role-based access control) role binding for the namespace: Admin. This makes the profile owner the namespace administrator, thus giving them access to the namespace using kubectl (via the Kubernetes API).
- Istio namespace-scoped AuthorizationPolicy: user-userid-email-com-clusterrole-edit. This allows the user to access data belonging to the namespace the AuthorizationPolicy was created in
- Namespace-scoped service-accounts default-editor and default-viewer to be used by user-created pods in the namespace.
- Namespace scoped resource quota limits will be placed.

For more details refer to the [official documentation](https://www.kubeflow.org/docs/components/multi-tenancy/getting-started/).

# Extra permissions

Kubeflow automatically adds the necessary permissions to the user for accessing the
Kubeflow tools, however, permissions to anything external to Kubeflow, such as MLflow must be added.

Here, we attach a new role to the user to allow him to access the MLflow server:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: mlflow
  name: users-mlflow
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "watch", "list"]
- apiGroups: [""]
  resources: ["services"]
  verbs: ["get", "watch", "list"]
- apiGroups: [""]
  resources: ["pods/portforward"]
  verbs: ["get", "list", "create"]

---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: user-mlflow-binding  
subjects:
- apiGroup: rbac.authorization.k8s.io
  kind: User
  name: "<Email of user, e.g. user@example.com>"
roleRef:
  kind: Role
  name: users-mlflow
  apiGroup: rbac.authorization.k8s.io
```

## Dex

On-premises installations of Kubeflow like this, without any external identity providers,
Dex is used for authentication. Dex is a flexible OpenID Connect (OIDC) provider.

> The Kubeflow installation on Google Cloud uses GKE and IAP instead.

![](/resources/img/kubeflow-auth.png)

To allow the users to authenticate to Dex, we need to add them as a new static user.

```shell
export EMAIL=user@example.com
export USERNAME=user
export HASH=$(python3 -c 'from passlib.hash import bcrypt; import getpass; print(bcrypt.using(rounds=12, ident="2y").hash(getpass.getpass()))')
export USERID=$(cat /proc/sys/kernel/random/uuid)

cat <<EOF
- email: ${EMAIL?}
  hash: ${HASH?}
  username: ${USERNAME?}
  userID: ${USERID?}
EOF
```
Edit [`deployment/kubeflow/manifests/common/dex/base/config-map.yaml`](/deployment/kubeflow/manifests/common/dex/base/config-map.yaml)
and add the previously generated entry to the staticPasswords field.

```yaml
staticPasswords:
...
- email: user@example.com
  hash: $2y$12$LXwF5gk43JunEM02OKWevuyyo0GPwZaD4WobTv0yahDZzN8IAFykO
  username: user
  userID: d28802d7-97a4-4e49-b67d-80c56fcaf530
```

For more details refer to the [official documentation](https://docs.arrikto.com/ops/dex.html#what-you-ll-need). 

Re-apply the configmap with:

```shell
kubectl apply -f config-map.yaml -n auth
```

After editing the configmap you also need to run the following command so that the new credentials are picked up. 

```shell
kubectl rollout restart deployment dex -n auth
```

### TODO: helper script