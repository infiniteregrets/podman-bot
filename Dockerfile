FROM python:3.9-slim-buster
WORKDIR /podbot
COPY ./ ./
RUN apt-get update -y \
    && apt-get install -y\
    chromium-driver 
RUN pip3 install pipenv && pipenv install
CMD ["pipenv", "run", "python3", "index.py"]
