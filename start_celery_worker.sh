#!/bin/bash

celery -A celery_app.celery worker --loglevel=info
