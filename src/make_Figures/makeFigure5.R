library(ggplot2)
library(maps)
library(dplyr)
library(ggthemes)
library(RColorBrewer)
library(socviz)
library(stringr)
library(gridExtra)

make_graph <- function(files_path, categories, saveloc, category_ranges) {
    my_colors <- rev(brewer.pal(6, "Spectral"))
    color_settings <- theme_map() +
        theme(legend.title = element_text(size = rel(1),
            color = "black"),
        legend.text = element_text(size = rel(1)),
        plot.title = element_text(color = "black",
            size = rel(1.5)),
        strip.text = element_text(size = rel(1.3)),
        text = element_text(size = 28),
        legend.key.size = unit(1, "lines"),
        legend.position = c(-0.07, -0.07),
        plot.margin = unit(c(1, 1, 1, 4), "lines"))

    plots <- list()  # Initialize an empty list to store the plots

    # Define a function to format category names for titles
    format_category_for_title <- function(category) {
        category <- str_replace_all(category, "([A-Z])", " \\1")
        category <- str_replace_all(category, " And ", " and ")
        return(category)
    }

    # Loop over categories
    for (category in categories) {
        # Filename uses the category directly
        filename <- paste0(files_path, "average_", category, ".csv")

        # Load data
        alpha_data <- read.csv(filename,
            header = TRUE,
            sep = ",",
            colClasses = c("character", "numeric"))
        alpha_data <- rename(alpha_data, id = "FIPS")

        # Apply category specific range
        range_vals <- category_ranges[[category]]
        alpha_data$AveragePercentChange <- pmin(pmax(
            alpha_data$AveragePercentChange,
            range_vals[1]),
            range_vals[2])

        # Join with county_map
        county_full <- inner_join(county_map,
            alpha_data,
            by = "id")

        # Create plot with updated color settings
        plot <- ggplot(data = county_full,
            mapping = aes(x = long,
                y = lat,
                fill = AveragePercentChange,
                group = group)) +
            geom_polygon(color = "white",
                size = 0.1) +
            coord_equal() +
            scale_fill_gradientn(colors = my_colors,
                breaks = seq(
                    range_vals[1],
                    range_vals[2],
                    length.out = length(my_colors)),
            labels = paste0(seq(
                range_vals[1],
                range_vals[2],
                length.out = length(my_colors))),
            limits = c(range_vals[1],
                range_vals[2]),
            name = "Predictability") +
            guides(fill = guide_legend(
                keywidth = 0.5,
                keyheight = 0.5)) +
            color_settings +
            labs(title = format_category_for_title(category))
        plots[[category]] <- plot
    }

    # Arrange all plots in a 2x3 grid
    combined_plot <- grid.arrange(grobs = plots, ncol = 3, nrow = 2)

    pdf(NULL)
    # Save the combined plot as PNG
    ggsave(paste0(saveloc, "Figure5.png"),
           plot = combined_plot,
           device = "png",
           width = 32, height = 18, dpi = 300)
}

categories <- c(
    "RetailAndRecreation",
    "GroceriesAndPharmacies",
    "Parks",
    "TransitStations",
    "Workplaces",
    "Residences")

# Define the ranges for each category
category_ranges <- list(
    "RetailAndRecreation" = c(0.25, 0.75),
    "GroceriesAndPharmacies" = c(0.3, 0.75),
    "Parks" = c(0.35, 0.65),
    "TransitStations" = c(0.35, 0.75),
    "Workplaces" = c(0.5, 0.85),
    "Residences" = c(0.65, 0.85)
)

data("county_map")
make_graph("./data/intermediate_data/",
           categories,
           "./results/figures/",
           category_ranges)