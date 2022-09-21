######################################################################
#
# Quebec emergency rooms - current occupancy rates
#
######################################################################


library(shiny)
library(leaflet)
library(dplyr)
library(stringr)

df_map <- read.csv("https://github.com/jlomako/quebec-emergency-rooms/raw/main/data/coordinates.csv")

# get hourly data:
 url <- "https://www.msss.gouv.qc.ca/professionnels/statistiques/documents/urgences/Releve_horaire_urgences_7jours.csv"
# using local copy for now
# url <- "Releve_horaire_urgences_7jours.csv"
df <- read.csv(url, encoding = "latin1") # using read.csv here because vroom can't handle french characters

# get last update
update <- as.Date(df$Mise_a_jour[1])
update_time <- df$Heure_de_l.extraction_.image.[1]
update_txt <- paste("\nlast update:", update, "at", update_time)

# get hospital data and calculate occupancy_rate
df <- df %>%
  select(etab = Nom_etablissement, hospital_name = Nom_installation, beds_total = Nombre_de_civieres_fonctionnelles, beds_occ = Nombre_de_civieres_occupees) %>%
  mutate(beds_total = suppressWarnings(as.numeric(beds_total)), beds_occ = suppressWarnings(as.numeric(beds_occ))) %>%
  mutate(occupancy_rate = round(100*(beds_occ/beds_total)), Date = update) %>%
  select(Date, etab, hospital_name, beds_occ, beds_total, occupancy_rate)

# some name changes
df$hospital_name <- str_replace(df$hospital_name, "L'Hôpital général Juif Sir Mortimer B. Davis", "Hôpital général Juif Sir Mortimer B. Davis")
df$hospital_name <- str_replace(df$hospital_name, "Hôpital, CLSC et Centre d'hébergement de Roberval", "Roberval Hôpital")
df$hospital_name <- str_replace(df$hospital_name, "Centre multiservices de santé et services sociaux Christ-Roi", "Centre Christ-Roi")
df$hospital_name <- str_replace(df$hospital_name, "Hôpital, CLSC et Centre d'hébergement d'Asbestos", "Hôpital d'Asbestos")


# left join with coordinates data
df <- df %>% 
  left_join(df_map, by = c("hospital_name")) 

  
# colors for circles on map
pal_red <- colorNumeric(palette = "YlOrRd", domain = df$occupancy_rate) # "YlOrRd"
pal_green <- colorNumeric(palette = "RdYlGn", reverse=T, domain = df$occupancy_rate)
  

# shiny app
ui <- bootstrapPage(
  
  # uses bootstrap 5
  theme = bslib::bs_theme(version = 5, bootswatch = "minty"),
  
  div(class="container-fluid text-center py-3",
    h1("Occupancy rates in Quebec emergency rooms"),
    div(leafletOutput("map")),
    div(htmlOutput("update"))
    
  ) # close container
  
  
) # close ui


server <- function(input, output) { 
  
  output$map <- renderLeaflet({
    leaflet(df) %>% addProviderTiles(providers$CartoDB.Voyager) %>% # providers$OpenStreetMap, CartoDB.Voyager
      addCircleMarkers(lng = ~Long, lat = ~Lat, 
                       label = ~paste(hospital_name, ":", occupancy_rate, "%"), 
                       color = ~ifelse(occupancy_rate >= 89, pal_red(occupancy_rate), pal_green(occupancy_rate)),
                       fillOpacity = 0.8,
                       stroke = FALSE
                       ) %>%
      setView(lng = -73.57827, lat = 45.49694, zoom = 10)
  } # close renderLeaflet
  ) # close map
  
  # plot last update & time
  output$update <- renderUI({update_txt})
  
} # close server

shinyApp(ui, server)
