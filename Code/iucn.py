#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  iucn.py

##################
###LOADING MODULES
##################

import requests
import pandas as pd #For using dataframes
import numpy as np #For arrays
import sys
import json
import re

##################
###ACCESSING API"s
##################

###Accessing IUCN API
##Entering name

name = sys.argv[1]
# name = "Loxodonta africana"
# name = "Psittacus erithacus"

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
res = response.json()

if res["count"] != 0:
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
else:
	data["taxonomy"]["synonyms"]["value"] = "NA"


###Individual species by name request
response = requests.get("http://apiv3.iucnredlist.org/api/v3/species/" + name,
						params = {"token" : tok})
res = response.json()

# Population trend
if res["result"][0]["population_trend"] is not None:
	data["population"]["population_trend"]["value"] = res["result"][0]["population_trend"]
else:
	data["population"]["population_trend"]["value"] = "NA"

# AOO
if res["result"][0]["aoo_km2"] is not None:
	data["habitat"]["area_of_occupancy"]["value"] = res["result"][0]["aoo_km2"]
	data["habitat"]["area_of_occupancy"]["unit"] = "km2"
else:
	data["habitat"]["area_of_occupancy"]["value"] = "NA"
	data["habitat"]["area_of_occupancy"]["unit"] = "NA"

# EOO
if res["result"][0]["eoo_km2"] is not None:
	data["habitat"]["extent_of_occurrence"]["value"] = res["result"][0]["eoo_km2"]
	data["habitat"]["extent_of_occurrence"]["unit"] = "km2"
else:
	data["habitat"]["extent_of_occurrence"]["value"] = "NA"
	data["habitat"]["extent_of_occurrence"]["unit"] = "NA"


### Country occurrence by species name
response = requests.get("http://apiv3.iucnredlist.org/api/v3/species/countries/name/"+name,
						params = {"token" : tok})
res = response.json()

if res["count"] != 0:
	##Number and list of countries of occurrence
	countrylist = [res["result"][i]["country"] for i in range(len(res["result"])) \
					if res["result"][i]["presence"] == "Extant"]

	data["habitat"]["countries_of_occurrence"]["value"] = countrylist
	data["habitat"]["countries_of_occurrence"]["unit"] = "Extant in country"

else:
	data["habitat"]["countries_of_occurrence"]["value"] = "NA"
	data["habitat"]["countries_of_occurrence"]["unit"] = "NA"


### Red List assessments by species name
response = requests.get("http://apiv3.iucnredlist.org/api/v3/species/history/name/"+name,
						params = {"token" : tok})
res = response.json()

##Current Red List Category
cat_yr = tuple((res["result"][0]["category"], res["result"][0]["year"]))
data["iucn_status"]["red_list_category"]["value"] = cat_yr

## Historical Red List Categories
if len(res["result"]) > 1:
	hist_cat_yr = [tuple((res["result"][i]["category"], res["result"][i]["year"])) \
					for i in range(1, len(res["result"]))]

	data["iucn_status"]["historical_categories"]["value"] = hist_cat_yr

else:
	data["iucn_status"]["historical_categories"]["value"] = "NA"


### Threats by species name
response = requests.get("http://apiv3.iucnredlist.org/api/v3/threats/species/name/"+name,
						params = {"token" : tok})
res = response.json()

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


###Habitats by species name
response = requests.get("http://apiv3.iucnredlist.org/api/v3/habitats/species/name/"+name,
						params = {"token" : tok})
res = response.json()

data["habitat"]["habitats"] = res["result"]


#Specificity
# specificity = len(list(set(habitattype)))/13
# print("Habitat specificity: " + str(specificity))

### Conservation measures by species name
response = requests.get("http://apiv3.iucnredlist.org/api/v3/measures/species/name/"+name,
						params = {"token" : tok})
res = response.json()

measures = [res["result"][i]["title"] for i in range(len(res["result"]))]
data["conservation"]["management_practices"]["value"] = measures


###Narrative text by species name
response = requests.get("http://apiv3.iucnredlist.org/api/v3/species/narrative/"+name,
						params = {"token" : tok})
res = response.json()

# Regex fro html tags
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


print(json.dumps(data, indent=4, sort_keys=False))
