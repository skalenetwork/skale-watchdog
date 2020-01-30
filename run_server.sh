#!/usr/bin/env bash
export $(cat .env | xargs)
python server.py