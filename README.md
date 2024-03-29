# wp3-smell-extraction-demo

This repository contains a modified version of the classifier from https://github.com/Odeuropa/wp3-information-extraction-system-v2 that can be used through a web interface.

Before running the demo download all the model in https://zenodo.org/records/10598306 and move it in `models` folder.


## Run with Docker
__`IMPORTANT:`__ Before run `docker build` open `main_odeuropa.py` and set for each language if you want to use GPU or CPU.


```
docker build -t odeuropademo .
docker run -p 8509:8509 --gpus '"device=0"' odeuropademo
```
To change the port edit the Dockerfile.

## Run without docker
Create an environment as you prefer. E.g. with conda.

```
conda create --name predictiondemo python=3.8
conda activate predictiondemo
```

Install the requirements:
```
pip install -r requirements.txt
```

### Run the server
__`IMPORTANT:`__ Before running the server open `main_odeuropa.py` and set for each language if you want to use GPU or CPU.

Set the max size of the files allowed to be uploaded in the demo.
```
export STREAMLIT_SERVER_MAX_UPLOAD_SIZE=1
```

Run the interface on the dessired port. The models will be loaded when opening the link for the first time.
```
streamlit run main_odeuropa.py --server.port 8509
```

## Publication

If you use this resource, please cite:

`Menini, Stefano. Semantic Frame Extraction in Multilingual Olfactory Events. In Proceedings of LREC-Coling 2024`

## Funding acknowledgement

<img src="https://github.com/Odeuropa/.github/raw/main/profile/eu-logo.png" width="80" height="54" align="left" alt="EU logo" />

This work has been realised in the context of [Odeuropa](https://odeuropa.eu/), a research project that has received funding from the European Union’s Horizon 2020 research and innovation programme under grant agreement No. 101004469.

