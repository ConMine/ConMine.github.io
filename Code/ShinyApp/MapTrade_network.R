require(maps)

country_centroids <- read.csv("../Data/parrot_csv/country_centroids.csv")
cites_full <- read.csv("../Data/parrot_csv/parrot_cites_full.csv")

tradeflow <- function(species,year){
  
  ##Loading and wrangling data
  ##Country centroids
  country_centroids[,1] <- NULL
  centroids <- dplyr::filter(country_centroids, !iso2 == "-99")
  
  ##Trade data
  cites_full[is.na(cites_full)] <- 0
  rawdata <- subset(cites_full, Taxon==species)
  rawdata$weighting <- rawdata$Importer.reported.quantity+rawdata$Exporter.reported.quantity
  
  #Subsetting data
  trade <- dplyr::select(rawdata, Importer, Exporter, weighting, Year, Taxon)
  sumtrade <- aggregate(trade$weighting, by=list(from=trade$Exporter, to=trade$Importer, Year=trade$Year, Taxon=trade$Taxon), FUN=sum)
  #weighting = total import and export quantity
  colnames(sumtrade) <- c("from", "to", "Year", "taxon", "weighting")
  
  ##Checking equivalent country levels
  combine <- dplyr::left_join(sumtrade, centroids, by = c("from"="iso2"))
  combine2 <- dplyr::left_join(combine, centroids, by = c("to"="iso2"))
  
  combsumtrade <- dplyr::select(combine2, from, to, weighting, Year, taxon)
  newcentroids <- dplyr::select(combine2, from, Longitude.x, Latitude.x)
  newcentroids <- unique(newcentroids)
  colnames(newcentroids) <- c("country", "Lat", "Long")
  
  newsumtrade <- data.frame()
  for(i in levels(as.factor(combsumtrade$from))){
    temp <- dplyr::filter(combsumtrade, to==i)
    newsumtrade<- rbind(newsumtrade, temp)
  }
  
  ##------------------------------------------------------------------##
  
  ###Plotting 
  
  ##Subsetting based on year
  newsumtrade <- subset(newsumtrade, Year== year)
  
  ##Plotting on map
  map("world", col="grey20", fill=TRUE, bg="black", lwd=0.1)
  
  ##Add points of each country centroid
  points(x=newcentroids$Lat, y=newcentroids$Long, col="orange")
  
  ##Colour spectrum
  col.1 <- adjustcolor("orange red", alpha=0.4)
  col.2 <- adjustcolor("orange", alpha=0.4)
  edge.pal <- colorRampPalette(c(col.1, col.2), alpha = TRUE)
  edge.col <- edge.pal(100)
  
  ##Logging weight to make more readable
  newsumtrade$logweight <- log(newsumtrade$weighting)
  
  ##Drawing arrows based on trade between countries
  newcentroids <- na.omit(newcentroids)
  for(i in 1:nrow(newsumtrade)){
    
    node1 <- newcentroids[newcentroids$country == newsumtrade[i,]$from,]
    node2 <- newcentroids[newcentroids$country == newsumtrade[i,]$to,]
    
    #Removing NA values
    if(is.na(node1[1,]) || is.na(node2[1,])){
      next
    }
    
    #Weighting arrow width by trade
    edge.ind <- newsumtrade[i,]$logweight+1
    
    arrows(node1[1,]$Lat, node1[1,]$Long, node2[1,]$Lat, node2[1,]$Long,
           lwd=edge.ind, angle=30, code=3, col = edge.col[edge.ind])
  }
  
  ##Adding legend
  legend("bottomleft", legend="Arrow width = Logarithm of Total Trade + 1",
         bg="black", text.col="orange", text.width=8, col="orange")
  
}

