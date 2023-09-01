# python base image so we can run a python app
FROM python:3.9.15-buster
# Sets working directory to /usr/src/app
WORKDIR /usr/src/app
# UPDATE APT-GET
RUN apt-get update
# UPGRADE pip3
RUN pip3 install --upgrade pip
RUN pip3 install python-dotenv
# Copies all files from current directory into the working directory
COPY . .
# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "src"]
