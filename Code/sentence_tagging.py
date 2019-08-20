
# Packages
import pandas as pd
import os
import json
from gensim.utils import simple_preprocess
from gensim.summarization.textcleaner import split_sentences
from functools import reduce
from fuzzywuzzy import fuzz


## Functions
## Returns marked html from iucn notes
def find_country(text, country):
	'''Function to id country names in iucn notes and insert mark tags for 
	highlighting in html'''

	# # Split text into individual words
	txt_ls = text.split(" ")
	q_ls = country.split(" ")

	# given length of country 
	q_len = len(q_ls)

	interest = [0]*len(txt_ls)

	# check each subset of n words for matches
	for i in range(len(txt_ls)-q_len+1):
		tmp_txt = (" ").join(txt_ls[i:i+q_len])

		if fuzz.token_set_ratio(tmp_txt, country)>=90:
			interest[i:i+q_len] = [1]*q_len

	# use index list to find words to highlight
	for w in range(len(txt_ls)):
		if interest[w] == 1:
			txt_ls[w] = "<mark>"+txt_ls[w]+"</mark>"

	recomb_html = " ".join(txt_ls)
	# If consecutive words highlighted, rm end and start
	recomb_html = recomb_html.replace("</mark> <mark>", " ")
	
	# for t in range(len(word_ls)):
	# 	# Match word against country
	# 	pr = fuzz.token_set_ratio(word_ls[t], country)
	# 	# If match is good, add html marks...	
	# 	if pr>90:
	# 		# print (word_ls[t])
	# 		word_ls[t] = "<mark>"+word_ls[t]+"</mark>"
	
	# Split text into sentences within paragraphs
	# split_txt = [split_sentences(para) for para in text.split("\n") if len(split_sentences(para))>0]
	# # interest_idx = [[0] * len(inner) for inner in split_txt]

	# for p in range(len(split_txt)):
	# 	for s in range(len(split_txt[p])):
	# 		# for each sentence fuzzy match against country
	# 		pr = fuzz.token_set_ratio(split_txt[p][s], country)
	# 		# If match is good, indicate in interest list or add marks...
	# 		if pr>90:
	# 			# interest_idx[p][s] += 1
	# 			# Add "<mark>" to start and "</mark>" end of sentence?
	# 			split_txt[p][s] = "<mark>"+split_txt[p][s]+"</mark>"

	# recomb_html = "\n".join([" ".join(inner) for inner in split_txt])
	# recomb_html = " ".join(word_ls)
	return(recomb_html)

# Extracts data from dictionary level given a list of indices to that level
def get_from_dict(dataDict, pathlist):
	"""Iterate nested dictionary"""
	return reduce(dict.get, pathlist, dataDict)


## Constants
notes_paths = {"taxonomic_notes" : ["taxonomy", "taxonomic_notes", "value"], 
				"red_list_notes" : ["iucn_status", "red_list_notes", "value"], 
				"range_notes" : ["habitat", "range_notes", "value"],  
				"population_notes" : ["population", "population_notes", "value"], 
				"use_trate_notes" : ["trade", "use_trade_notes", "value"], 
				"conservation_notes" : ["conservation", "conservation_notes", "value"], 
				"threats_notes" : ["threats", "threats_notes", "value"]}


## Main code
# Load cites df for relevant countries
cites_df = pd.read_csv("../Data/CitesParrots.csv")
cites_country_code = list(set(list(cites_df["Importer"])+(list(cites_df["Exporter"]))))

# Load country list data data
country_df = pd.read_csv("../Data/countries.csv")
# Subset to countries of interest
country_df = country_df.loc[country_df["Code"].isin(cites_country_code)]
# Create a simpler, single word country name
country_df["Basic"] = [country.split("(")[0].split(",")[0] for country in country_df["Name"]]


# List all json files
dat_dir = "../Data/parrot_data/"
f_ls = os.listdir(dat_dir)
# Calc no of rows need in output df
n_row = len(f_ls) * country_df.shape[0] 

out_df = pd.DataFrame({"SpeciesID" : ["NA"]*n_row,
						"Country" : ["NA"]*n_row,
							"taxonomic_notes" : ["NA"]*n_row, 
							"red_list_notes" : ["NA"]*n_row,
							"range_notes" : ["NA"]*n_row,
							"population_notes" : ["NA"]*n_row, 
							"use_trate_notes" : ["NA"]*n_row, 
							"conservation_notes" : ["NA"]*n_row, 
							"threats_notes" : ["NA"]*n_row})


row_count = 0
for f in f_ls:
	# Load json
	with open(dat_dir+f) as json_file:
		parrot_dat = json.load(json_file)
	parrot = f.split(".")[0]

	# Is IUCN data there?
	if len(parrot_dat["iucn"])>0:
		iucn_dat = parrot_dat["iucn"]
		for country in country_df["Basic"]:
			for key in notes_paths.keys():
				# Obtain data
				tmp_dat = get_from_dict(iucn_dat, notes_paths[key])
				# If not "NA" or "value" add to notes dict
				if ((tmp_dat != "NA") & (tmp_dat != "value")):
					out_df.iloc[row_count][key] = find_country(tmp_dat, country)
			out_df.iloc[row_count]["SpeciesID"] = parrot
			out_df.iloc[row_count]["Country"] = country
			row_count +=1

# print(row_count)
out_df = out_df.loc[0:row_count-1]
# out_df.to_csv("../../Local_Code/Data/marked_text.csv")

idx = int((row_count-1)/3.0)

out_df1 = out_df.loc[0:idx]
out_df2 = out_df.loc[idx+1:2*idx]
out_df3 = out_df.loc[2*idx+1:row_count-1]

out_df1.to_csv("../Data/parrot_csv/marked_text1.csv")
out_df2.to_csv("../Data/parrot_csv/marked_text2.csv")
out_df3.to_csv("../Data/parrot_csv/marked_text3.csv")

