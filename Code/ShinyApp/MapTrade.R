#Load packages
library(rworldmap)
library(countrycode)

#Read data
worldwide_cites = read.csv("../Data/parrot_csv/parrot_cites_summary.csv")


get_year_range <- function(species){
  TrimData <- worldwide_cites %>%
    filter(Taxon == species)

  if(nrow(TrimData) > 0){
    MinYear = as.numeric(min(TrimData$Year))
    MaxYear = as.numeric(max(TrimData$Year))
    return(sort(c(MinYear,MaxYear)))
  } else {
    return(NA)
  }
  
}

plot_trademap <- function(species,country,year){
  #trim by species
  TrimData = as.data.frame(worldwide_cites[worldwide_cites$Taxon == species,])
  #trim by date
  Trim2Data = TrimData[TrimData$Year == year,]
  MaxExports = as.numeric(max(TrimData$ExportSum))
  
  #add to maps
  matched <- joinCountryData2Map(Trim2Data, joinCode="ISO2", nameJoinColumn="Country")
  #plot
  mapCountryData(matched, nameColumnToPlot="ExportSum",
                 mapTitle= paste("Global exports of ",
                 species, " in ", year, sep = ""), catMethod = c(0:MaxExports),
                 colourPalette = "heat")
}

plot_trademap_time <- function(species){
  x <- worldwide_cites %>%
    filter(Taxon == species) %>%
    mutate(Country = countrycode(Country,"iso2c","country.name")) %>%
    group_by(Year) %>% mutate(Total = sum(ExportSum)) %>%
    ggplot(aes(x = Year, y = ExportSum, group = Country , colour = Country))+
    geom_point()+geom_line()+
    geom_point(aes(y = Total, group = NULL), colour = "black")+
    geom_line(aes(y = Total, group = NULL), colour = "black")+
    theme_bw()
  
  return(x)
}

