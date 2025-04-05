#!/bin/bash

# Check if enough arguments are provided
if [ $# -lt 1 ]; then
    echo "Usage: $0 <namespace>"
    exit 1
fi

YAML=./infra/deployment/deployment.yaml
NAMESPACE=$1

export NAMESPACE=$NAMESPACE
envsubst < $YAML | kubectl apply -f -
