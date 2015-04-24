#+ licence, echo=FALSE 
# Copyright 2014 Simon Garnier (http://www.theswarmlab.com / @sjmgarnier)
# 
# This script is free software: you can redistribute it and/or modify it under 
# the terms of the GNU General Public License as published by the Free Software 
# Foundation, either version 3 of the License, or (at your option) any later 
# version.
# 
# This script is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.
# 
# See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along with 
# this script. If not, see http://www.gnu.org/licenses/.
# 
# You can generate the HTML files by running: 
# library(knitr) 
# spin("notebook2.R") 
# pandoc("notebook2.md", config = "pandoc_config2.txt")


#+ 
#' **Document title:** R vs Python - Round 2 (2/2)
#' 
#' **Date:** February 2, 2014
#' 
#' **Text by:** Simon Garnier ([www.theswarmlab.com](http://www.theswarmlab.com)
#' / [\@sjmgarnier](http://twitter.com/sjmgarnier))
#' 
#' **R code by:** Simon Garnier
#' ([www.theswarmlab.com](http://www.theswarmlab.com) /
#' [\@sjmgarnier](http://twitter.com/sjmgarnier))
#' 
#' **Python code by:** Randy Olson
#' ([www.randalolson.com](http://www.randalolson.com) /
#' [\@randal_olson](http://twitter.com/randal_olson))
#' 
#' Document generated with RStudio ([www.rstudio.com](http://www.rstudio.com)), 
#' knitr ([www.yihui.name/knitr/](http://yihui.name/knitr/)) and pandoc 
#' ([www.johnmacfarlane.net/pandoc/](http://johnmacfarlane.net/pandoc/)). Python
#' figures generated with iPython Notebook
#' ([www.ipython.org/notebook.html](http://ipython.org/notebook.html)).
#' 


#' ___
#' 
#' #### Foreword ####
#' 
#' My friend Randy Olson and I got into the habit to argue about the relative 
#' qualities of our favorite languages for data analysis and visualization. I am
#' an enthusiastic R user ([www.r-project.org](http://www.r-project.org)) while 
#' Randy is a fan of Python ([www.python.org](http://www.python.org)). One thing
#' we agree on however is that our discussions are meaningless unless we
#' actually put R and Python to a series of tests to showcase their relative
#' strengths and weaknesses. Essentially we will set a common goal (*e.g.*,
#' perform a particular type of data analysis or draw a particular type of
#' graph) and create the R and Python codes to achieve this goal. And since
#' Randy and I are all about sharing, open source and open access, we decided to
#' make public the results of our friendly challenges so that you can help us
#' decide between R and Python and, hopefully, also learn something along the
#' way.
#' 


#' ___
#' 
#' #### Today's challenge: a data thief manual for honest scientists (Part 2 of 2) ####
#' 
#' ##### 1 - Introduction #####
#' 
#' [Last time](http://www.theswarmlab.com/r-vs-python-round-2/) we showed you 
#' how to scrape data from 
#' [www.MovieBodyCounts.com](http://www.moviebodycounts.com). Today, we will 
#' finish what we started by retrieving additional information from 
#' [www.imdb.com](http://www.imdb.com). In particular, we will attempt to 
#' recover the following pieces of information for each of the movies we 
#' collected last time: MPAA rating, genre(s), director(s), duration in minutes,
#' IMDb rating and full cast. We will detail the different steps of the process 
#' and provide for each step the corresponding code (red boxes for R, green 
#' boxes for Python). You will also find the entire codes at the end of this 
#' document.
#' 
#' If you think there’s a better way to code this in either language, leave a 
#' pull request on our [GitHub
#' repository](https://github.com/morpionZ/R-vs-Python/tree/master/Deadliest%20movies%20scrape/code)
#' or leave a note with suggestions in the comments below.
#' 


#' ##### 2 - Step by step process #####
#' 
#' First things first, let's set up our working environment by loading some
#' necessary libraries.
#' 

#+ libR, eval=FALSE, message=FALSE
# Load libraries
# No additional libraries needed here. Yeah!

#+ libPy, eval=FALSE, engine="python"
# String parsing libraries
from imdb import IMDb
import pandas as pd
import re

