FROM python:3.6

#
# Installing python packages and bringing in code
#

RUN mkdir -p /app
WORKDIR /app
COPY ./requirements.txt /app
COPY ./requirements-models.txt /app
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements-models.txt
COPY ./ /app/app
WORKDIR /app/app
RUN python compose/worker/prime-cache.py