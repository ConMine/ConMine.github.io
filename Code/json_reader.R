library(jsonlite)
library(tidyverse)

#load data
data <- read_json("../Data/test.json")
Sp_name <- "cow"

####
# TRAITS
####
get_trait_df <- function(data,Sp_name){
  #setup traits dataframe
  trait_names <- enframe(unlist(data[[1]]$life_history_traits))$name
  non_adult_mass_index <- !grepl("neonate",trait_names) & !grepl("weaning",trait_names)
  trait_names <- trait_names[non_adult_mass_index]
  
  df_traits <- data.frame(matrix(nrow = length(data),ncol = 2 + length(trait_names) ))
  colnames(df_traits) <- c("Species","Database",trait_names)
  
  #add data
  df_traits$Species <- Sp_name #set species name
  df_traits$Database <- names(data) #add databases
  
    
  for(i in 1:length(data)){ #for each database
    source <- enframe(unlist(data[[i]]$life_history_traits))[non_adult_mass_index,]
    for(j in 1:nrow(source)){
      df_traits[[source$name[j]]][i] <- source$value[j]
    }
  }
  
  return(df_traits)
}


####
# THREATS AND CONSERVATION
####
get_t_and_c <- function(data,Sp_name){
  #setup dataframe
  tc_names <- c(enframe(unlist(data[[1]]$conservation))$name,enframe(unlist(data[[1]]$threats))$name)
  
  df_tc <- data.frame(matrix(nrow = length(data),ncol = 2 + length(tc_names) ))
  colnames(df_tc) <- c("Species","Database",tc_names)
  
  #add data
  df_tc$Species <- Sp_name #set species name
  df_tc$Database <- names(data) #add databases
  
  for(i in 1:length(data)){ #for each database
    source <- rbind(enframe(unlist(data[[i]]$threats)),enframe(unlist(data[[i]]$conservation)))
    for(j in 1:nrow(source)){
      df_tc[[source$name[j]]][i] <- source$value[j]
    }
  }
  
  return(df_tc)
}

####
# other data for shiny app
####
get_shiny_data <- function(data,Sp_name){
  #setup dataframe
  shiny_names <- c(enframe(unlist(data[[1]]$taxonomy))$name,
                enframe(unlist(data[[1]]$iucn_status))$name,
                enframe(unlist(data[[1]]$habitat))$name,
                enframe(unlist(data[[1]]$population))$name,
                enframe(unlist(data[[1]]$trade))$name)
  
  df_shiny <- data.frame(matrix(nrow = length(data),ncol = 2 + length(shiny_names) ))
  colnames(df_shiny) <- c("Species","Database",shiny_names)
  
  #add data
  df_shiny$Species <- Sp_name #set species name
  df_shiny$Database <- names(data) #add databases
  
  for(i in 1:length(data)){ #for each database
    
    source <- rbind(enframe(unlist(data[[i]]$taxonomy)),
                  enframe(unlist(data[[i]]$iucn_status)),
                  enframe(unlist(data[[i]]$habitat)),
                  enframe(unlist(data[[i]]$population)),
                  enframe(unlist(data[[i]]$trade)))
    
    for(j in 1:nrow(source)){
      df_shiny[[source$name[j]]][i] <- source$value[j]
    }
  }
  
  return(df_shiny)
}


#Save threats and conservation!


