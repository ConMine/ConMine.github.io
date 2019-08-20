#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# conmine.py


# Load modules
import requests
import pandas as pd #For using dataframes
import numpy as np #For arrays
import sys
import json
import re
import os
import time
import random

# Function to collect data from eol
def eol(name):
	eol_base_url = "https://eol.org/service/cypher"

	#read in eol token
	with open("../config.json") as json_f:
		token = json.load(json_f)

	eol_tok = token["EOL_TOK"]

	# Establish data structure
	with open("../Data/template.json") as json_f:
		output = json.load(json_f)

	# Generate query
	query = "MATCH (t:Trait)<-[:trait]-(p:Page), \
				(t)-[:supplier]->(r:Resource), \
				(t)-[:predicate]->(pred:Term) \
			WHERE p.canonical = '" + name + "'"\
			"OPTIONAL MATCH (t)-[:units_term]->(units:Term) \
			OPTIONAL MATCH (t)-[:object_term]->(obj:Term) \
			OPTIONAL MATCH (t)-[:normal_units_term]->(normal_units:Term) \
			OPTIONAL MATCH (t)-[:sex_term]->(sex:Term) \
			OPTIONAL MATCH (t)-[:lifestage_term]->(lifestage:Term) \
			OPTIONAL MATCH (t)-[:statistical_method_term]->(stats:Term) \
			RETURN p.canonical, pred.name, obj.name, t.literal, t.measurement, units.name, t.normal_measurement, normal_units.name, sex.name, lifestage.name, stats.name, stats.comment, r.resource_id, p.page_id, t.eol_pk, t.source \
			LIMIT 500"

	data = {"query" : query,
			"format" : "cypher"}

	# Send api call
	r = requests.get(eol_base_url,
					headers = {"accept" : "application/json",
								"authorization" : "JWT " + eol_tok},
					params = data)

	# Check for bad request...
	if r.status_code != 200:
		print ("Error: Unsuccessful api call.")
		return None
	
	j = r.json()

	# Convert to df
	df = pd.DataFrame(j["data"])

	# Check for presence of data
	if df.shape[0]==0:
		print ("No data found.")
		return None

	df.columns = j["columns"]

	# Drop rows where source is anage or iucn
	df["t.source"] = df["t.source"].fillna(value = "NA")
	df["Ignore_source"] = [1 if any(s in x for s in["genomics.senescence", "iucn"]) else 0 for x in df["t.source"].tolist()]

	df = df[df["Ignore_source"] != 1]
	if df.shape[0]==0:
		print ("No eol data found.")
		return None

	df_datafields = df["pred.name"].unique().tolist()

	# Extract relevant data
	# Habitat related data
	if "habitat includes" in df_datafields:
		output["habitat"]["habitats"] = df.loc[df["pred.name"] == "habitat includes", "obj.name"].unique().tolist()

	# Pretty much countries of occurence but sum within county data too...
	if "geographic distribution includes" in df_datafields:
		output["habitat"]["countries_of_occurrence"]["value"] = df.loc[df["pred.name"] == "geographic distribution includes", "obj.name"].tolist()
		output["habitat"]["countries_of_occurrence"]["unit"] = "Extant in country"

	# Native range
	if "native range includes" in df_datafields:
		output["habitat"]["native_range"]["value"] = df.loc[df["pred.name"] == "native range includes", "obj.name"].tolist()
		output["habitat"]["native_range"]["unit"] = "Locations where the species is native"

	# Introduced locations
	if "introduced range includes" in df_datafields:
		output["habitat"]["introduced_range"]["value"] = df.loc[df["pred.name"] == "introduced range includes", "obj.name"].tolist()
		output["habitat"]["introduced_range"]["unit"] = "Locations where the species has been introduced"

	# Body mass
	if "body mass" in df_datafields:
		if df.loc[(df["pred.name"] == "body mass") &
					(df["lifestage.name"].isnull()) &
					(df["stats.name"] == "average"),:].shape[0] > 0:
					# Could be improved to obtain info from various sources...
			output["life_history_traits"]["bodymass"]["adult_bodymass"]["value"] = df.loc[(df["pred.name"] == "body mass") & (df["lifestage.name"].isnull()) & (df["stats.name"] == "average"), "t.normal_measurement"].values[0]
			output["life_history_traits"]["bodymass"]["adult_bodymass"]["unit"] = df.loc[(df["pred.name"] == "body mass") & (df["lifestage.name"].isnull()) & (df["stats.name"] == "average"), "normal_units.name"].values[0]

	return output


