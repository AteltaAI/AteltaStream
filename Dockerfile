FROM ubuntu

# Install Anaconda
RUN apt-get update && apt-get install -y wget
ENV CONDA_DIR /opt/conda
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && /bin/bash ~/miniconda.sh -b -p /opt/conda
ENV PATH=$CONDA_DIR/bin:$PATH

# Create and activate the conda environment
RUN conda create -n myenv python=3.8
RUN echo "source activate myenv" > ~/.bashrc
ENV PATH ${CONDA_DIR}/envs/myenv/bin:$PATH

# Install necessary packages
RUN conda install -c pytorch pytorch
# Set the workdir and copy the project files
RUN mkdir /AteltaStream
WORKDIR /AteltaStream
COPY . .

RUN pip3 install mediapipe streamlit opencv-python streamlit

# Allow the container to access the host's system camera and run the script
RUN apt-get install ffmpeg libsm6 libxext6  -y
RUN apt-get update && apt-get install libgl1 -y

EXPOSE 8900
ENV PYTHONPATH=.
ENTRYPOINT ["PYTHONPATH=.", "streamlit", "run"]
CMD ["app/app.py"]