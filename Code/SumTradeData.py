#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  SumTradeData.py
#

###################
### Loading Modules
###################

import pandas as pd
import numpy as np
import sys
import os
import matplotlib.pyplot as plt  


# Make fig directory
fig_dir = '../Results/Figures'

if not os.path.exists(fig_dir):
	os.makedirs(fig_dir)

##############
## Reading csv
##############

Export_Data = pd.read_csv("../Data/GreyParrot.csv")

#----------------------------------------------------------------------#

#############################
### Calculating summary stats
#############################

## Total global exports
Total_Global_Exports = len(Export_Data['Exporter reported quantity'])

## Total global imports
Total_Global_Exports = len(Export_Data['Importer reported quantity'])

## How many of those reported export quantities
Reported_Quantities = len(Export_Data['Exporter reported quantity'].dropna())

## Total export quantities
Total_Export_Quantities = sum(Export_Data['Exporter reported quantity'].dropna())

## Leading exporter countries and amount
Leading_Export_Country = Export_Data.groupby('Exporter').size().sort_values(ascending = False).head(1)

## Top five exporter countries and amount
Top_Five_Export_Countries = Export_Data.groupby('Exporter').size().sort_values(ascending = False).head(5)

## Leading Export Country with Reported Quantity
Leading_Export_Country_Quantity = Export_Data[['Exporter', 'Exporter reported quantity']].groupby('Exporter').sum().sort_values(by = 'Exporter reported quantity', ascending = False).head(1)

## Leading importer countries and amount
Leading_Import_Country = Export_Data.groupby('Importer').size().sort_values(ascending = False).head(1)

## Top five exporter countries and amount
Top_Five_Import_Countries = Export_Data.groupby('Importer').size().sort_values(ascending = False).head(5)

##Leading Export Country with Reported Quantity
Leading_Import_Country_Quantity = Export_Data[['Importer', 'Importer reported quantity']].groupby('Importer').sum().sort_values(by = 'Exporter reported quantity', ascending = False).head(1)

#----------------------------------------------------------------------#

### Change summary

## Change in export frequency globally
exportsubset = Export_Data.loc[Export_Data['Exporter reported quantity'] > 0]
temp = exportsubset.groupby('Year').size().reset_index()
Total_Change_Exports = int(temp[0].tail(1)) - int(temp[0].head(1))

## Change in exports quantities globally
temp1 = Export_Data.groupby('Year').sum().reset_index()
Total_Change_Export_Quantity = int(temp1['Exporter reported quantity'].tail(1)) - int(temp1['Exporter reported quantity'].head(1))

# Plot of Imports and Exports through time
plt.cla()
plt.clf()
# plt.close()
plt.plot(temp1["Year"], temp1["Importer reported quantity"], "b", label = "Imports")
plt.plot(temp1["Year"], temp1["Exporter reported quantity"], "r", label = "Exports")
plt.legend()
plt.xlabel("Year")
plt.ylabel("Quantity")
plt.title("Global trade of Grey Parrots")
# plt.show()
# plt.savefig("../../Local_Code/global_trade.png", dpi = 300) 
plt.savefig("../"+fig_dir+"/global_trade.png", dpi = 300)
plt.cla()
plt.clf()
# plt.close()

## Mean change per year in export frequency globally
exportsubset = Export_Data.loc[Export_Data['Exporter reported quantity'] > 0]
temp = exportsubset.groupby('Year').size().reset_index()
Mean_Change_Freq_Per_Year = (np.array(temp1[0][1:]) - np.array(temp1[0][:-1])).mean()

## Mean change per year in export quantity globally
temp1 = Export_Data.groupby('Year').sum().reset_index()
Mean_Change_Quan_Per_Year = (np.array(temp1['Exporter reported quantity'][1:]) - np.array(temp1['Exporter reported quantity'][:-1])).mean()

#----------------------------------------------------------------------#

## Change in export frequency for a specific country
# Take specific country from user
country = input("Which country? ")
exportsubset = Export_Data.loc[Export_Data['Exporter reported quantity'] > 0]
subset2 = exportsubset.loc[Export_Data['Exporter'] == country]
temp2 = subset2.groupby('Year').size().reset_index()
Mean_Change_Freq_For_Country = (np.array(temp2[0][1:]) - np.array(temp2[0][:-1])).mean()

## Change in export quantities for a specific country
# Take specific country from user
country = input("Which country? ")
exportsubset = Export_Data.loc[Export_Data['Exporter reported quantity'] > 0]
subset2 = exportsubset.loc[exportsubset['Exporter'] == country]
temp3 = subset2.groupby('Year').sum().reset_index()
Mean_Change_Quan_For_Country = (np.array(temp3['Exporter reported quantity'][1:]) - np.array(temp3['Exporter reported quantity'][:-1])).mean()
Mean_Change_Quan_For_Country

