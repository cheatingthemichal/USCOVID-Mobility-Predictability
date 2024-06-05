library(mgcv)
library(ggplot2)
library(gridExtra)

axis_labels <- c(
    LogPopulation = "log(Population)",
    GovernmentResponseIndexAverage = "Government Response Index",
    MonthlyPrecip = "Total daily precipitation (mm)",
    AvgMonthlyTemp = "Mean Daily Temperature (°C)")

all_variables <- c(
    "LogPopulation",
    "PercentBlack",
    "PercentHispanic",
    "MedHouseholdIncome",
    "NewMonthlyCOVIDCases",
    "PercentAge60Plus",
    "PercentAge25PluswoutHSDiploma",
    "GovernmentResponseIndexAverage",
    "MonthlyPrecip",
    "AvgMonthlyTemp",
    "PercWorkersCommuteByTransit",
    "PercWorkersWorkFromHome",
    "CasesIncreasing")

variable_indices <- c(1, 8, 9, 10, 13)

formatted_variable_names <- c(
    "Log Population",
    "Government Response",
    "Monthly Precipitation",
    "Avg Monthly Temp",
    "Cases Increasing")

categories <- c(
    "Retail_and_Recreation",
    "Grocery_and_Pharmacy",
    "Parks",
    "Transit_Stations",
    "Workplaces",
    "Residences")

category_titles <- c(
    Grocery_and_Pharmacy = "Groceries & Pharmacy",
    Retail_and_Recreation = "Retail & Recreation",
    Transit_Stations = "Transit Stations",
    Residences = "Residences",
    Workplaces = "Workplaces",
    Parks = "Parks")

color_palettes <- list(
    Grocery_and_Pharmacy = "tomato4",
    Retail_and_Recreation = "black",
    Transit_Stations = "darkmagenta",
    Residences = "midnightblue",
    Workplaces = "darkred",
    Parks = "darkgreen")

color_palettes_light <- list(
    Grocery_and_Pharmacy = "salmon",
    Retail_and_Recreation = "azure4",
    Transit_Stations = "orchid",
    Residences = "lightslateblue",
    Workplaces = "indianred",
    Parks = "green"
)

county_centroids_df <- readRDS("./data/raw_data/county_centroids_data.rds")

gam_models <- list()

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

    gam_models[[category]] <- gam(Pred ~ s(LogPopulation, k = 3) +
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
}

theme_set(theme_light(base_size = 36))

# Initialize a list to store the ggplot objects
plots_list <- list()

# Define a blank plot to use for spacing
blank_plot <- ggplot() + theme_void()

row_labels <- setNames(lapply(formatted_variable_names, function(label) {
  ggplot() +
    annotate("text",
        x = 0, y = 0,
        label = label, size = 14,
        angle = 90, hjust = 0.5,
        vjust = 0.5) +
    theme_void() +
    theme(plot.margin = margin(0, 0, 0, 0))
}), formatted_variable_names)