def iucn(name):
	# Counter to check if data added to json
	dat_count = 0

	#read in eol token
	with open("../config.json") as json_f:
		token = json.load(json_f)

	tok = token["IUCN_TOK"]

	# Establish data structure
	with open("../Data/template.json") as json_f:
		data = json.load(json_f)

	### Find synonyms
	response = requests.get("http://apiv3.iucnredlist.org/api/v3/species/synonym/"+name,
							params = {"token" : tok})

	if response.status_code == 200:
		res = response.json()

		if res["count"] != 0:
			dat_count += 1
			# Check if given name is accepted name
			if name == res["result"][0]["accepted_name"]:
				synonyms = [res["result"][i]["synonym"] for i in range(len(res["result"]))]
				data["taxonomy"]["synonyms"]["value"] = synonyms

			# If provided name is a synonym, assign accepted name as <name> and use from here on.
			elif name != res["result"][0]["accepted_name"]:
				print ("Name provided is a synonym, fool!")
				name = res["result"][0]["accepted_name"]

				response = requests.get("http://apiv3.iucnredlist.org/api/v3/species/synonym/"+name,
								params = {"token" : tok})
				res = response.json()

				if res["count"] != 0:
					synonyms = [res["result"][i]["synonym"] for i in range(len(res["result"]))]
					data["taxonomy"]["synonyms"]["value"] = synonyms
		# else:
		# 	data["taxonomy"]["synonyms"]["value"] = "NA"

	time.sleep(random.randint(5,10))

	###Individual species by name request
	response = requests.get("http://apiv3.iucnredlist.org/api/v3/species/" + name,
							params = {"token" : tok})
	
	if response.status_code == 200:
		res = response.json()
		if len(res["result"])>0:
			dat_count += 1
			# Population trend
			if res["result"][0]["population_trend"] is not None:
				data["population"]["population_trend"]["value"] = res["result"][0]["population_trend"]
			# else:
			# 	data["population"]["population_trend"]["value"] = "NA"

			# AOO
			if res["result"][0]["aoo_km2"] is not None:
				data["habitat"]["area_of_occupancy"]["value"] = res["result"][0]["aoo_km2"]
				data["habitat"]["area_of_occupancy"]["unit"] = "km2"
			# else:
			# 	data["habitat"]["area_of_occupancy"]["value"] = "NA"
			# 	data["habitat"]["area_of_occupancy"]["unit"] = "NA"

			# EOO
			if res["result"][0]["eoo_km2"] is not None:
				data["habitat"]["extent_of_occurrence"]["value"] = res["result"][0]["eoo_km2"]
				data["habitat"]["extent_of_occurrence"]["unit"] = "km2"
			# else:
			# 	data["habitat"]["extent_of_occurrence"]["value"] = "NA"
			# 	data["habitat"]["extent_of_occurrence"]["unit"] = "NA"

	time.sleep(random.randint(5,10))
	
	### Country occurrence by species name
	response = requests.get("http://apiv3.iucnredlist.org/api/v3/species/countries/name/"+name,
							params = {"token" : tok})
	if response.status_code == 200:
		res = response.json()

		if res["count"] != 0:
			dat_count += 1
			##Number and list of countries of occurrence
			countrylist = [res["result"][i]["country"] for i in range(len(res["result"])) \
							if res["result"][i]["presence"] == "Extant"]

			data["habitat"]["countries_of_occurrence"]["value"] = countrylist
			data["habitat"]["countries_of_occurrence"]["unit"] = "Extant in country"

		# else:
		# 	data["habitat"]["countries_of_occurrence"]["value"] = "NA"
		# 	data["habitat"]["countries_of_occurrence"]["unit"] = "NA"

	time.sleep(random.randint(5,10))
	
	### Red List assessments by species name
	response = requests.get("http://apiv3.iucnredlist.org/api/v3/species/history/name/"+name,
							params = {"token" : tok})
	if response.status_code == 200:
		res = response.json()

		if len(res["result"])>0:
			dat_count += 1
			##Current Red List Category
			cat_yr = tuple((res["result"][0]["category"], res["result"][0]["year"]))
			data["iucn_status"]["red_list_category"]["value"] = cat_yr

			## Historical Red List Categories
			if len(res["result"]) > 1:
				hist_cat_yr = [tuple((res["result"][i]["category"], res["result"][i]["year"])) \
								for i in range(1, len(res["result"]))]

				data["iucn_status"]["historical_categories"]["value"] = hist_cat_yr

			# else:
			# 	data["iucn_status"]["historical_categories"]["value"] = "NA"

	time.sleep(random.randint(5,10))

	### Threats by species name
	response = requests.get("http://apiv3.iucnredlist.org/api/v3/threats/species/name/"+name,
							params = {"token" : tok})
	if response.status_code == 200:
		res = response.json()

		if len(res["result"])>0:
			dat_count += 1
			##Impact on species
			threat = [res["result"][i]["title"] for i in range(len(res["result"]))]
			scope = [res["result"][i]["scope"] for i in range(len(res["result"]))]
			timing = [res["result"][i]["timing"] for i in range(len(res["result"]))]
			severity = [res["result"][i]["severity"] for i in range(len(res["result"]))]
			score = [res["result"][i]["score"] for i in range(len(res["result"]))]

			data["threats"]["threats"]["value"] = threat
			data["threats"]["scope"]["value"] = scope
			data["threats"]["timing"]["value"] = timing
			data["threats"]["severity"]["value"] = severity
			data["threats"]["score"]["value"] = score

	time.sleep(random.randint(5,10))

	###Habitats by species name
	response = requests.get("http://apiv3.iucnredlist.org/api/v3/habitats/species/name/"+name,
							params = {"token" : tok})
	if response.status_code == 200:
		res = response.json()
		if len(res["result"])>0:
			dat_count += 1
			data["habitat"]["habitats"] = res["result"]


	#Specificity
	# specificity = len(list(set(habitattype)))/13
	# print("Habitat specificity: " + str(specificity))
	time.sleep(random.randint(5,10))

	### Conservation measures by species name
	response = requests.get("http://apiv3.iucnredlist.org/api/v3/measures/species/name/"+name,
							params = {"token" : tok})
	if response.status_code == 200:
		res = response.json()
		if len(res["result"])>0:
			dat_count += 1
			measures = [res["result"][i]["title"] for i in range(len(res["result"]))]
			data["conservation"]["management_practices"]["value"] = measures

	time.sleep(random.randint(5,10))

	###Narrative text by species name
	response = requests.get("http://apiv3.iucnredlist.org/api/v3/species/narrative/"+name,
							params = {"token" : tok})
	if response.status_code == 200:
		res = response.json()

		# Regex for html tags
		htmltag = re.compile(r"<.+?>")

		# May be other issues, eg unicode etc...

		def collect_clean_narrative(key, narrative_dict):
			"""Function to obtain specific narrative and remove html marck-up etc.
			"""
			narrative = narrative_dict["result"][0][key]
			if narrative is not None:
				narrative = narrative.replace("&#160;", " ")
				narrative = narrative.replace("<br/>", "\n")
				narrative = htmltag.sub("", narrative)
			else:
				narrative = "NA"
			return (narrative)

		if len(res["result"])>0:
			dat_count += 1

			## Taxonomic notes if present (if synonyms exist...)
			if "taxonomicnotes" in res["result"][0].keys():
				taxnotes = collect_clean_narrative(key = "taxonomicnotes",
													narrative_dict = res)
				data["taxonomy"]["taxonomic_notes"]["value"] = taxnotes


			##Rationale for red list category
			if "rationale" in res["result"][0].keys():
				rationale = collect_clean_narrative(key = "rationale",
													narrative_dict = res)
				data["iucn_status"]["red_list_notes"]["value"] = rationale


			##Geographic range
			if "geographicrange" in res["result"][0].keys():
				georange = collect_clean_narrative(key = "geographicrange",
													narrative_dict = res)
				data["habitat"]["range_notes"]["value"] = georange


			##Population
			if "population" in res["result"][0].keys():
				popnote = collect_clean_narrative(key = "population",
													narrative_dict = res)
				data["population"]["population_notes"]["value"] = popnote


			##Threats Narrative
			if "threats" in res["result"][0].keys():
				threatnote = collect_clean_narrative(key = "threats",
													narrative_dict = res)
				data["threats"]["threats_notes"]["value"] = threatnote


			##Conservation Measures Narrative
			if "conservationmeasures" in res["result"][0].keys():
				consnote = collect_clean_narrative(key = "conservationmeasures",
													narrative_dict = res)
				data["conservation"]["conservation_notes"]["value"] = consnote


			##UseTrade
			if "usetrade" in res["result"][0].keys():
				tradenote = collect_clean_narrative(key = "usetrade",
													narrative_dict = res)
				data["trade"]["use_trade_notes"]["value"] = tradenote
	if dat_count == 0:
		print ("No iucn data found.")
		return None

	return data


