import streamlit as st
from annotated_text import annotated_text
import os
from functions import *
import tempfile
import pathlib
import os
from PIL import Image
from machamp.predictor.predict import predict_with_paths
from convert_excel import make_excel,to_excel
import logging
import torch
import sys
import machamp
import pandas as pd


logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
                    level=logging.INFO, handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger(__name__)



def main():
    
    st.set_page_config(
        page_title="Odeuropa Smells Extraction",
        page_icon="",
        # layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            "Get Help": 'https://github.com',
            "Report a bug": "https://github.com",
            "About": "Odeuropa demonstrator for the smells extraction tools."})

    ### model to be used for every language
    langdict = {
        "English": "en.pt",
        "Italian": "it.pt",
        "French": "fr.pt",
        "German": "de.pt",
        "Dutch": "nl.pt",
        "Slovene": "sl.pt"
    }

    ### select where to load the models, could be gpu (e.g. "cuda:0") or cpu (e.g "cpu")
    langdevice = {
        "English": "cuda:0",
        "Italian": "cuda:0",
        "French": "cuda:0",
        "German": "cuda:0",
        "Dutch": "cuda:0",
        "Slovene": "cuda:0"
    }

    ### preload the models for the classifier
    for l in langdict:
        loadModel(langdict[l], langdevice[l])


    ### Header

    col1, empty,  mid,  col2 = st.columns([2,2,10,2])
    with col1:
        st.image('logo.png', use_column_width="always")
    with mid:
        st.title("Smells Extraction")
    with col2:
        st.image('fbk.png', use_column_width="always")

    ### main form

    form = st.form("main_form")


    ### upload documents and save them in a temp file
    fp = tempfile.TemporaryFile(mode="w+")
    uploadedFile = False
    uploaded_file = form.file_uploader("Upload a file")
    
    if uploaded_file is not None:
        fp.write(uploaded_file.getvalue().decode("utf-8"))
        fp.seek(0)
        uploadedFile = True

    ### or read the text from the box
    txt = form.text_area('Insert a text:')


    ### lanuguage selection. The names need to match the ones in langdict and langdevice
    language = form.selectbox(
        'Language',
        ['English', 'Italian', 'French', 'German', 'Dutch', 'Slovene'])

    
    outTxt = ""

    form.text("For this demo only the first 1000 words of the text will be processed")



    if form.form_submit_button("Extract the smells"):
        
        ### if no document is uploaded the text from the input box is saved in the temp file
        if not uploadedFile:
            fp.write(txt)
            fp.seek(0)

        
        ### convert the text into the format required by the classifier 
        ### only convert the first N tokens defined by "limit"
        convertedText = convertText(fp, limit=1000)
        
        ### Temp files needed by the classifier
        fInput = tempfile.NamedTemporaryFile(delete=False, mode="w")
        fInput.write(convertedText)
        fInput.close()

        fOutput = tempfile.NamedTemporaryFile(delete=False, mode="w")
        fOutput.close()

        input_path = fInput.name
        output_path = fOutput.name

        ### Run predictions
        model = loadModel(langdict[language], langdevice[language])
        logger.info('predicting on ' + input_path + ', saving on ' + output_path)
        predict_with_paths(model, input_path, output_path, None, 32, False, langdevice[language], "=", "|")

        os.remove(fInput.name)

        tuples = predictions_to_tuples(fOutput.name)
        with open(fOutput.name) as f:
            for line in f:
                outTxt += line

        ### save prediction on excel file for download
        df_out = make_excel(fOutput.name)

        os.remove(fOutput.name)
        
        ### convert predictions in the tuples needed for the annotated_text module
        ### and add them the colors to display
        ### you can change colors in functions.py -> add_colors
        tuples_fixed = []
        for t in tuples:
            if len(t) == 1:
                tuples_fixed.append(t[0])
            else:
                tuples_fixed.append(t)
            
        tuples_colors = add_colors(tuples_fixed)

        ### print the predictions
        annotated_text(tuples_colors)

    ### download predictions as excel file
    if outTxt:
        st.markdown("""---""")
        df_xlsx = to_excel(df_out)
        st.download_button(label='Download Output', data=df_xlsx, file_name= 'df_test.xlsx')


if __name__ == "__main__":
    main()

