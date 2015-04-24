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
# spin("notebook.R") 
# pandoc("notebook.md", config = "pandoc_config.txt")


#+ 
#' **Document title:** R vs Python - Round 2 (1/2)
#' 
#' **Date:** January 12, 2014
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
#' #### Today's challenge: a data thief manual for honest scientists (Part 1 of 2) ####
#' 
#' ##### 1 - Introduction #####
#' 
#' Last week we started our challenge series with a rather simple task: plot a 
#' pretty barchart from some data collected by Randy for his recent post on the 
#' ["Top 25 most violence packed films" in the history of the movie 
#' industry](www.randalolson.com/2013/12/31/most-violence-packed-films/). Today 
#' we will try to up our game a little bit with a more complex task. We will 
#' show you how you can collect the data that Randy used for his post directly 
#' from the website they originate from 
#' ([www.MovieBodyCounts.com](http://www.moviebodycounts.com)). This is called 
#' data scraping, or the art of taking advantage of the gigantic database that 
#' is the Internet.
#' 
#' The basic principle behind the scraping of website data is simple: a website 
#' is a like database, and each page of the website is like a table of this 
#' database. All we want is find in the database the tables that contain 
#' information that we would like to acquire, and then extract this information 
#' from within these relevant tables. This task can be relatively easy if all 
#' the pages of a website have a similar structure (*i.e.*, if the database is 
#' clean and well maintained). In this ideal situation, all we have to do is 
#' identify one or more stable markers that delimit the desired information and 
#' use them to tell R or Python what to save in memory. Unfortunately not all 
#' websites have a similar structure across all of their pages and it can 
#' quickly become a nightmare to identify such markers. Worse, sometimes you 
#' will have to resign yourself to scrape or correct part or all of the data 
#' manually.
#' 
#' For this challenge, we will attempt to recover the following pieces of
#' information for each movie listed on
#' [www.MovieBodyCounts.com](http://www.moviebodycounts.com): title, release
#' year, count of on-screen deaths and link to the movie page on
#' [www.imdb.com](http://www.imdb.com) (this will help us for part 2 of this
#' challenge next week). We will detail the different steps of the process and
#' provide for each step the corresponding code (red boxes for R, green boxes
#' for Python). You will also find the entire codes at the end of this document.
#' 


#' ##### 2 - Step by step process #####
#' 
#' First things first, let's set up our working environment by loading some
#' necessary libraries.
#' 

#+ libR, eval=FALSE, message=FALSE
# Load libraries
library(RCurl)      # Everything necessary to grab webpages on the Web
library(XML)        # Everything necessary to parse XML and HTML code
library(pbapply)    # Progress bars!!! Just because why not :-)

# Create curl handle which can be used for multiple HHTP requests. 
# followlocation = TRUE in case one of the URLs we want to grab is a redirection
# link.
curl <- getCurlHandle(useragent = "R", followlocation = TRUE)

#+ libPy, eval=FALSE, engine="python"
# String parsing libraries
import string
import re

# urllib2 reads web pages if you provide it an URL
import urllib2

# html2text converts HTML to Markdown, which is much easier to parse
from html2text import html2text

#' Now a word about the organization of 
#' [www.MovieBodyCounts.com](http://www.moviebodycounts.com). To be perfectly 
#' honest, it is a bit messy :-) Movies are organized in a series of 
#' alphabetically ordered lists (by the first letter of each movie's title), 
#' each letter having its own page 
#' (http://www.moviebodycounts.com/movies-[A-Z].htm). There is also a list for 
#' movies which title starts with a number 
#' (http://www.moviebodycounts.com/movies-numbers.htm). Finally, all category 
#' letters are capitalized in the lists' URLs, except for letters v and x. 
#' Annoying, right? This is just one of the many little problems one can
#' encounter when dealing with messy databases :-)
#' 
#' With all this information in mind, our first task is to create a list of all
#' these lists.
#' 

#+ listURLsR, eval=FALSE
# Prepare URLs of the movie lists alphabetically ordered by first letter of
# movie title (capital A to Z, except for v and y) + "numbers" list (for movies
# which title starts with a number)
urls.by.letter <- paste0("http://www.moviebodycounts.com/movies-", 
                         c("numbers", LETTERS[1:21], "v", "W" , "x", "Y", "Z"), ".htm")

