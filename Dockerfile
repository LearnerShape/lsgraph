FROM python:3.6

#
# Installing python packages and bringing in code
#

RUN mkdir -p /app
WORKDIR /app
COPY ./requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt
COPY ./ /app/app
WORKDIR /app/app