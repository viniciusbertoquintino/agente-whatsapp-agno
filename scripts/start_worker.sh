#!/bin/sh

dotenv run celery -A workers.tasks worker --loglevel=INFO --concurrency=1