# Loop over the variables and categories to create the plots
for (i in variable_indices) {
    for (j in seq_along(categories)) {
        category <- categories[j]
        variable_name <- all_variables[i]
        x_axis_label <- axis_labels[variable_name]
        color_palette <- color_palettes[[category]]
        color_palette_light <- color_palettes_light[[category]]

        if (variable_name == "CasesIncreasing") {
            model_summary <- summary(gam_models[[category]])

            coef_est <- model_summary$p.table["CasesIncreasing", "Estimate"]
            std_error <- model_summary$p.table["CasesIncreasing", "Std. Error"]

            ci_lower <- coef_est - 1.96 * std_error
            ci_upper <- coef_est + 1.96 * std_error

            effect_df <- data.frame(
                slope = coef_est,
                ci_lower = ci_lower,
                ci_upper = ci_upper)

            p <- ggplot(
                effect_df,
                aes(x = factor(1), y = slope)) +
                geom_hline(
                    yintercept = 0,
                    linetype = "solid",
                    color = color_palette,
                    size = 1.5) +
                geom_bar(
                    stat = "identity",
                    position = position_dodge(),
                    width = 0.5,
                    fill = color_palette) +
                geom_errorbar(
                    aes(ymin = ci_lower, ymax = ci_upper),
                    width = 0.3,
                    color = color_palette_light,
                    size = 2.5) +
                labs(x = "", y = "") +
                ylim(-0.04, 0.04) +
                theme_minimal() +
                theme(
                    axis.text.x = element_blank(),
                    axis.ticks.x = element_blank(),
                    axis.text.y = element_text(size = 28),
                    axis.line = element_line(),
                    plot.margin = margin(0.3, 0.3, -0.3, -0.3, "cm"),
                    panel.background = element_rect(
                        fill = "white",
                        color = "black"),
                    plot.background = element_rect(
                        fill = "white",
                        color = "black"),
                    panel.spacing = unit(0, "lines")
                )
        # Add y-axis label for first column
        if (j == 1) {
            p <- p +
                labs(y = "Slope", size = 28) +
                theme(axis.title.y = element_text(size = 28)) +
                theme(plot.margin = margin(0.3, 0.3, -0.3, 0.3, "cm"))
        }
        # Plot non-binary variables
        } else {
            partial_effect <- mgcv::plot.gam(
                gam_models[[category]],
                select = i,
                se = TRUE,
                all.terms = TRUE,
                residuals = TRUE)

            effect_df <- data.frame(x = partial_effect[[i]]$x,
                y = partial_effect[[i]]$fit,
                ymin = partial_effect[[i]]$fit -
                    (1.96 * partial_effect[[i]]$se),
                ymax = partial_effect[[i]]$fit +
                    (1.96 * partial_effect[[i]]$se))

            p <- ggplot(effect_df, aes(x = x, y = y)) +
                geom_ribbon(
                    aes(ymin = ymin, ymax = ymax),
                    fill = color_palette,
                    alpha = 0.2) +
                geom_line(color = color_palette, size = 1.5) +
                labs(x = x_axis_label, y = "") +
                theme_minimal() +
                theme(
                    plot.title = element_text(hjust = 0.5),
                    axis.text.x = element_text(angle = 0,
                        vjust = 0.5,
                        size = 28),
                    axis.text.y = element_text(size = 28),
                    axis.ticks = element_line(),
                    panel.grid = element_blank(),
                    axis.line = element_line(color = "black"),
                    plot.margin = margin(0.3, 0.3, 0.3, -0.3, "cm"),
                    panel.background = element_rect(fill = "white",
                        color = "black"),
                    plot.background = element_rect(fill = "white",
                        color = "black"),
                    panel.spacing = unit(0, "lines"),
                    axis.title.x = element_text(size = 28)
                )
            #Add titles for first row
            if (i == 1) {
                p <- p +
                    ggtitle(category_titles[category]) +
                    theme(plot.title = element_text(size = 36))
            }
            #Add y-axis label for first column
            if (j == 1) {
                p <- p +
                    labs(y = "Partial Residual") +
                    theme(axis.title.y = element_text(size = 28)) +
                    theme(plot.margin = margin(0.3, 0.3, 0.3, 0.3, "cm"))
            }
        }
        plots_list[[paste0(i, "_", category)]] <- p
    }
}

# Now we prepare a matrix indicating the layout of our plots
# First, create an empty matrix of the correct size
layout_matrix <- matrix(
    ncol = length(categories) + 1,
    nrow = length(variable_indices))

# Fill the first column with row labels
layout_matrix[, 1] <- seq_along(formatted_variable_names)

# Fill the rest with the plot indices
plot_indices <- length(formatted_variable_names) + 1
for (i in seq_along(variable_indices)) {
    layout_matrix[i, -1] <- plot_indices:(
        plot_indices + length(categories) - 1)
    plot_indices <- plot_indices + length(categories)
}

grobs <- c(row_labels, plots_list)

widths <- c(
    unit(0.2, "lines"),
    rep(unit(1, "null"),
    length(categories)))

# Arrange the plots and labels according to the layout matrix
plot_grid <- gridExtra::grid.arrange(
    grobs = grobs,
    layout_matrix = layout_matrix,
    widths = widths)
    
pdf(NULL)
ggsave(filename = "./results/figures/Figure6.png",
    plot = plot_grid, width = 40, height = 30, dpi = 300)