## Change in export frequency for all countries
Mean_Change_Freq_For_All_Country = []
exportsubset = Export_Data.loc[Export_Data['Exporter reported quantity'] > 0]
for i in exportsubset['Exporter'].unique():
	subset2 = exportsubset.loc[exportsubset['Exporter'] == i]
	temp2 = subset2.groupby('Year').size().reset_index()
	meanchange = (np.array(temp2[0][1:]) - np.array(temp2[0][:-1])).mean()
	meanchangecountry = (i, meanchange)
	Mean_Change_Freq_For_All_Country.append(meanchangecountry)
Mean_Change_Freq_For_All_Country
	
## Change in export quantity for all countries
Mean_Change_Quan_For_All_Country = []
exportsubset = Export_Data.loc[Export_Data['Exporter reported quantity'] > 0]
for i in exportsubset['Exporter'].unique():
	subset2 = exportsubset.loc[exportsubset['Exporter'] == i]
	temp3 = subset2.groupby('Year').sum().reset_index()
	meanchange = (np.array(temp3['Exporter reported quantity'][1:]) - np.array(temp3['Exporter reported quantity'][:-1])).mean()
	meanchangecountry = (i, meanchange)
	Mean_Change_Quan_For_All_Country.append(meanchangecountry)
Mean_Change_Quan_For_All_Country

#----------------------------------------------------------------------#

## Change in export frequency depending on appendix level (3,2a,2b – should be no exports for appendix 1)
# Take specific appendix from user
appendix = input("Which appendix (I, II, or II)? ")
exportsubset = Export_Data.loc[Export_Data['Exporter reported quantity'] > 0]
subset3 = exportsubset.loc[exportsubset['App.'] == appendix]
temp4 = subset3.groupby('Year').size().reset_index()
Mean_Change_Freq_For_Appendix = (np.array(temp4[0][1:]) - np.array(temp4[0][:-1])).mean()

## Change in export quantity depending on appendix level (3,2a,2b – should be no exports for appendix 1)
# Take specific appendix from user
appendix = input("Which appendix (I, II, or II)? ")
exportsubset = Export_Data.loc[Export_Data['Exporter reported quantity'] > 0]
subset3 = exportsubset.loc[exportsubset['App.'] == appendix]
temp5 = subset3.groupby('Year').sum().reset_index()
Mean_Change_Quan_For_Appendix = (np.array(temp5['Exporter reported quantity'][1:]) - np.array(temp5['Exporter reported quantity'][:-1])).mean()

## Change in export frequency for all appendices
Mean_Change_Freq_For_All_Appendices = []
exportsubset = Export_Data.loc[Export_Data['Exporter reported quantity'] > 0]
for i in exportsubset['App.'].unique():
	subset3 = exportsubset.loc[exportsubset['App.'] == i]
	temp4 = subset3.groupby('Year').size().reset_index()
	meanchange = (np.array(temp4[0][1:]) - np.array(temp4[0][:-1])).mean()
	meanchangeapp = (i, meanchange)
	Mean_Change_Freq_For_All_Appendices.append(meanchangeapp)

## Change in export quantity for all appendices
Mean_Change_Quan_For_All_Appendices = []
exportsubset = Export_Data.loc[Export_Data['Exporter reported quantity'] > 0]
for i in exportsubset['App.'].unique():
	subset3 = exportsubset.loc[exportsubset['App.'] == i]
	temp5 = subset3.groupby('Year').sum().reset_index()
	meanchange = (np.array(temp5['Exporter reported quantity'][1:]) - np.array(temp5['Exporter reported quantity'][:-1])).mean()
	meanchangeapp = (i, meanchange)
	Mean_Change_Quan_For_All_Appendices.append(meanchangeapp)

# Plots for appendix 1, 2, 3....
app_I_trade = Export_Data.loc[Export_Data["App."] == "I"].groupby("Year").sum().reset_index()
app_II_trade = Export_Data.loc[Export_Data["App."] == "II"].groupby("Year").sum().reset_index()
app_III_trade = Export_Data.loc[Export_Data["App."] == "III"].groupby("Year").sum().reset_index()

# plt.plot(app_I_trade["Year"], app_I_trade["Importer reported quantity"], "b^", label = "Imports")
# plt.plot(app_I_trade["Year"], app_I_trade["Exporter reported quantity"], "r^", label = "Exports")
# plt.legend()
# plt.xlabel("Year")
# plt.ylabel("Quantity")
# plt.title("Global trade of Grey Parrots under Appendix I")
# # plt.show()

