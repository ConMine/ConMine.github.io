Imputed_data <- read.csv("../Data/imputation/ImputedData.csv")
Imputed_report <- read.csv("../Data/imputation/ImputationReport.csv")

#read in real data
Real_data <- read.csv("../Data/parrot_csv/parrot_traits.csv") %>%
  select(-bodymass.adult_bodymass.value,-bodymass.adult_bodymass.unit,
         -lifespan.value,-lifespan.unit)
Real_data[Real_data == "value"] <- NA
Real_data[Real_data == "unit"] <- NA

Real_data_values <- Real_data %>% na.omit() %>%
  gather("key","value",-Species,-Database) %>%
  filter(value != "NaN") %>%
  filter(!grepl(".unit",key))

#functions to plot imputed data
#Lifespan
  plot_imputation <- function(X,ImputedValues,ImputationReport,trait){
    
    TempData = ImputedValues[ImputedValues$Species == X,]
    FamilyGroup = TempData$Family
    if(trait == "Life span"){
    if(grepl("Imputed",TempData$LifespanStatus)){
      MeanLine = round(10^TempData$Lifespan_Years)
      LowerCI = round(10^TempData$LowerCI_Lifespan_Years)
      UpperCI = round(10^TempData$UpperCI_Lifespan_Years)
      ggplot(ImputedValues[ImputedValues$Family == FamilyGroup,]) +
        geom_density(aes(x = 10^(Lifespan_Years)), fill = "light grey") +
        geom_vline(xintercept = MeanLine, colour = "red", linetype = "dotted", size = 2) +
        geom_vline(xintercept = LowerCI, colour = "red", size = 0.1) +
        geom_vline(xintercept = UpperCI, colour = "red", size = 0.1) +
        annotate("rect", xmin = LowerCI, xmax = UpperCI, ymin = 0, ymax = Inf, fill = "red", alpha = 0.1) +
        scale_y_continuous(expand = c(0, 0)) +
        labs(x = "Lifespan(years)", 
             title = paste("Predicted lifespan (95% confidence intervals): ", MeanLine, " (", LowerCI, ", ", UpperCI,") years", sep = ""),
             subtitle = paste("Family: ", FamilyGroup, sep = ""),
             caption = paste("Values are derived from imputation. Warnings: ", ImputationReport$MissingWarning[1], "; ", ImputationReport$PhyloBias, "; ", ImputationReport$TraiBias, ".", sep = "")) +
        theme_classic() +
        theme(plot.caption=element_text(face="bold", color="dark red"))
    } else {
      MeanLine = round(10^TempData$Lifespan_Years)
      ggplot(ImputedValues[ImputedValues$Family == FamilyGroup,]) +
        geom_density(aes(x = 10^(Lifespan_Years)), fill = "light grey") +
        geom_vline(xintercept = MeanLine, colour = "red", linetype = "dotted", size = 2) +
        scale_y_continuous(expand = c(0, 0)) +
        labs(x = "Lifespan(years)", 
             title = paste("Lifespan:", MeanLine, "years"),
             subtitle = paste("Family: ", FamilyGroup, sep = "")) +
        theme_classic()
    }
    } else if (trait == "Body size"){
      if(grepl("Imputed",TempData$BodymassStatus)){
        MeanLine = round(10^TempData$Bodymass_g)
        LowerCI = round(10^TempData$LowerCI_Bodymass_g)
        UpperCI = round(10^TempData$UpperCI_Bodymass_g)
        ggplot(ImputedValues[ImputedValues$Family == FamilyGroup,]) +
          geom_density(aes(x = 10^(Bodymass_g)), fill = "light grey") +
          geom_vline(xintercept = MeanLine, colour = "red", linetype = "dotted", size = 2) +
          geom_vline(xintercept = LowerCI, colour = "red", size = 0.1) +
          geom_vline(xintercept = UpperCI, colour = "red", size = 0.1) +
          annotate("rect", xmin = LowerCI, xmax = UpperCI, ymin = 0, ymax = Inf, fill = "red", alpha = 0.1) +
          scale_y_continuous(expand = c(0, 0)) +
          labs(x = "Body mass(grams)", 
               title = paste("Predicted body mass (95% confidence intervals): ", MeanLine, " (", LowerCI, ", ", UpperCI,") grams", sep = ""),
               subtitle = paste("Family: ", FamilyGroup, sep = ""),
               caption = paste("Values are derived from imputation. Warnings: ", ImputationReport$MissingWarning[1], "; ", ImputationReport$PhyloBias, "; ", ImputationReport$TraiBias, ".", sep = "")) +
          theme_classic() +
          theme(plot.caption=element_text(face="bold", color="dark red"))
      }
      else {
        MeanLine = round(10^TempData$Bodymass_g)
        ggplot(ImputedValues[ImputedValues$Family == FamilyGroup,]) +
          geom_density(aes(x = 10^(Bodymass_g)), fill = "light grey") +
          geom_vline(xintercept = MeanLine, colour = "red", linetype = "dotted", size = 2) +
          scale_y_continuous(expand = c(0, 0)) +
          labs(x = "Body mass(grams)", 
               title = paste("Body mass:", MeanLine, "grams"),
               subtitle = paste("Family: ", FamilyGroup, sep = "")) +
          theme_classic()
      } 
    }
  }

  