FROM python:3.6
WORKDIR /home/run

COPY ["./requirements.txt", \
      "./jupyter/apt.txt", \
      "./"]
RUN apt-get update && apt-get install -y $(grep -vE "^\s*#" apt.txt) && \
    rm -rf /var/lib/apt/lists/*
RUN pip install -r requirements.txt


COPY ./jupyter/set_jupyter_password.py /usr/local/bin/
COPY ./jupyter/startup.sh /usr/local/bin/
RUN mkdir -p /root/.jupyter/
RUN touch /root/.jupyter/jupyter_notebook_config.json

EXPOSE 8888
ENTRYPOINT startup.sh