# Function to collect data from anage database
def	anage(name):
	# Create output json
	with open("../Data/template.json") as json_file:
		output = json.load(json_file)

	#read in df
	anage_df = pd.read_csv("../Data/anage_data.txt", sep='\t')
	#combine to get binomial column
	anage_df['binomial'] = (anage_df['Genus'] + ' ' + anage_df['Species'])
	#extract species row
	sp_row = anage_df[list(anage_df['binomial'] == name)]

	if sp_row.empty:
		print("No anage data bro")
		return None

	# Get specific info
	#lifespan
	output["life_history_traits"]["lifespan"]["value"] = sp_row.iloc[0]["Maximum longevity (yrs)"]
	output["life_history_traits"]["lifespan"]["unit"] = "Years"

	#sexual_maturity_age
	#male
	output["life_history_traits"]["sexual_maturity_age"]["male"]["value"] = (sp_row.iloc[0]["Male maturity (days)"] / 365)
	output["life_history_traits"]["sexual_maturity_age"]["male"]["unit"] = "Years"
	#female
	output["life_history_traits"]["sexual_maturity_age"]["female"]["value"] = (sp_row.iloc[0]["Female maturity (days)"] / 365)
	output["life_history_traits"]["sexual_maturity_age"]["female"]["unit"] = "Years"

	#breeding Lifespan
	#male
	breeding_lifespan = sp_row.iloc[0]["Maximum longevity (yrs)"] - (sp_row.iloc[0]["Male maturity (days)"] / 365)
	output["life_history_traits"]["breeding_lifespan"]["male"]["value"] = breeding_lifespan
	output["life_history_traits"]["breeding_lifespan"]["male"]["unit"] = "Years"
	#female
	breeding_lifespan = sp_row.iloc[0]["Maximum longevity (yrs)"] - (sp_row.iloc[0]["Female maturity (days)"] / 365)
	output["life_history_traits"]["breeding_lifespan"]["female"]["value"] = breeding_lifespan
	output["life_history_traits"]["breeding_lifespan"]["female"]["unit"] = "Years"

	#generation_time
	output["life_history_traits"]["generation_time"]["value"] = "?"
	output["life_history_traits"]["generation_time"]["unit"] = "?"

	#clutch_size
	output["life_history_traits"]["clutch_size"]["value"] = sp_row.iloc[0]["Litter/Clutch size"]
	output["life_history_traits"]["clutch_size"]["unit"] = "Individuals"

	#breeding interval
	output["life_history_traits"]["breeding_interval"]["value"] = sp_row.iloc[0]["Inter-litter/Interbirth interval"]
	output["life_history_traits"]["breeding_interval"]["unit"] = "?"

	#Time to independence interval
	output["life_history_traits"]["time_to_independence"]["value"] = sp_row.iloc[0]["Weaning (days)"] / 365
	output["life_history_traits"]["time_to_independence"]["unit"] = "Years"

	#Hatching time
	output["life_history_traits"]["hatching_time"]["value"] = sp_row.iloc[0]["Gestation/Incubation (days)"] / 365
	output["life_history_traits"]["hatching_time"]["unit"] = "Years"

	#Breeding season
	output["life_history_traits"]["breeding_season"]["value"] = "?"
	output["life_history_traits"]["breeding_season"]["unit"] = "Years"

	#bodysize
	output["life_history_traits"]["bodymass"]["neonate_bodymass"]["value"] = sp_row.iloc[0]["Birth weight (g)"] / 1000
	output["life_history_traits"]["bodymass"]["neonate_bodymass"]["unit"] = "Kg"

	output["life_history_traits"]["bodymass"]["weaning_bodymass"]["value"] = sp_row.iloc[0]["Weaning weight (g)"] / 1000
	output["life_history_traits"]["bodymass"]["weaning_bodymass"]["unit"] = "Kg"

	output["life_history_traits"]["bodymass"]["adult_bodymass"]["value"] = sp_row.iloc[0]["Adult weight (g)"] / 1000
	output["life_history_traits"]["bodymass"]["adult_bodymass"]["unit"] = "Kg"

	return output