#' Randy is lucky today. Someone else has already written a package
#' (['IMDbPY'](http://imdbpy.sourceforge.net/)) to scrape data from IMDb.
#' Unfortunately for me, R users are too busy working with serious data sets to
#' take the time to write such a package for my favorite data processing
#' language. [Hadley Wickham](http://had.co.nz/) has included a ['movie' data
#' set](http://had.co.nz/data/movies/) in the [ggplot2](http://ggplot2.org/)
#' package that contains some of the information stored on IMDb, but some of the
#' pieces we need for today's challenge are missing.
#' 
#' Since I am not easily discouraged, I decided to write my own IMDb scraping
#' function (see below). It is not as sophisticated as the Python package Randy
#' is using today, but it does the job until someone else decides to write a
#' more complete R/IMDb package. As you will see, I am using the same scraping
#' technique (XPath) as the one I used in the first part of the challenge.
#' 

#+ IMDbScraperR, eval=FALSE
# Create IMDB scraper
IMDb <- function(ID) {
  # Retrieve movie info from IMDb.com. 
  #
  # Args:
  #   ID: IDs of the movies.
  #
  # Returns:
  #   A data frame containing one line per movie, and nine columns: movie ID,
  #   film title, year of release, duration in minutes, MPAA rating, genre(s),
  #   director(s), IMDb rating, and full cast.
  
  # Load required libraries
  require(XML)
  require(pbapply)    # Apply functions with progress bars!!!
  
  # Wrap core of the function in do.call and pblapply in order to
  # pseudo-vectorize it (pblapply) and return a data frame (do.call)
  info <- do.call(rbind, pblapply(ID, FUN = function(ID) {
    # Create movie URL on IMDb.com
    URL <- paste0("http://www.imdb.com/title/tt", ID)
    
    # Download and parse HTML of IMDb page
    parsed.html <- htmlParse(URL)
    
    # Find title
    Film <- xpathSApply(parsed.html, "//h1[@class='header']/span[@class='itemprop']", xmlValue)
    
    # Find year
    Year <- as.numeric(gsub("[^0-9]", "", xpathSApply(parsed.html, "//h1[@class='header']/span[@class='nobr']", xmlValue)))
    
    # Find duration in minutes
    Length_Minutes <- as.numeric(gsub("[^0-9]", "", xpathSApply(parsed.html, "//div[@class='infobar']/time[@itemprop='duration']", xmlValue)))
    
    # Find MPAA rating
    MPAA_Rating <- unname(xpathSApply(parsed.html, "//div[@class='infobar']/span/@content"))
    if (!is.character(MPAA_Rating)) {   # Some movies don't have a MPAA rating
      MPAA_Rating <- "UNRATED"
    }
    
    # Find genre
    Genre <- paste(xpathSApply(parsed.html, "//span[@class='itemprop' and @itemprop='genre']", xmlValue), collapse='|')
    
    # Find director
    Director <- paste(xpathSApply(parsed.html, "//div[@itemprop='director']/a", xmlValue), collapse='|')
    
    # Find IMDB rating
    IMDB_rating <- as.numeric(xpathSApply(parsed.html, "//div[@class='titlePageSprite star-box-giga-star']", xmlValue))
    
    # Extract full cast from the full credits page
    parsed.html <- htmlParse(paste0(URL,"/fullcredits"))
    Full_Cast <- paste(xpathSApply(parsed.html, "//span[@itemprop='name']", xmlValue), collapse='|')
    
    data.frame(ID = ID, Film = Film, Year = Year, Length_Minutes = Length_Minutes,
               MPAA_Rating = MPAA_Rating, Genre = Genre, 
               Director = Director, IMDB_rating = IMDB_rating, Full_Cast = Full_Cast))
  }))
}

#+ IMDbScraperPy, eval=FALSE, engine="python"
imdb_access = IMDb()

#' Randy and I now have a working IMDb scraper. We can start collecting and
#' organizing the data that we need.
#' 
#' First, let's load the data we collected last time.
#' 

