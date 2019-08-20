# See above for the definitions of ui and server
source("ShinyApp/helpers.R")
source("ShinyApp/ImputationPlots.R")
source("ShinyApp/MapTrade.R")
source("ShinyApp/MapTrade_network.R")
source("ShinyApp/DownloadImage.R")


source("ShinyApp/ConMine_ui.R")
source("ShinyApp/ConMine_server.R")

shinyApp(ui = ui, server = server)
