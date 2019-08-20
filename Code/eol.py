#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  eol.py

##################
###LOADING MODULES
##################

import requests
import pandas as pd #For using dataframes
import numpy as np #For arrays
import sys
import json
import re


#####
# Constants
#####

eol_base_url = "https://eol.org/service/cypher"

#read in eol token
with open("../config.json") as json_f:
	token = json.load(json_f)

eol_tok = token["EOL_TOK"]

# Establish data structure
with open("../Data/template.json") as json_f:
	output = json.load(json_f)


#####
# Main code
#####

# Specify sp name
# sp_name = "Odocoileus hemionus"
# name = "Ara macao"
name = sys.argv[1]

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

j = r.json()

# Convert to df
df = pd.DataFrame(j["data"])
df.columns = j["columns"]

# Drop rows where source is anage or iucn
df["t.source"] = df["t.source"].fillna(value = "NA")
df["Ignore_source"] = [1 if any(s in x for s in["genomics.senescence", "iucn"]) else 0 for x in df["t.source"].tolist()]

df = df[df["Ignore_source"] != 1]

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


if "body mass" in df_datafields:
	if df.loc[(df["pred.name"] == "body mass") &
				(df["lifestage.name"].isnull()) &
				(df["stats.name"] == "max"),:].shape[0] > 0:
		output["life_history_traits"]["bodymass"]["adult_bodymass"]["value"] = df.loc[(df["pred.name"] == "body mass") & (df["lifestage.name"].isnull()) & (df["stats.name"] == "max"), "t.normal_measurement"].values[0]
		output["life_history_traits"]["bodymass"]["adult_bodymass"]["unit"] = df.loc[(df["pred.name"] == "body mass") & (df["lifestage.name"].isnull()) & (df["stats.name"] == "max"), "normal_units.name"].values[0]


print (json.dumps(output, indent=4, sort_keys=False))
# May be more data, depends on species searched for...
# Generally not much for parrots.

# Not normally in reduced df
# Population trend
# if "population trend" in df_datafields:
# 	output["population"]["population_trend"]["value"] = df.loc[df["pred.name"] == "population trend", "t.literal"].values[0]

# # Weights/bodymass??
# if "weight" in df_datafields:
# 	if df.loc[(df["pred.name"] == "weight") & (df["lifestage.name"] == "adult"),:].shape[0] > 0:
# 		output["bodymass"]["adult_bodymas"]["value"] = df.loc[(df["pred.name"] == "weight") & (df["lifestage.name"] == "adult"), "t.normal_measurement"].values[0]
# 		output["bodymass"]["adult_bodymas"]["unit"] = df.loc[(df["pred.name"] == "weight") & (df["lifestage.name"] == "adult"), "normal_units.name"].values[0]
# 	if df.loc[(df["pred.name"] == "weight") & (df["lifestage.name"] == "weanling"),:].shape[0] > 0:
# 		df.loc[(df["pred.name"] == "weight") & (df["lifestage.name"] == "weanling"), "t.normal_measurement"].values[0]
# 		df.loc[(df["pred.name"] == "weight") & (df["lifestage.name"] == "weanling"), "normal_units.name"].values[0]
# 	if df.loc[(df["pred.name"] == "weight") & (df["lifestage.name"] == "neonate stage"),:].shape[0] > 0:
# 		df.loc[(df["pred.name"] == "weight") & (df["lifestage.name"] == "neonate stage"), "t.normal_measurement"].values[0]
# 		df.loc[(df["pred.name"] == "weight") & (df["lifestage.name"] == "neonate stage"), "normal_units.name"].values[0]
