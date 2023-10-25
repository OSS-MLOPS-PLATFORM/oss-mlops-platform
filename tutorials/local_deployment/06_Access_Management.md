# Access Management

Low level/Cloud agnostic method to give access to your cluster with A client certificate.

> This is only needed for local/on-premise clusters. All major cloud provider already have
> their own recommended access control, which should be much easier to use. 

# 1. Creation of a Private Key and a Certificate Signing Request (CSR)

Let's say we have a new user called "John". First, we need to generate a private rsa
key and a CSR for the user. The private key can easily be created with this command:

```bash
openssl genrsa -out john.key 4096
```

The CSR is a bit more complicated. We need to make sure that:

- The name of the user is used in the Common Name (CN) field: this will be used to identify him against the API Server.
- The group name is used in the Organisation (O) field: this will be used to identify the group against the API Server.

We will use the following configuration file to generate the CSR:

```ini
# /csr.cnf

[ req ]
default_bits = 2048
prompt = no
default_md = sha256
distinguished_name = dn

[ dn ]
CN = john
O = users

[ v3_ext ]
authorityKeyIdentifier=keyid,issuer:always
basicConstraints=CA:FALSE
keyUsage=keyEncipherment,dataEncipherment
extendedKeyUsage=clientAuth
```

Using the above configuration file (saved in `csr.cnf`), the CSR can be created using the following command:

```bash
openssl req -config ./csr.cnf -new -key ./john.key -nodes -out john.csr
```

Ideally, it would be John's responsibility to do these steps. Then, once the .csr file
is created, "John" would send it to the platform administrator/s so he can sign it using the cluster
Certificate Authority. That’s what we’ll do in the next step.

## 2. Signature of the CSR

The signature of the `.csr` file will result in the creation of a certificate. This one
will be used to authenticate each request the user (John) will send to the API Server.

We will start by creating a Kubernetes CertificateSigninRequest resource.

We will use the following specification and save it in `csr.yaml`.

```yaml
apiVersion: certificates.k8s.io/v1
kind: CertificateSigningRequest
metadata:
  name: john-csr
spec:
  signerName: kubernetes.io/kube-apiserver-client

  groups:
  - system:authenticated
  request: ${BASE64_CSR}
  usages:
  - client auth
  - digital signature
  - key encipherment
```

As we can see, the value of the request key is the content of the BASE64_CSR environment variable.
The first step is to get the base64 encoding of the `.csr` file generated for John and
then use the `envsubst` binary to substitute the value of this variable before creating the resource.

```bash
# Encoding the .csr file in base64
export BASE64_CSR=$(cat ./john.csr | base64 | tr -d '\n')
# Substitution of the BASE64_CSR env variable and creation of the CertificateSigninRequest resource
cat csr.yaml | envsubst | kubectl apply -f -
```

```bash
# Checking the status of the newly created CSR
$ kubectl get csr

NAME       AGE   SIGNERNAME                            REQUESTOR          REQUESTEDDURATION   CONDITION
john-csr   5s    kubernetes.io/kube-apiserver-client   kubernetes-admin   <none>              Pending
```

We can then approve this CSR with this command:

```bash
kubectl certificate approve john-csr
```

Checking the status of the CSR once again, we can see it’s now approved and issued.

```bash
$ kubectl get csr

NAME            AGE     SIGNERNAME                            REQUESTOR            REQUESTEDDURATION   CONDITION
john-csr    41s     kubernetes.io/kube-apiserver-client   kubernetes-admin     <none>              Approved,Issued
```

You can extract the certificate from the CSR resource and save it in a file to check what’s inside. E.g.

```bash
# download and decode john's certificate
kubectl get csr john-csr -o jsonpath='{.status.certificate}' | base64 --decode > ./downloaded-john.crt
# show the certificate
openssl x509 -in ./downloaded-john.crt -noout -text
```

# Building a Kube Config for the user

We now have to send Dave the information he needs to configure his local kubectl client to communicate with our cluster.

We’ll first create a `kubeconfig.template` file, with the following content, that we’ll use as a template.

