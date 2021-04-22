FROM nvidia/cuda:10.2-cudnn8-devel-ubuntu18.04
RUN apt-get update

#REQUIREMENTS
RUN apt-get install -y gcc wget python3-pip python3 libgl1-mesa-glx git

WORKDIR /opt/roboweldar-3d-reconstruction
COPY . .

#MESHROOM
ENV RBW_PATH=/opt/roboweldar-3d-reconstruction
RUN mkdir -p ${RBW_PATH}/deps/ && cd ${RBW_PATH}/deps/ && \
    wget https://db.3dscan.io/static/Meshroom-2019.2.0-linux.tar.gz \
    && tar zxf Meshroom-2019.2.0-linux.tar.gz && rm Meshroom-2019.2.0-linux.tar.gz

RUN chmod 755 ${RBW_PATH}/deps/Meshroom-2019.2.0/meshroom_*

RUN export LD_LIBRARY_PATH=/usr/local/cuda/lib64

#SETUP
RUN yes | pip3 install -r src/rest/roboweldar_networking/interfaces/requirements.txt
RUN yes | pip3 install -r requirements.txt


#PORTS
EXPOSE 3000
EXPOSE 3001

#EXECUTE
ENV PYTHONPATH "${PYTHONPATH}:$(pwd)"

ENTRYPOINT ["python3", "src/rest/client.py"]