#+ listURLsPy, eval=FALSE, engine="python"
# Generate a list of all letters for the Movie pages (+ a "numbers" page)
# MovieBodyCount's actor pages are all with capital letters EXCEPT v and x
letters = ["numbers"] + list(string.letters[26:52].upper().replace("V", "v").replace("X", "x"))

#' Our next task is to go through the HTML code of all these lists and gather
#' the URLs of all the movie webpages. This is where the data scraping really
#' starts.
#' 
#' As you will quickly notices by reading the following code, Randy and I have
#' decided to use a different approach to identify and collect the desired URLs
#' (and of all the data in the rest of this challenge). I have decided to rely
#' on the [XML Path Language (XPath)](http://www.w3schools.com/xpath/), a
#' language that makes it easy to navigate through elements and attributes in an
#' XML/HTML document. Randy has decided to use an approach based on more
#' "classical" string parsing and manipulation functions. Note that these are
#' just personal preferences. XPath interpreters are also available in Python,
#' and R is fully equipped for manipulating character strings.
#' 
#' For each movie list, we will...
#' 

#+ loop1R, eval=FALSE 
# For each movie list... For loops are frowned upon in R, let's use the classier
# apply functions instead. Here I use the pblapply from the pbapply package.
# It's equivalent to the regular lapply function, but it provides a neat 
# progress bar. Unlist to get a vector. 
urls.by.movie <- unlist(pblapply(urls.by.letter, FUN = function(URL) {

#+ loop1Py, eval=FALSE, engine="python"
list_of_films = []
  
# Go through each movie list page and gather all of the movie web page URLs
for letter in letters:
  try:
  
#' ...download the raw HTML content of the webpage,...
#'

#+ readRaw1R, eval=FALSE
  # Load raw HTML
  raw.html <- getURL(URL, curl = curl)

#+ readRaw1Py, eval=FALSE, engine="python"
      # Read the raw HTML from the web page
      page_text = urllib2.urlopen("http://www.moviebodycounts.com/movies-" + letter + ".htm").read()
  
#' ...transform raw HTML into a more convenient format to work with,...
#' 

#+ parse1R, eval=FALSE
  # Parse HTML content
  parsed.html <- htmlParse(raw.html)

#+ parse1Py, eval=FALSE, engine="python"
      # Convert the raw HTML into Markdown
      page_text = html2text(page_text).split("\n")

#' ...find movie page entry, store the URL for later use and close the loop.
#'

#+ movieLinkR, eval=FALSE
  # Extract desired links from HTML content using XPath. 
  # The desired links are all the URLs ("a/@href") directly following
  # ("/following::") the image which source file is called "graphic-movies.jpg" 
  # ("//img[@src='graphic-movies.jpg']").
  links <- as.vector(xpathSApply(parsed.html, "//img[@src='graphic-movies.jpg']/following::a/@href"))

  # Most links are relative URLs. Add root of the website to make them absolute.
  if (!is.null(links)) {
    ix = grepl("http://www.moviebodycounts.com/", links)                  # Find relative URLs
    links[!ix] <- paste0("http://www.moviebodycounts.com/", links[!ix])   # Add root of website to make URLs absolute
    return(links)
  }
}), use.names = FALSE) # close the loop

# One URL is actually just a symbolic link to another page. Let's get rid of it.
ix <- which(grepl("movies-C.htm", urls.by.movie))
urls.by.movie <- urls.by.movie[-ix]

#+ movieLinkPy, eval=FALSE, engine="python"
      # Search through the web page for movie page entries
      for line in page_text:
        # We know it's a movie page entry when it has ".htm" in it, but not ".jpg", "contact.htm", and "movies.htm"
        # .jpg means it's a line with an image -- none of the movie entries have an image
        # contact.htm and movies.htm means it's a link to the Contact or Movies page -- not what we want
        # movies- means it's a redirect link to another page -- just skip over it
        if ".htm" in line and ".jpg" not in line and "contact.htm" not in line and "movies.htm" not in line and "movies-" not in line:
          #print line
          # The URL is in between parentheses (), so we can simply split the string on those
          # Some URLs are full URLs, e.g. www.moviebodycounts.com/movie_name.html, so splitting on the / gives us only the page name
          list_of_films.append(line.split("(")[-1].strip(")").split("/")[-1])
      
    # If the movie list page doesn't exist, keep going
    except:
      print "\nerror with " + letter + "\n"

