#!/bin/bash

source ../env/bin/activate
export STREAMLIT_SERVER_MAX_UPLOAD_SIZE=1
streamlit run main.py --server.port 8507
