#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
cites_df = pd.read_csv('Data/cites_data.csv')
#extract species row
sp_row = cites_df[list(cites_df['Taxon'] == name)]

print(sp_row)
if sp_row.empty:
        print("No data bro")
else:
        #All trade data
        output["trade"]["year"]["value"] = sp_row.iloc[0]["Year"]

        output["trade"]["appendix"]["value"] = sp_row.iloc[0]["App."]

        output["trade"]["importer"]["value"] = sp_row.iloc[0]["Importer"]
        output["trade"]["importer"]["unit"] = "Country"

        output["trade"]["exporter"]["value"] = sp_row.iloc[0]["Exporter"]
        output["trade"]["exporter"]["unit"] = "Country"

        output["trade"]["origin"]["value"] = sp_row.iloc[0]["Origin"]
        output["trade"]["origin"]["unit"] = "Country"

        output["trade"]["imported_quantity"]["value"] = sp_row.iloc[0]["Importer reported quantity"]
        output["trade"]["imported_quantity"]["unit"] = "Number of items"

        output["trade"]["exported_quantity"]["value"] = sp_row.iloc[0]["Exporter reported quantity"]
        output["trade"]["exported_quantity"]["unit"] = "Number of items"

        output["trade"]["term"]["value"] = sp_row.iloc[0]["Term"]

        output["trade"]["unit"]["value"] = sp_row.iloc[0]["Unit"]

        output["trade"]["purpose"]["value"] = sp_row.iloc[0]["Purpose"]

        output["trade"]["source"]["value"] = sp_row.iloc[0]["Source"]

        # print(json.dumps(output, indent=4, sort_keys=True))
        # print(output)
