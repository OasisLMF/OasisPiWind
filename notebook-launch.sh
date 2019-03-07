#!/bin/bash                                                                                                                                                                                    

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
docker build -f docker/Dockerfile.jupyter -t piwind-jupyter .
docker run  -v "$SCRIPT_DIR":/home/run -e JUPYTER_PASS='<ADD-PASSWORD-HERE>' -p 8888:8888 -d piwind-jupyter
