#!/bin/bash

# usage: $./create_user.sh <username> <group_name>
# e.g. $./create_user.sh john users

set -eoau pipefail


function print_help {
  echo ""
  echo "options:"
  echo "  -h                    Print this help message and exit"
  echo "  -u=USER_NAME                                          "
  echo "  -g=GROUP_NAME                                         "
  echo "  -o=OUTPUT_DIR                                         "

}

while getopts hu:g:o: flag
do
    case "${flag}" in
        h)
          print_help
          exit 0
        ;;
        u) USER_NAME=${OPTARG};;
        g) GROUP_NAME=${OPTARG};;
        o) OUTDIR=${OPTARG};;
        *)
          echo 'Error in command line parsing' >&2
          print_help
          exit 1
    esac
done

if [ -u "$USER_NAME" ]; then
        echo 'Missing -u / USER_NAME' >&2
        exit 1
fi
if [ -g "$GROUP_NAME" ]; then
        echo 'Missing -g / GROUP_NAME' >&2
        exit 1
fi
if [ -o "$OUTDIR" ]; then
        echo 'Missing -o / OUTDIR' >&2
        exit 1
fi

echo "USER_NAME: $USER_NAME";
echo "GROUP_NAME: $GROUP_NAME";
echo "OUTDIR: $OUTDIR";

TEMPLATES_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# create CSR config for the user
cat "$TEMPLATES_DIR"/csr.cnf.template | envsubst > "$OUTDIR"/"$USER_NAME"-csr.cnf

# create user key
openssl genrsa -out "$OUTDIR"/"$USER_NAME".key 4096

# create CSR
openssl req -config "$OUTDIR"/"$USER_NAME"-csr.cnf -new -key "$OUTDIR"/"$USER_NAME".key -nodes -out "$OUTDIR"/"$USER_NAME".csr

# encode the .csr file in base64
BASE64_CSR=$(cat "$OUTDIR"/"$USER_NAME".csr | base64 | tr -d '\n')

# create the CertificateSigninRequest
cat "$TEMPLATES_DIR"/csr.yaml.template | envsubst > "$OUTDIR"/csr.yaml

kubectl apply -f "$OUTDIR"/csr.yaml

# approve the certificate
sleep 2
kubectl certificate approve "$USER_NAME"-csr

### generate kubeconfig ###

# Cluster Name (from the current context)
export CLUSTER_NAME=$(kubectl config view --minify -o jsonpath={.current-context})
# Client certificate
export CLIENT_CERTIFICATE_DATA=$(kubectl get csr "$USER_NAME"-csr -o jsonpath='{.status.certificate}')
# Cluster Certificate Authority
export CLUSTER_CA=$(kubectl config view --raw -o json | jq -r '.clusters[] | select(.name == "'$(kubectl config current-context)'") | .cluster."certificate-authority-data"')
# API Server endpoint
export CLUSTER_ENDPOINT=$(kubectl config view --raw -o json | jq -r '.clusters[] | select(.name == "'$(kubectl config current-context)'") | .cluster."server"')

echo "user: $USER_NAME, cluster name: $CLUSTER_NAME, client certificate (length): ${#CLIENT_CERTIFICATE_DATA}, Cluster Certificate Authority (length): ${#CLUSTER_CA}, API Server endpoint: $CLUSTER_ENDPOINT"

cat "$TEMPLATES_DIR"/kubeconfig.template | envsubst > "$OUTDIR"/"$USER_NAME"-kubeconfig

# add user private key
kubectl config set-credentials $USER_NAME --client-key="$OUTDIR"/"$USER_NAME".key --embed-certs=true --kubeconfig="$OUTDIR"/"$USER_NAME"-kubeconfig

# confirm user access
kubectl version --kubeconfig="$OUTDIR"/"$USER_NAME"-kubeconfig