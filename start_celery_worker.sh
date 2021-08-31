#!/bin/bash

celery -A celery_app.celery worker --concurrency=1 --loglevel=info
