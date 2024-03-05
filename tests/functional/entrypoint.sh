#!/bin/bash
python3 utils/wait_for_postgres.py && python3 utils/wait_for_redis.py

pytest