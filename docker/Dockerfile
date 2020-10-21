FROM nvidia/cuda:10.2-cudnn8-devel-ubuntu18.04
RUN apt-get update

#REQUIREMENTS
RUN apt-get install -y gcc wget python3-pip python3 libgl1-mesa-glx git

#MESHROOM
RUN mkdir -p /opt && cd /opt && \
    wget https://db.3dscan.io/static/Meshroom-2019.2.0-linux.tar.gz \
    && tar zxf Meshroom-2019.2.0-linux.tar.gz && rm Meshroom-2019.2.0-linux.tar.gz

RUN chmod 755 /opt/Meshroom-2019.2.0/meshroom_*
RUN export LD_LIBRARY_PATH=/usr/local/cuda/lib64

#ROBOWELDAR REPO DOWNLOAD
ADD repo-key /
RUN \
  chmod 600 /repo-key && \
  echo "IdentityFile /repo-key" >> /etc/ssh/ssh_config && \
  echo "StrictHostKeyChecking no" >> /etc/ssh/ssh_config

WORKDIR /opt/
ENV GITHUB_SSH_REPO=git@github.com:ikh-innovation/roboweldar-3d-reconstruction.git
RUN git clone --recurse-submodules --single-branch --branch docker_branch ${GITHUB_SSH_REPO}

#SETUP
RUN yes | pip3 install -r roboweldar-3d-reconstruction/src/rest/roboweldar_networking/interfaces/requirements.txt
RUN yes | pip3 install -r roboweldar-3d-reconstruction/src/rest/requirements.txt

#PORTS
EXPOSE 3000
EXPOSE 3001

#EXECUTE
WORKDIR /opt/roboweldar-3d-reconstruction
ENV PYTHONPATH "${PYTHONPATH}:$(pwd)"

ENTRYPOINT ["python3", "src/rest/client.py"]