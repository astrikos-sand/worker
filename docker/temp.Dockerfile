FROM gcr.io/kaggle-images/python:v153

RUN apt-get update && \
    apt-get install -y libgomp1 && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip

RUN pip3 install pycaret hdbscan mlflow umap bayesian-optimization 
