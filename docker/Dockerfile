FROM nvidia/cuda:10.2-cudnn8-devel-ubuntu18.04

RUN apt-get update

RUN apt-get install -y gcc wget python3-pip python3 libgssapi-krb5-2 git

RUN mkdir -p /opt && cd /opt && \
    wget https://db.3dscan.io/static/Meshroom-2019.2.0-linux.tar.gz \
    && tar zxf Meshroom-2019.2.0-linux.tar.gz && rm Meshroom-2019.2.0-linux.tar.gz

RUN chmod 755 /opt/Meshroom-2019.2.0/meshroom_*

#COPY ./uploads /opt/Meshroom-2019.2.0

RUN export LD_LIBRARY_PATH=/usr/local/cuda/lib64


#add shh key for private repo
#RUN mkdir -p ~/.ssh
ADD repo-key /
RUN \
  chmod 600 /repo-key && \
  echo "IdentityFile /repo-key" >> /etc/ssh/ssh_config && \
  echo "StrictHostKeyChecking no" >> /etc/ssh/ssh_config

WORKDIR /opt/
ENV GITHUB_SSH_REPO=git@github.com:ikh-innovation/roboweldar-3d-reconstruction.git
RUN git clone --recurse-submodules --single-branch --branch docker_branch ${GITHUB_SSH_REPO}
#RUN git clone --recurse-submodules ${GITHUB_SSH_REPO}
#https://github.com/singularityhub/registry/wiki/Github-Machine-User

#COPY roboweldar_networking ./roboweldar-3d-reconstruction/src/rest/roboweldar_networking




#setup
#RUN yes | pip3 install -r roboweldar-3d-reconstruction/src/requirements.txt

RUN yes | pip3 install -r roboweldar-3d-reconstruction/src/rest/roboweldar_networking/interfaces/requirements.txt
RUN yes | pip3 install -r roboweldar-3d-reconstruction/src/rest/requirements.txt

EXPOSE 3000
EXPOSE 3001

WORKDIR /opt/roboweldar-3d-reconstruction
RUN export PYTHONPATH=$PYTHONPATH:$(pwd);

ENTRYPOINT ["python3", "src/rest/client.py"]
#CMD [" python src/rest/client.py --host localhost"]
