# get the python docker image
FROM python:3.9

WORKDIR /app

COPY ./requirements.txt ./

# install requirements
RUN pip install --no-cache-dir -r requirements.txt

# add all the files and folders
COPY . .

# run the uvicorn server
CMD uvicorn main:app --host 0.0.0.0 --port 5000
