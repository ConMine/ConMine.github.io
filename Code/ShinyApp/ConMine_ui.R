# Define UI for app that draws a histogram ----
ui <- fluidPage(
  titlePanel("ConMine"),
  sidebarLayout(sidebarPanel(selectInput(inputId = "Species_Choice",
                                         label = "Choose a species:",
                                         choices = names),
                             
                             selectInput(inputId = "Country_Choice",
                                         label = "Choose a country:",
                                         choices = countries)),
                
mainPanel(tabsetPanel(type = "tabs",
#welcome
tabPanel("Welcome",
         h1("Welcome to ConMine!"),br(),
         p("ConMine is a dashboard created to assist in the reporting of Non-Detrimental Findings (NDFs). It uses data collected from IUCN, CITES, EOL, and ANAGE to help you plot and understand the trade of a specific species."),br(),
         p("To use the app please select a species and/or country from the drop down column on the left:"), br(),
         p("For help/support please email:")),

#Species Tab  
tabPanel("Species Information",
         fluidRow(column(6,
                  h1(textOutput("species_name")),
                  h4(textOutput("synonym")),br(),br(),
                  h3("Taxanomic Notes"), htmlOutput("taxa_notes"),br(),br(),
                  h3("Range Notes"), htmlOutput("range_notes"),br(),br()),
                  column(4,htmlOutput("picture"),br(),
                  tableOutput("redlist")
                  )
                  )
         ),

#Trait Tab 
tabPanel("Traits",
 tabsetPanel(type = "tabs",
  tabPanel("Real Data"),
  tabPanel("Imputed Data",
   selectInput(inputId = "imputed_trait",
    label = "Choose a imputed trait:",
     choices = c("Life span","Body size")),
   plotOutput("Imputed_Plot")))),

#Threats and Consservation
tabPanel("Threats and Conservation",
         h3("Red List Notes"), htmlOutput("redlist_notes"),br(),br(),
         h3("Population Notes"), htmlOutput("population_notes"),br(),br(),
         h3("Conservation Notes"), htmlOutput("conservation_notes") 
         ),

#Trade
tabPanel("Trade",
         h3("Trade Notes"), htmlOutput("trade_notes"),br(),br(),
         plotOutput("Trade_Plot"),
         uiOutput("year_slider"),
         br(),br(),
         plotOutput("Trade_timeseries"),
         plotOutput("Trade_Network")
         )
      )                                 
    )             
  )
)
