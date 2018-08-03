# Build image with command:
#   ofer-main/ds# docker build -t keywee/ofer-ds .
# Run jupyter lab server:
#   ofer-main/ds# docker run --name=ofer_ds_container --rm -ti -p 8900:8900 -v "$PWD/../..":/home/jovyan/work keywee/ofer-ds /bin/bash -c  "jupyter lab --ip='*' --port=8900 --no-browser --allow-root"
# Run docker for further installations:
#   ofer-main/ds# docker run --name=ofer_ds_container --rm -ti -e GRANT_SUDO=yes --user root -p 8900:8900 -v "$PWD/../..":/home/jovyan/work keywee/ofer-ds /bin/bash

# latest at 2018-08-03
FROM jupyter/scipy-notebook:45e010d9e849

RUN jupyter lab build

# Octave! In Jupyter notebook!
USER root
RUN export GRANT_SUDO=yes
RUN apt-get update && apt-get install -yq octave && apt-get clean
USER jovyan
RUN export GRANT_SUDO=FALSE

RUN pip install octave_kernel

