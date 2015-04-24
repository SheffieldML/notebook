#' Copyright 2014 Simon Garnier (http://www.theswarmlab.com / @sjmgarnier)
#' 
#' This script is free software: you can redistribute it and/or modify it under
#' the terms of the GNU General Public License as published by the Free Software
#' Foundation, either version 3 of the License, or (at your option) any later
#' version.
#' 
#' This script is distributed in the hope that it will be useful, but WITHOUT
#' ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#' FOR A PARTICULAR PURPOSE.
#' 
#' See the GNU General Public License for more details.
#' 
#' You should have received a copy of the GNU General Public License along with
#' this script. If not, see http://www.gnu.org/licenses/.
#' 

#' **Document title:** R vs Python - Round 1
#' 
#' **Date:** January 5, 2014
#' 
#' **Author:** Simon Garnier (http://www.theswarmlab.com / @sjmgarnier)
#' 
#' **Description:** This script generates a pretty barchart representing the top
#' 25 most violent movies ordered by number of on screen deaths per minute. For
#' more information, see http://www.theswarmlab.com/r-vs-python-round-1/
#' 
#' Document generated with RStudio ([www.rstudio.com](http://www.rstudio.com)).
#' 

# Load libraries
library(lattice)        # Very versatile graphics package
library(latticeExtra)   # Addition to "lattice" that makes layering graphs a 
                        # breathe, and I'm a lazy person, so why not

# Load data into a data frame
body.count.data <- within(read.csv("http://files.figshare.com/1332945/film_death_counts.csv"), {
  
  # Compute on screen deaths per minute for each movie. 
  Deaths_Per_Minute <- Body_Count / Length_Minutes
  ord <- order(Deaths_Per_Minute, decreasing = TRUE)  # useful later
  
  # Combine film title and release date into a new factor column with levels
  # ordered by ascending violence
  Full_Title <- paste0(Film, " (", Year, ")")
  Full_Title <- ordered(Full_Title, levels = rev(unique(Full_Title[ord])))
  
  # Combine number of on screen death per minute and duration of the movies into
  # a new character string column
  Deaths_Per_Minute_With_Length <- paste0(round(Deaths_Per_Minute, digits=2), " (", Length_Minutes, " mins)")
  
})

# Reorder "body.count.data" by (descending) number of on screen deaths per minute
body.count.data <- body.count.data[body.count.data$ord, ]

# Select top 25 most violent movies by number of on screen deaths per minute
body.count.data <- body.count.data[1:25,]

# Generate base graph
graph <- barchart(Full_Title ~ Deaths_Per_Minute, data = body.count.data)
graphics.off()
dev.new(width = 10, height = 8)
print(graph)

# Create theme
my.bloody.theme <- within(trellis.par.get(), {    # Initialize theme with default value
  axis.line$col <- NA                             # Remove axes 
  plot.polygon <- within(plot.polygon, {
    col <- "#8A0606"                              # Set bar colors to a nice bloody red
    border <- NA                                  # Remove bars' outline
  })
  axis.text$cex <- 1                              # Default axis text size is a bit small. Make it bigger
  layout.heights <- within(layout.heights, {
    bottom.padding <- 0                           # Remove bottom padding
    axis.bottom <- 0                              # Remove axis padding at the bottom of the graph
    axis.top <- 0                                 # Remove axis padding at the top of the graph
  })
})

# Update figure with new theme + other improvements (like a title for instance)
graph <- update(
  graph, 
  main  ="25 most violence packed films by deaths per minute",  # Title of the barchart
  par.settings = my.bloody.theme,                               # Use custom theme
  xlab = NULL,                                                  # Remove label of x axis
  scales = list(x = list(at = NULL)),                           # Remove rest of x axis
  xlim = c(0, 6.7),                                             # Set graph limits along x axis to accomodate the additional text (requires some trial and error)
  box.width = 0.75)                                               # Default bar width is a bit small. Make it bigger)

print(graph)

# Add number of on screen deaths per minute and duration of movies at the end of each bar 
graph <- graph + layer(with(body.count.data, 
  panel.text(
    Deaths_Per_Minute,                # x position of the text
    25:1,                             # y position of the text
    pos = 4,                          # Position of the text relative to the x and y position (4 = to the right)
    Deaths_Per_Minute_With_Length)))  # Text to display                                     

# Print graph
print(graph)

# Load additional libraries
library(jpeg)  # To read JPG images
library(grid)  # Graphics library with better image plotting capabilities

# Download a pretty background image; mode is set to "wb" because it seems that
# Windows needs it. I don't use Windows, I can't confirm
download.file(url = "http://www.theswarmlab.com/wp-content/uploads/2014/01/bloody_gun.jpg", 
              destfile = "bloody_gun.jpg", quiet = TRUE, mode = "wb")

# Load gun image using "readJPEG" from the "jpeg" package
img <- readJPEG("bloody_gun.jpg")

# Add image to graph using "grid.raster" from the "grid" package
graph <- graph + layer_(
  grid.raster(
    as.raster(img),                 # Image as a raster
    x = 1,                          # x location of image "Normalised Parent Coordinates"
    y = 0,                          # y location of image "Normalised Parent Coordinates"
    height = 0.7,                   # Height of the image. 1 indicates that the image height is equal to the graph height
    just = c("right", "bottom")))   # Justification of the image relative to its x and y locations

# Print graph
print(graph)