#' Now that we know where to find each movie, we can start the hard part of this
#' challenge. We will go through each movie webpage and attempt to find its 
#' title, release year, count of on-screen deaths and link to its page on 
#' [www.imdb.com](http://www.imdb.com). We will save all this information in a
#' .csv file.
#' 
#' For each movie, we will...

#+ loop2R, eval=FALSE
# For each movie... 
# do.call(rbind, ...) to reorganize the results in a nice data frame
data <- do.call(rbind, pblapply(urls.by.movie, FUN = function(URL) {

#+ loop2Py, eval=FALSE, engine="python"
# Now that we have every movie web page URL, go through each movie page and
# extract the movie name, kill counts, etc.
out_file = open("film-death-counts.csv", "wb")
out_file.write("Film,Year,Kill_Count,IMDB_url\n")
  
for film_page in list_of_films:
  try:
      # The information we're looking for on the page:
      film = ""
      kills = ""
      year = ""
      IMDB_url = ""

      # A flag indicating that we've found the film title on the page
      found_title = False

#' ...download the raw HTML content of the webpage and transform raw HTML into a
#' more convenient format to work with,...
#' 

#+ readRaw2R, eval=FALSE
  # Load raw HTML
  raw.html <- getURL(URL, curl = curl)

  # Parse HTML content
  parsed.html <- htmlParse(raw.html)

#+ readRaw2Py, eval=FALSE, engine="python"
      # Read the page's raw HTML and convert it to Markdown (again) and go
      # through each line
      for line in html2text(urllib2.urlopen("http://www.moviebodycounts.com/" + film_page).read()).split("\n"):

#' ...attempt to find movie title,...

#+ titleR, eval=FALSE
  # Find movie title
  # Title appears inside a XML/HTML node called "title" ("//title"). In this
  # node, it comes after "Movie Body Counts: ". I use gsub to get rid off "Movie
  # Body Counts: " and keep only the movie title.
  Film <- xpathSApply(parsed.html, "//title", xmlValue)
  Film <- gsub("Movie Body Counts: ", "", Film)

#+ titlePy, eval=FALSE, engine="python"
# If we haven't found the title yet, these markers tell us we've found the movie
# title
        if not found_title and "!" not in line and "(" not in line and "[" not in line and line.strip() != "":
          film = line.replace(",", "").strip(":")
          found_title = True

#' ...attempt to find movie year,...

#+ yearR, eval=FALSE
  # Find movie year
  # The year is usually a text inside ("/descendant::text()") a link node
  # ("//a") which source contains the string "charts-year" ("[contains(@href,
  # 'charts-year')]").
  Year <- as.numeric(xpathSApply(parsed.html, "//a[contains(@href, 'charts-year')]/descendant::text()", xmlValue))

#+ yearPy, eval=FALSE, engine="python"
        # The year is usually on a line with "charts-year"
        if "charts-year" in line:
          year = line.split("[")[1].split("]")[0]

#' ...attempt to find link to movie on IMDB,...

#+ imdbR, eval=FALSE
  # Find IMDB link
  # The IMDB link is inside a link node ("//a") which source contains "imdb"
  # ("/@href[contains(.,'imdb')]")
  IMDB_URL <- as.vector(xpathSApply(parsed.html, "//a/@href[contains(.,'imdb')]"))[1]

  # Note: We select the first element of the vector because for at least one of
  # the movies, this command returns two links.

#+ imdbPy, eval=FALSE, engine="python"
        # The IMDB url is on a line with "[imdb]"
        if "[imdb]" in line.lower():
          IMDB_url = line.lower().split("[imdb](")[1].split(")")[0]

#' ... and finally attempt to find the on-screen kill count. Here, Randy chose 
#' an approach that minimizes his coding effort, but that will potentially force
#' him to make several manual corrections a posteriori. I chose to find a 
#' solution that works with minimal to no manual corrections, but that requires 
#' an extra coding effort. Whichever approach is best depends mostly on the size
#' of the data you want to scrape and the time you have to do it.

#+killsR, eval=FALSE
  # Find kill count.
  # Kill count is contained in the first non-empty text node
  # ("/following::text()[normalize-space()]") after the image which source file
  # is called "graphic-bc.jpg" ("//img[@src='graphic-bc.jpg']")
  Body_Count <- xpathSApply(parsed.html, "//img[@src='graphic-bc.jpg']/following::text()[normalize-space()]", xmlValue)[1]

  # Now we need to clean up the text node that we just extracted because there
  # are lots of inconsistencies in the way the kill counts are displayed across
  # all movie pages. For instance, counts are sometimes accompanied by text, not
  # always the same, and sometimes there is no text at all. Sometimes the total
  # count is split in two numbers (e.g., number of dead humans and number of
  # dead aliens). And sometimes the total count is displayed and accompanied by
  # a split count in parenthesis. First, let's remove everything that is
  # writtent in parenthesis or that is not a number.
  # Using gsub, remove everything in parenthesis and all non number characters
  Body_Count <- gsub("\\(.*?\\)", " ", Body_Count)
  Body_Count <- gsub("[^0-9]+", " ", Body_Count)
  
  # In case the total count has been split, we want to separate these numbers
  # from each other so that we can add them up later. Using strsplit, split the
  # character string at spaces
  Body_Count <- unlist(strsplit(Body_Count, " "))
  
  # For now, we have extracted characters. Transform them into numbers.
  Body_Count <- as.numeric(Body_Count)
  
  # Sum up the numbers (in case they have been split into separate categories.
  Body_Count <- sum(Body_Count, na.rm = TRUE)
  
#+ killsPy, eval=FALSE, engine="python"
        # The kill counts are usually on a line with "Film:"
        if "film:" in line.lower() or "kills:" in line.lower() or "count:" in line.lower():
          kills = re.sub("[^0-9]", "", line.split(":")[1].split("(")[0])

#' Almost done! Now we just need to close the loop and write the data frame into
#' a .csv file

#+ saveR, eval=FALSE
  # Return scraped data into a data frame form
  return(data.frame(IMDB_URL, Film, Year, Body_Count))
}))

