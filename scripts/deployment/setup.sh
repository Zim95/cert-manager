#!/bin/bash

# Check if enough arguments are provided
if [ $# -lt 2 ]; then
    echo "Usage: $0 <namespace> <repo-name>"
    exit 1
fi

YAML=./infra/deployment/deployment.yaml
NAMESPACE=$1
REPO_NAME=$2    

export NAMESPACE=$NAMESPACE
export REPO_NAME=$REPO_NAME
envsubst < $YAML | kubectl apply -f -
