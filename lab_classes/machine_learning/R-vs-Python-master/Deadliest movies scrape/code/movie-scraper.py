"""
Copyright 2014 Randal S. Olson

This file is a script that scrapes on-screen body counts for various movies on
www.MovieBodyCounts.com. The script requires an internet connection and two libraries
installed: urllib2 and html2text.

Due to inconsistent formatting of the HTML on www.MovieBodyCounts.com, the script will
not scrape everything perfectly. As such, the resulting output file *will* require some
cleanup afterwards. The manual cleanup will take less time than finding an elegant
solution to perfectly scrape the page.


This script is free software: you can redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free Software Foundation,
either version 3 of the License, or (at your option) any later version.

This script is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this script.
If not, see http://www.gnu.org/licenses/.
"""

# String parsing libraries
import string
import re

# urllib2 reads web pages if you provide it an URL
import urllib2

# html2text converts HTML to Markdown, which is much easier to parse
from html2text import html2text

# Generate a list of all letters for the Movie pages (+ a "numbers" page)
# MovieBodyCount's actor pages are all with capital letters EXCEPT v and x
letters = ["numbers"] + list(string.letters[26:52].upper().replace("V", "v").replace("X", "x"))

list_of_films = []

# Go through each movie list page and gather all of the movie web page URLs
for letter in letters:
    try:
        # Read the raw HTML from the web page
        page_text = urllib2.urlopen("http://www.moviebodycounts.com/movies-" + letter + ".htm").read()
        
        # Convert the raw HTML into Markdown
        page_text = html2text(page_text).split("\n")
        
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

# Now that we have every movie web page URL, go through each movie page and extract the movie name, kill counts, etc.
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
        
        # Read the page's raw HTML and convert it to Markdown (again) and go through each line
        for line in html2text(urllib2.urlopen("http://www.moviebodycounts.com/" + film_page).read()).split("\n"):
        
            # If we haven't found the title yet, these markers tell us we've found the movie title
            if not found_title and "!" not in line and "(" not in line and "[" not in line and line.strip() != "":
                film = line.replace(",", "").strip(":")
                found_title = True
                
            # The kill counts are usually on a line with "Film:"
            if "film:" in line.lower() or "kills:" in line.lower() or "count:" in line.lower():
                kills = re.sub("[^0-9]", "", line.split(":")[1].split("(")[0])

            # The year is usually on a line with "charts-year"
            if "charts-year" in line:
                year = line.split("[")[1].split("]")[0]
            
            # The IMDB url is on a line with "[imdb]"
            if "[imdb]" in line.lower():
                IMDB_url = line.lower().split("[imdb](")[1].split(")")[0]
                
        out_file.write(film + "," + year + "," + kills + "," + IMDB_url + "\n")
            
    # If a movie page fails to open, print out the error and move on to the next movie
    except Exception as e:
        print film_page
        print e
        
out_file.close()