```yaml
apiVersion: v1
kind: Config
clusters:
- cluster:
    certificate-authority-data: ${CLUSTER_CA}
    server: ${CLUSTER_ENDPOINT}
  name: ${CLUSTER_NAME}
users:
- name: ${USER}
  user:
    client-certificate-data: ${CLIENT_CERTIFICATE_DATA}
contexts:
- context:
    cluster: ${CLUSTER_NAME}
    user: dave
  name: ${USER}-${CLUSTER_NAME}
current-context: ${USER}-${CLUSTER_NAME}
```

To build a base kube config from this template, we first need to set all the needed environment variables:

```bash
# User identifier
export USER="john"
# Cluster Name (get it from the current context)
export CLUSTER_NAME=$(kubectl config view --minify -o jsonpath={.current-context})
# Client certificate
export CLIENT_CERTIFICATE_DATA=$(kubectl get csr john-csr -o jsonpath='{.status.certificate}')
# Cluster Certificate Authority
export CLUSTER_CA=$(kubectl config view --raw -o json | jq -r '.clusters[] | select(.name == "'$(kubectl config current-context)'") | .cluster."certificate-authority-data"')
# API Server endpoint
export CLUSTER_ENDPOINT=$(kubectl config view --raw -o json | jq -r '.clusters[] | select(.name == "'$(kubectl config current-context)'") | .cluster."server"')

echo "user: $USER, cluster name: $CLUSTER_NAME, client certificate (length): ${#CLIENT_CERTIFICATE_DATA}, Cluster Certificate Authority (length): ${#CLUSTER_CA}, API Server endpoint: $CLUSTER_ENDPOINT"
```

Then, we can substitute them using the convenient `envsubst` utility:

```bash
cat ./kubeconfig.template | envsubst > ./john-kubeconfig
```

We can now send this kubeconfig file to "John" who will just need to add his private key inside of it and he will be fine to communicate with the cluster.

> **NOTE:**: For the users to be able to access the cluster from other computer in the local network, make sure that the IP of `CLUSTER_ENDPOINT` is accessible on the local network. If the IP is `127.0.0.1` it won't be visible to other computer.

# Use of the Context

In order to use the kubeconfig, John can set the `KUBECONFIG` environment variable with the path towards the file.

```bash
export KUBECONFIG=$PWD/john-kubeconfig
```

**Note:** There are different ways to use a Kubernetes configuration: setting the `KUBECONFIG` environment variable, adding a new entry in the default `$HOME/.kube/config` file, or using the `--kubeconfig` flag on each kubectl command.

To add his private key, John.key generated at the beginning of the process, "John" can use this command:

```bash
$ kubectl config set-credentials john --client-key=$PWD/john.key --embed-certs=true
```

The `--embed-certs` flag is needed to generate a standalone kubeconfig, that will work as-is on another host.

It will create the key client-key-data within the user entry of the kubeconfig file and set the base64 encoding of `john.key` as the value.

If everything is fine, John should be able to check the version of the server (and the client) with the following command:

```bash
$ kubectl version

Client Version: version.Info{Major:"1", Minor:"25", GitVersion:"v1.25.2", GitCommit:"5835544ca568b757a8ecae5c153f317e5736700e", GitTreeState:"clean", BuildDate:"2022-09-21T14:33:49Z", GoVersion:"go1.19.1", Compiler:"gc", Platform:"linux/amd64"}
Kustomize Version: v4.5.7
Server Version: version.Info{Major:"1", Minor:"24", GitVersion:"v1.24.0", GitCommit:"4ce5a8954017644c5420bae81d72b09b735c21f0", GitTreeState:"clean", BuildDate:"2022-05-25T22:55:08Z", GoVersion:"go1.18.1", Compiler:"gc", Platform:"linux/amd64"}
```

## Helper script

To make it easier for the admins, you can use the
[create_user.sh](/resources/local-setup/access_management/create_user/create_user.sh) script to add a new user
and create the user's `kubeconfig` in one command.
