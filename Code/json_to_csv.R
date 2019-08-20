#json_to_csv functions
source("json_reader_functions.R")

#get .json directory
json_dir <- commandArgs(trailingOnly = TRUE)[1]

#get list of files
json_files <- list.files(json_dir)
#temp
temp_data <- read_json("../Data/test.json")


traits <- list()
threats <- list()
other <- list()

for(i in 1:length(json_files)){
  Sp_name <- gsub(".json","",json_files[i])
  data <- read_json(paste0(json_dir,json_files)[i])
  traits[[i]] <- get_trait_df(data,Sp_name,temp_data)
  threats[[i]] <- get_t_and_c(data,Sp_name,temp_data)
  other[[i]] <- get_shiny_data(data,Sp_name,temp_data)
  
}


#write dfs
trait_df <- bind_rows(traits)
write_csv(trait_df,"../Data/parrot_csv/parrot_traits.csv")

threats_df <- bind_rows(threats)
write_csv(threats_df,"../Data/parrot_csv/parrot_threatsandconservation.csv")

other_df <- bind_rows(other)
write_csv(other_df,"../Data/parrot_csv/parrot_shiny.csv")
