library(shiny)
library(tidyverse)

#Loading data
other_data <- read.csv("../Data/parrot_csv/parrot_shiny.csv",stringsAsFactors = F)
marked_text <- read.csv("../Data/parrot_csv/marked_text.csv",stringsAsFactors = F)


#get parrot names
names <- gsub("_"," ",sort(unique(other_data$Species)))

#get Country name
countries <- unique(marked_text$Country)