## Testing code...
# Specified parrot species
# parrot_species = ["Anodorhynchus leari", "Probosciger aterrimus", 
# 					"Eunymphicus cornutus", "Prosopeia personata", 
# 					"Tanygnathus lucionensis"]


## Main code ....
# Load parrot species 
sp_df = pd.read_csv("../Data/SpeciesList.csv")

parrot_species = set(sp_df["Binomial"])
# os.mkdir("../Data/parrot_data")

# 
for parrot in parrot_species:
	# time.sleep(10)
	print (parrot)
	dat_found = 0
	sp_dat = {"iucn" : {},
			"anage" : {},
			"eol" : {}}
	
	eol_dat = eol(parrot)
	if eol_dat != None:
		sp_dat["eol"] = eol_dat
		dat_found += 1

	anage_dat = anage(parrot)
	if anage_dat != None:
		sp_dat["anage"] = anage_dat
		dat_found += 1
	
	iucn_dat = iucn(parrot)
	if iucn_dat != None:
		sp_dat["iucn"] = iucn_dat
		dat_found += 1

	if dat_found > 0:
		print ("Saving data ...")
		with open("../Data/parrot_data/"+"_".join(parrot.split(" "))+".json", 'w') as json_f:
  			json.dump(sp_dat, json_f)
	# print("\n")
	# print (sp_dat)

	
parrot_list = os.listdir("../Data/parrot_data")

par = [p.split(".json")[0] for p in parrot_list]

par = [" ".join(p.split("_")) for p in par]

# Sp with no data
parrot_species.difference(set(par))
# {'Charmosyna aureicincta',
#  'Pionopsitta aurantiocephala',
#  'Pionopsitta pyrilia',
#  'Psittacula intermedia'}