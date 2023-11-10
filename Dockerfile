FROM nvcr.io/nvidia/pytorch:20.10-py3

FROM python:3.8

RUN pip install --upgrade pip

COPY requirements.txt /code/

RUN pip install -r /code/requirements.txt

COPY ./ /code/

ENV STREAMLIT_SERVER_MAX_UPLOAD_SIZE=1

CMD ["streamlit", "run", "/code/main_odeuropa.py", "--server.port", "8509","--server.address", "0.0.0.0"]

WORKDIR /code