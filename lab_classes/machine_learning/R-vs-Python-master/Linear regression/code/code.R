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

#' **Document title:** R vs Python - Round 3
#' 
#' **Date:** February 5, 2014
#' 
#' **Author:** Simon Garnier (http://www.theswarmlab.com / @sjmgarnier)
#' 
#' **Description:** This script demonstrate how to perform simple linear
#' regression with R. For more information, see 
#' http://www.theswarmlab.com/r-vs-python-round-3/
#' 
#' Document generated with RStudio ([www.rstudio.com](http://www.rstudio.com)).
#' 

# Load libraries
require("Quandl")         # Functions to access Quandl's database
require("lattice")        # Base graph functions
require("latticeExtra")   # Layer graph functions

# Load data from Quandl
my.data <- Quandl("TPC/HIST_RECEIPT", 
                  start_date = "1945-12-31", 
                  end_date = "2013-12-31")

# The columns' names contain spaces, make them syntactically valid
names(my.data) <- make.names(names(my.data))

# Create graph object
graph <- xyplot(Individual.Income.Taxes ~ Fiscal.Year, 
                data = my.data,
                type = c("g", "b"),
                col = "#00526D")

graph <- graph + xyplot(Corporation.Income.Taxes ~ Fiscal.Year, 
                        data = my.data,
                        type = c("b"),
                        col = "#AD3333")

# Create pretty theme
my.theme <- within(trellis.par.get(), {           
  plot.line <- within(plot.line, {
    lwd <- 3
  })
  
  axis.text <- within(axis.text, {
    cex <- 1.25
  })
  
  par.xlab.text <- within(par.xlab.text, {
    cex <- 1.5
  })
  
  par.ylab.text <- within(par.ylab.text, {
    cex <- 1.5
  })
  
  add.text <- within(add.text, {
    cex <- 1.25
  })
  
  superpose.line <- within(superpose.line, {
    col <- c("#00526D", "#AD3333")
    lwd <- 3
  })
})

# Compute upper and lower limits of the y axes
max.val <- max(my.data$Corporation.Income.Taxes, my.data$Individual.Income.Taxes)
ylim <- c(0 - 0.05 * max.val, max.val * 1.15)

# Prepare a legend
key <- within(list(), {
  text <- c("Individuals", "Corporations")
  corner <- c(0.05, .95)
  lines <- TRUE
  points = FALSE
})

# Update graph object 
graph <- update(graph, 
                xlab = "Fiscal year", ylab = "Income taxes (% of GDP)",
                ylim = ylim,
                par.settings = my.theme,
                auto.key = key)

# Print graph object
print(graph)

# Fit individuals' income taxes data
model.ind <- lm(Individual.Income.Taxes ~ Fiscal.Year, data = my.data)

# Fit corporations' income taxes data
model.corp <- lm(Corporation.Income.Taxes ~ Fiscal.Year, data = my.data)

# Summary statistics for individual income taxes model
summary(model.ind)

# Summary statistics for corporation income taxes model
summary(model.corp)

# Create new dates for model predictions
difference <- as.Date("2013-12-31") - as.Date("1945-12-31")
new.data <- data.frame(Fiscal.Year = seq.Date(from = as.Date("1945-12-31") - 0.1 * difference, 
                                              to = as.Date("2013-12-31") + 0.1 * difference,
                                              by = "years"))

# Compute model predictions (values + confidence intervals) for new dates
# Model of individual income taxes
predict.ind <- within(new.data, {
  Predictions <- as.data.frame(predict(model.ind, 
                                       newdata = new.data,
                                       interval = "confidence"))
})

# Model of corporation income taxes
predict.corp <- within(new.data, {
  Predictions <- as.data.frame(predict(model.corp, 
                                       newdata = new.data,
                                       interval = "confidence"))
})

# Add predicted values for model of individual income taxes 
graph <- graph + xyplot(Predictions$fit ~ Fiscal.Year, 
                        data = predict.ind,
                        type = c("l"),
                        col = "#00526D")

# Add predicted values for model of corporation income taxes 
graph <- graph + xyplot(Predictions$fit ~ Fiscal.Year, 
                        data = predict.corp,
                        type = c("l"),
                        col = "#AD3333")

# Add confidence polygon for model of individual income taxes 
graph <- graph + layer_(lpolygon(x = c(predict.ind$Fiscal.Year, 
                                       rev(predict.ind$Fiscal.Year)),
                                 y = c(predict.ind$Predictions$upr, 
                                       rev(predict.ind$Predictions$lwr)),
                                 col = "#00526D25", 
                                 border = "#00526D75"))

# Add confidence polygon for model of corporation income taxes 
graph <- graph + layer_(lpolygon(x = c(predict.corp$Fiscal.Year, 
                                       rev(predict.corp$Fiscal.Year)),
                                 y = c(predict.corp$Predictions$upr, 
                                       rev(predict.corp$Predictions$lwr)),
                                 col = "#AD333325", 
                                 border = "#AD333375"))

# Reprint graph object
print(graph)
