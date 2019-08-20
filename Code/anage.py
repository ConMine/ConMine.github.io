#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  anage.py

##################
###LOADING MODULES
##################

import requests
import pandas as pd #For using dataframes
import numpy as np #For arrays
import sys
import json

###################
###DEFINE CONSTANTS
###################

name = sys.argv[1]
# name = "Psittacus erithacus"
# name = "Loxodonta africana"
# name = "Jynx torquilla"

with open("../Data/template.json") as json_file:
        output = json.load(json_file)

#################
###Main body
#################

#read in df
anage_df = pd.read_csv('../Data/anage_data.txt', sep='\t')
#combine to get binomial column
anage_df['binomial'] = (anage_df['Genus'] + ' ' + anage_df['Species'])
#extract species row
sp_row = anage_df[list(anage_df['binomial'] == name)]

if sp_row.empty:
        print("No data bro")
else:
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

        print(json.dumps(output, indent=4, sort_keys=True))
