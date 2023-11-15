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
    # langdevice = {
    #     "English": "cpu",
    #     "Italian": "cpu",
    #     "French": "cpu",
    #     "German": "cpu",
    #     "Dutch": "cpu",
    #     "Slovene": "cpu"
    # }

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
    # uploaded_file = form.file_uploader("Upload a txt file")
    
    # if uploaded_file is not None:
    #     fp.write(uploaded_file.getvalue().decode("utf-8"))
    #     fp.seek(0)
    #     uploadedFile = True

    txt = form.text_area('Insert a text:', height=300)

    ### list of examples
    example = form.selectbox(
    'Or... you might want to try these examples',
        ['', 
        '[ENGLISH] It\'s 1787, you are newly arrived in London, and you are walking the short distance from the Saracen\'s Head Inn to the nearby Newgate prison. As you pass the Old Bailey courthouse you catch a terrible smell in the air. Uncertain of its origins, you ask a lawyer as they hurry past on their way to a trial. They tell you that the smell arose from the burning of a woman who had been found guilty of coining farthings. The public burning of women in England only ended in 1790, Catherine Hayes being the last such individual to be thus punished. Up until 1789 the scent of burnt flesh also appeared in the courtroom itself, where some malefactors might be branded with a hot iron - "T" for theft, "F" for felon, or "M" for murder. The smell of burning was a warning to others. But smell could also feature as part of the humilitation of legal or, in some cases, extra-judicial punishment.',
        '[DUTCH] Evenwel was het eene goede zaak; er werd nu een verbod uitgevaardigd, om elders in de stad visch te verkoopen en de walgelijke overblijfsels van den visch, die vroeger hier en daar werden nedergeworpen, verpesten niet langer de lucht door onaangename reuk; terwijl nu tevens een beter toezigt op de hoedanigheid van den aangeboden visch kon worden uitgeoefend'
        ]
    )

    


    ### lanuguage selection. The names need to match the ones in langdict and langdevice
    language = form.selectbox(
        'Select the language of the text:',
        ['','English', 'Italian', 'French', 'German', 'Dutch', 'Slovene'])

    
    outTxt = ""

    form.text("For this demo only the first 1000 words of the text will be processed")



    if form.form_submit_button("Extract the smells"):
        
        ### if no document is uploaded the text from the input box or the example is saved in the temp file

        if not uploadedFile:
            if len(txt) > 0:
                fp.write(txt)
                fp.seek(0)
            elif len(example) > 0:
                fp.write(example)
                fp.seek(0)
        
        if len(language) == 0:
            st.warning('Please select a language', icon="⚠️")
            exit()

        if not uploadedFile and len(txt) == 0 and len(example) == 0:
            st.warning('Please enter a text', icon="⚠️")
            exit()
        
 
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

