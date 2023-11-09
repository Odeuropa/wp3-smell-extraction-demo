import sys
import os
import pandas as pd
import csv
from pathlib import Path
from io import BytesIO
from pyxlsb import open_workbook as open_xlsb
import xlsxwriter

spamList = []
tokenID =1
textIndex = 3
smell_word_tag = "Smell_Word"
frameElements = "Smell_Source,Quality,Odour_Carrier,Evoked_Odorant,Location,Perceiver,Time,Circumstances,Effect".split(",")

def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    format1 = workbook.add_format({'num_format': '0.00'}) 
    worksheet.set_column('A:A', None, format1)  
    writer.close()
    processed_data = output.getvalue()
    return processed_data


def pocess_annotations(myAnnotations:list):
	annotationsDict = dict()
	outputDict = dict()

	s = [a for a in myAnnotations if smell_word_tag in " ".join(a)]

	# save all annotations in annotationsDict
	if len(s) == 0:
		return(None)
	annotationsDict[smell_word_tag] = s
	
	for f in frameElements:
		fe = [a for a in myAnnotations if f in " ".join(a)]
		annotationsDict[f] = fe

	#parse the annotations in annotationsDict merging tokens in the same span and puth them in outputDict
	
	# smell words:

	outputDict[smell_word_tag] = []
	firstID = int(annotationsDict[smell_word_tag][0][tokenID].split("-")[1])-1

	span = []
	for sw in annotationsDict[smell_word_tag]:

		myID = sw[tokenID].split("-")[1]
		myToken = sw[textIndex]

		if int(myID) == int(firstID)+1:
			span.append(myToken)
			firstID = myID

		else:	
			outputDict[smell_word_tag].append(" ".join(span))
			firstID = myID
			span = []
			span.append(myToken)

	outputDict[smell_word_tag].append(" ".join(span))

	
	#frame-elements

	

	for frameElement in frameElements:
		span = []
		outputDict[frameElement] = []
		if len(annotationsDict[frameElement]) == 0:
			continue
		
		firstID = int(annotationsDict[frameElement][0][tokenID].split("-")[1])-1
		
		for f in annotationsDict[frameElement]:

			myID = f[tokenID].split("-")[1]
			myToken = f[textIndex]
			
			if int(myID) == int(firstID)+1:
				span.append(myToken)
				firstID = myID
		
			else:	
				if " ".join(span).lower() not in spamList:
					outputDict[frameElement].append(" ".join(span))
				firstID = myID
				span = []
				span.append(myToken)

		if " ".join(span).lower() not in spamList:
			outputDict[frameElement].append(" ".join(span))
	
	return(outputDict)

def dictToString (myDict):
	myList = []
	myList.append("|".join(myDict[smell_word_tag]))
	for f in frameElements:
		myList.append("|".join(myDict[f]))
	return("\t".join(myList)+"\t")








def make_excel(myFile):
	annotations_list = []
	sentence_list = []
	
	all_lines = []
	
	
	counter = 0
	all_annotations_dict = dict()
	all_sentences_dict = dict()
	all_sentences_dict[0] = []
	all_titles_dict = dict()
	with open(myFile, 'r') as file:

		for line in file:
			line = line.strip()
			parts = line.split("\t")
			
			
			
			if line == "":
				counter += 1
				all_annotations_dict[counter] = annotations_list
				all_sentences_dict[counter] = sentence_list
				all_titles_dict[counter] = title
				sentence_list = []
				annotations_list = []

				continue

			title = parts[0]

			try:
				sentence_list.append(parts[textIndex])
			except:
				aaaa=1
			for p in parts[textIndex+1:]:
				if p != "O":
					annotations_list.append(parts)
					continue

		all_sentences_dict[counter+1] = []						

	for i in all_annotations_dict:
		# print(i)
		# print(i,all_titles_dict[i])
		# print(i,all_sentences_dict[i])
		# print(i,all_annotations_dict[i])
		# print()
		annotations_list = all_annotations_dict[i]
		
		sentence_list_before = all_sentences_dict[i-1]
		sentence_list = all_sentences_dict[i]
		sentence_list_after = all_sentences_dict[i+1]
		title = all_titles_dict[i]

		

		if len(annotations_list) > 1:
			
			dictAnnotations = pocess_annotations(annotations_list)
			
			if dictAnnotations != None:
				stringToPrint = dictToString(dictAnnotations)
				tmpString = title+"\t"+stringToPrint+" ".join(sentence_list_before)+"\t"+" ".join(sentence_list)+"\t"+" ".join(sentence_list_after)
				parts = tmpString.split("\t")
				all_lines.append(parts)
				if "\t\t" not in stringToPrint:
					tmpString = title+"\t"+stringToPrint+" ".join(sentence_list_before)+"\t"+" ".join(sentence_list)+"\t"+" ".join(sentence_list_after)
					parts = tmpString.split("\t")
					all_lines.append(parts)
					
					
					
	myHeaderString = "Book\t"+smell_word_tag+"\t"+"\t".join(frameElements)+"\tSentenceBefore\tSentence\tSentenceAfter"
	myHeader = myHeaderString.split("\t")
	df = pd.DataFrame(all_lines)
	df.columns=myHeader[:len(df.columns)]

	# df.to_excel(Path(myOut), sheet_name="FrameElements")
	# df.to_csv(outPath, index=False)
	return(df)