#+ loadDataR, eval=FALSE 
# Load data from last challenge 
data <- read.csv("movies-R.csv")

#+ loadDataPy, eval=FALSE, engine="python"
movie_data = pd.read_csv("movies.csv")

#' Then, we will extract the movie IMDb ID from the IMDb URL we collected last
#' week. It's easy, it's the only number in the URL.
#' 

#+ getIDR, eval=FALSE
# For each movie, extract IMDb info and append it to the data
data <- within(data, {
  # Extract ID number
  IMDB_ID <- gsub("[^0-9]", "", IMDB_URL)

#+ getIDPy, eval=FALSE, engine="python"
# Grab only the movie number out of the IMDB URL
movie_data["Movie_Number"] = movie_data["IMDB_URL"].apply(lambda x: re.sub("[^0-9]", "", x))
  
#' Now that this is done, we will simply let the IMDb scraper collect the data
#' we want and we will append it to the data from the first part of the
#' challenge.
#' 

#+ appendR, eval=FALSE
  # Download IMDb info into a temporary variable
  IMDB_Info <- IMDb(IMDB_ID)
  
  # Save MPAA rating
  MPAA_Rating <- IMDB_Info$MPAA_Rating
  
  # Save genre(s)
  Genre <- IMDB_Info$Genre
  
  # Save director(s)
  Director <- IMDB_Info$Director
  
  # Save duration in minutes
  Length_Minutes <- IMDB_Info$Length_Minutes
  
  # Save IMDb rating
  IMDB_rating <- IMDB_Info$IMDB_rating
  
  # Save full cast
  Full_Cast <- IMDB_Info$Full_Cast
  
  # Delete IMDb info
  IMDB_Info <- NULL
})

#+ appendPy, eval=FALSE, engine="python"
with open("film-death-counts-Python.csv", "wb") as out_file:
    out_file.write("Film,Year,Body_Count,MPAA_Rating,Genre,Director,Actors,Length_Minutes,IMDB_Rating\n")

    for movie_entry in movie_data.iterrows():
        # Use a try-catch on the loop to prevent temporary connection-related issues from stopping the scrape
        try:
            movie = imdb_access.get_movie(movie_entry[1]["Movie_Number"])
            movie_fields = []
            
            # Remove non-ASCII character encodings and commas from movie titles
            movie_fields.append(movie["title"].encode("ascii", "replace").replace(",", ""))
            movie_fields.append(str(movie["year"]))
            movie_fields.append(str(movie_entry[1]["Body_Count"]))
            
            # Some movies don't have MPAA Ratings on IMDB
            try:
              movie_fields.append(str(movie["mpaa"].split(" ")[1]))
            except:
              movie_fields.append("")
            
            # For movies with multiple genres/directors/actors, join them with bars |
            movie_fields.append(str("|".join(movie["genres"])))
            movie_fields.append(str("|".join([str(x) for x in movie["director"]])))
            movie_fields.append(str("|".join([str(x) for x in movie["cast"]])))
            
            movie_fields.append(str(int(movie["runtime"][0].split(":")[-1])))
            movie_fields.append(str(float(movie["rating"])))

#' And finally, all what is left to do is to save the complete data set into a
#' .csv file and close the script. 
#' 

#+ saveR, eval=FALSE
write.csv(data, file = "movies-R-full.csv")

#+ savePy, eval=FALSE, engine="python"
# All entries are comma-delimited
            out_file.write(",".join(movie_fields) + "\n")
            
        except Exception as e:
            print "Error with", str(movie)


#' That's it! You should now have a .csv file somewhere on your computer 
#' containing all the information we just scraped in both parts of this 
#' challenge.
#' 
#' Sorry it took us so long to complete this part, but beginnings of semesters 
#' are always very busy times at the university.
#' 
#' Stay tuned for our next challenge! It will be about making a linear
#' regression, running basic diagnostic tests and plotting the resulting
#' straight line with its confidence interval.
#' 


#' ___
#' 
#' #### 3 - Source code ####
#' 
#' R and Python source codes are available 
#' [here](https://github.com/morpionZ/R-vs-Python/tree/master/Deadliest%20movies%20scrape/code).
#' 
