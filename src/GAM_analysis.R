library(mgcv)
library(sp)
library(sf)
library(dplyr)
library(spdep)
library(lme4)
library(dlnm)
library(boot)
library(lmtest)
library(visreg)
library(CARBayesST)
library(CARBayes)
library(Matrix)

# Check if the county centroids data file exists
if (file.exists("county_centroids_data.rds")) {
  # Load the data from the RDS file
  county_centroids_df <- readRDS("county_centroids_data.rds")
} else {
  # If the file doesn't exist, retrieve the data as before
  county_centroids <- st_centroid(county_data)
  county_centroids_df <- data.frame(
    FIPS = county_data$COUNTYFP,
    Longitude = st_coordinates(st_centroid(county_data))[, 1],
    Latitude = st_coordinates(st_centroid(county_data))[, 2]
  )
  county_centroids_df$FIPS <- paste0(county_data$STATEFP, county_data$COUNTYFP)
  
  # Save the data for future use
  saveRDS(county_centroids_df, file = "county_centroids_data.rds")
}

categories <- c("Retail", "Grocery", "Parks", "Transit", "Workplaces", "Residences")

# Define the more descriptive titles for the categories in the same order
category_titles <- c(
  "Retail & Rec.",
  "Groceries & Pharm.",
  "Parks",
  "Transit Stations",
  "Workplaces",
  "Residences"
)

for (index in seq_along(categories)) {
  category <- categories[index]
  data_file <- paste0("C:/Users/micha/Desktop/Columbia/Research/DATA/Model/Mine/final/data_clean_monthly_", category, "_smooth_^v20.csv")
  fipsdata <- read.csv(data_file, header = TRUE, colClasses = c("FIPS" = "character"))
  fipsdata <- merge(fipsdata, county_centroids_df, by = "FIPS")
  # Subset the data to the period of interest
  period_of_interest <- c(1, 22) # Modify this according to your data
  model_data <- fipsdata[fipsdata$Month >= period_of_interest[1] & fipsdata$Month <= period_of_interest[2], ]

  # Fit the GAM model
  gam_model <- gam(PE ~ s(LogPopulation, k = 3) +
          s(PercentBlack, k = 3) + s(PercentHispanic, k = 3) + s(MedHouseholdIncome, k = 3) +
          s(NewMonthlyCOVIDCases, k = 3) + s(PercentAge60Plus, k = 3) +
          s(PercentAge25PluswoutHSDiploma, k = 3) + s(GovernmentResponseIndexAverage, k = 3) +
          s(MonthlyPrecip, k = 3) + s(AvgMonthlyTemp, k = 3) +
          s(PercWorkersCommuteByTransit, k = 3) + s(PercWorkersWorkFromHome, k = 3) +
          CasesIncreasing +
          te(Latitude, Longitude, Month, k = c(3,3,3)) +
          s(Latitude, Longitude, bs = "tp", k = 3),
          data = model_data, select = TRUE)

  # Print the R² value of the model
  r_squared <- summary(gam_model)$r.sq
  cat("R² for", category_titles[index], ":", r_squared, "\n")
}