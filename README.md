# wp3-smell-extraction-demo

This repository contains a modified version of the classifier from https://github.com/Odeuropa/wp3-information-extraction-system-v2 that can bt run through a web interface.

Before running the demo download all the model in https://drive.google.com/drive/u/1/folders/1HRfiE3atNbXHIfj8mjXNiPJPZCxSmHky and move it in `models` folder.



Create an environment as you prefer. E.g. with conda.

```
conda create --name predictiondemo python=3.8
conda activate predictiondemo
```

Install the requirements:
```
pip install -r requirements.txt
```

Set the max size of the files allowed to be uploaded in the demo.
```
export STREAMLIT_SERVER_MAX_UPLOAD_SIZE=1
```

Run the interface on the dessired port. The models will be loaded when opening the link for the first time.
```
streamlit run main_odeuropa.py --server.port 8509
```



## Funding acknowledgement

<img src="https://github.com/Odeuropa/.github/raw/main/profile/eu-logo.png" width="80" height="54" align="left" alt="EU logo" />

This work has been realised in the context of [Odeuropa](https://odeuropa.eu/), a research project that has received funding from the European Union’s Horizon 2020 research and innovation programme under grant agreement No. 101004469.

