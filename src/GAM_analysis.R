library(mgcv)
library(sf)
library(dplyr)

county_centroids_df <- readRDS("./data/raw_data/county_centroids_data.rds")

categories <- c(
    "Retail_and_Recreation",
    "Grocery_and_Pharmacy",
    "Parks",
    "Transit_Stations",
    "Workplaces",
    "Residences")

output_file <- "./results/gam_summaries.txt"
sink(output_file)

for (index in seq_along(categories)) {
    category <- categories[index]
    data_file <- paste0(
        "./data/data_for_GAM/",
        category,
        "_table_for_GAM.csv")
    fipsdata <- read.csv(
        data_file,
        header = TRUE,
        colClasses = c("FIPS" = "character"))
    fipsdata <- merge(
        fipsdata,
        county_centroids_df,
        by = "FIPS")
    period_of_interest <- c(1, 22)
    model_data <- fipsdata[fipsdata$Month >= period_of_interest[1] &
        fipsdata$Month <= period_of_interest[2], ]

    gam_model <- gam(PE ~ s(LogPopulation, k = 3) +
        s(PercentBlack, k = 3) +
        s(PercentHispanic, k = 3) +
        s(MedHouseholdIncome, k = 3) +
        s(NewMonthlyCOVIDCases, k = 3) +
        s(PercentAge60Plus, k = 3) +
        s(PercentAge25PluswoutHSDiploma, k = 3) +
        s(GovernmentResponseIndexAverage, k = 3) +
        s(MonthlyPrecip, k = 3) +
        s(AvgMonthlyTemp, k = 3) +
        s(PercWorkersCommuteByTransit, k = 3) +
        s(PercWorkersWorkFromHome, k = 3) +
        CasesIncreasing +
        te(Latitude, Longitude, Month, k = c(3, 3, 3)) +
        s(Latitude, Longitude, bs = "tp", k = 3),
        data = model_data, select = TRUE)

    cat("\n=================================================\n")
    cat("Category:", category, "\n")
    cat("=================================================\n\n")
    print(summary(gam_model))
    cat("\n\n")
}

sink()