# plt.plot(app_II_trade["Year"], app_II_trade["Importer reported quantity"], "b", label = "Imports")
# plt.plot(app_II_trade["Year"], app_II_trade["Exporter reported quantity"], "r", label = "Exports")
# plt.legend()
# plt.xlabel("Year")
# plt.ylabel("Quantity")
# plt.title("Global trade of Grey Parrots under Appendix II")
# # plt.show()

# plt.plot(app_III_trade["Year"], app_III_trade["Importer reported quantity"], "bs", label = "Imports")
# plt.plot(app_III_trade["Year"], app_III_trade["Exporter reported quantity"], "rs", label = "Exports")
# plt.legend()
# plt.xlabel("Year")
# plt.ylabel("Quantity")
# plt.title("Global trade of Grey Parrots under Appendix III")
# plt.show()

plt.plot(app_I_trade["Year"], app_I_trade["Importer reported quantity"], "b^", alpha = 0.5, label = "Imports - App. I")
plt.plot(app_I_trade["Year"], app_I_trade["Exporter reported quantity"], "r^", alpha = 0.5, label = "Exports - App. I")
plt.plot(app_II_trade["Year"], app_II_trade["Importer reported quantity"], "b", label = "Imports - App. II")
plt.plot(app_II_trade["Year"], app_II_trade["Exporter reported quantity"], "r", label = "Exports - App. II")
plt.plot(app_III_trade["Year"], app_III_trade["Importer reported quantity"], "bs", alpha = 0.5, label = "Imports - App. III")
plt.plot(app_III_trade["Year"], app_III_trade["Exporter reported quantity"], "rs", alpha = 0.5, label = "Exports - App. III")
plt.legend()
plt.xlabel("Year")
plt.ylabel("Quantity")
plt.title("Global trade of Grey Parrots under different Appendices")
# plt.show()
# fig2 = plt.figure()
# plt.savefig("../../Local_Code/global_trade_app.png", dpi = 300)
plt.savefig("../"+fig_dir+"/global_trade_app.png", dpi = 300)
plt.cla()
plt.clf()

#----------------------------------------------------------------------#

## Change in exports depending on IUCN status

#~ find IUCN status from API
#~ Append IUCN status to each year
#~ Examine change per year as above

#----------------------------------------------------------------------#

### Number of deaths on route (Imported - Exported)

## Total deaths globally
# Subsetting live specimens
livesubset = Export_Data.loc[Export_Data['Term'] == 'live']
# Subetting data with both import and export quantities
quantsubset = livesubset.loc[(livesubset['Importer reported quantity'] > 0) & (livesubset['Exporter reported quantity'] > 0)].reset_index(drop = True)
Deaths = []
for i,j in zip(quantsubset['Exporter reported quantity'], quantsubset['Importer reported quantity']):
	deaths = j - i
	if deaths > 0:# Because some of the exports increase on arrival
		Deaths.append(deaths)
Total_Deaths_Globally = sum(Deaths)

## Total Deaths Per Year
# Subsetting live specimens with both import and export quantities
livesubset = Export_Data.loc[Export_Data['Term'] == 'live']
quantsubset = livesubset.loc[(livesubset['Importer reported quantity'] > 0) & (livesubset['Exporter reported quantity'] > 0)].reset_index(drop = True)

Total_Deaths_Per_Year = []
for l in quantsubset['Year'].unique():
	year = quantsubset.loc[quantsubset['Year'] == l]
	deaths = []
	for i,j in zip(year['Exporter reported quantity'], year['Importer reported quantity']):
		value = j - i
		if value > 0:# Because some of the exports increase on arrival
			deaths.append(value)
	totaldeaths = sum(deaths)
	deathsperyear = [l, totaldeaths]
	Total_Deaths_Per_Year.append(deathsperyear)

# Plot of number of deaths during transit - is this how the data works
death_matr = np.matrix(Total_Deaths_Per_Year)
plt.plot(death_matr[:,0], death_matr[:,1], "black")
plt.xlabel("Year")
plt.ylabel("Quantity")
plt.title("Deaths of Grey Parrots during trade")
# plt.show()
# plt.savefig("../../Local_Code/global_deaths.png", dpi = 300)
plt.savefig("../"+fig_dir+"/global_deaths.png", dpi = 300)
plt.cla()
plt.clf()

#Mean deaths per year
Totals = []
for i in Total_Deaths_Per_Year:
	value = i[1]
	Totals.append(value)
Mean_Deaths_Per_year = np.array(Totals).mean()
Mean_Deaths_Per_year


