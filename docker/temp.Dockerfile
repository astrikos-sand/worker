FROM gcr.io/kaggle-images/python:v153

RUN apt-get update

# Pillow dependencies
RUN apt-get install -y libgomp1

# MSSQL ODBC Driver
RUN apt-get install -y unixodbc unixodbc-dev
RUN apt-get install -y curl gnupg2 apt-transport-https
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list | tee /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update
RUN ACCEPT_EULA=Y apt-get install -y msodbcsql17

# Remove apt cache
RUN rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip

RUN pip3 install pycaret hdbscan mlflow umap bayesian-optimization 

RUN pip3 install pyodbc
