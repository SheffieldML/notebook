"""
Copyright 2014 Randal S. Olson

This file is a script that combines data from www.MovieBodyCounts.com and IMDB.com to
create a list of films, metadata about the films, and the number of on-screen body
counts in the films. The script requires an internet connection and two libraries
installed: imdbpy and pandas.


This script is free software: you can redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free Software Foundation,
either version 3 of the License, or (at your option) any later version.

This script is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this script.
If not, see http://www.gnu.org/licenses/.
"""

from imdb import IMDb
import pandas as pd
import re

imdb_access = IMDb()
movie_data = pd.read_csv("movies.csv")

# Grab only the movie number out of the IMDB URL
movie_data["Movie_Number"] = movie_data["IMDB_URL"].apply(lambda x: re.sub("[^0-9]", "", x))

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
            
            # All entries are comma-delimited
            out_file.write(",".join(movie_fields) + "\n")
            
        except Exception as e:
            print "Error with", str(movie)