# Save scraped data in a .csv file for future use
write.csv(data, "movies-R.csv", row.names = FALSE)

#+ savePy, eval=FALSE, engine="python"
      out_file.write(film + "," + year + "," + kills + "," + IMDB_url + "\n")

    # If a movie page fails to open, print out the error and move on to the next movie
    except Exception as e:
      print film_page
    print e

out_file.close()

#' And voilà! You should now have a .csv file somewhere on your computer
#' containing all the information we just scraped from the website. Not too
#' hard, right?
#' 
#' Keep the .csv file, we will use it again next week to complete this challenge
#' by scraping additional information from [www.imdb.com](http://www.imdb.com).
#' 


#' ___
#' 
#' #### 3 - Source code ####
#' 
#' R and Python source codes are available 
#' [here](https://github.com/morpionZ/R-vs-Python/tree/master/Deadliest%20movies%20scrape/code).
#' 


#' ___
#' 
#' #### 4 - Bonus for the braves ####
#' 
#' Today's challenge was code and text heavy. No pretty pictures to please the eye. So, for all the brave people who made it to the end, here is a cat picture :-) 

#+ bonus, echo=FALSE
library(jpeg)  # To read JPG images

# Download a relevant cat picture; mode is set to "wb" because it seems that
# Windows needs it. I don't use Windows, I can't confirm
if (!file.exists("programming_cat.jpg")) {
  download.file(url = "http://i.chzbgr.com/completestore/2010/5/18/129186912722282650.jpg", 
                destfile = "programming_cat.jpg", quiet = TRUE, mode = "wb")
}

# Display image
#' <center> ![](programming_cat.jpg) </center>
#' 






