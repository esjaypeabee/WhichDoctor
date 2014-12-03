# WhichDoctor
### Hackbright Final Project

===========

## Introduction

WhichDoctor gives users a tool to see past the dark magic that is medical pricing. Intended for cost-conscious patients seeking a new doctor, this app analyzes data from the Medicare open data set to provide a list of doctors with name, contact information, specialty, and the cost of the doctor relative to other medical providers in the same specialty. Users can search for doctors by geographic area, procedures performed, or specialty in plain English terms, and WhichDoctor will translate the query into relevant medical jargon. 

**Note:** The cost information represented by the app is based only on the charges medical providers submitted to Medicare in 2012 because that is the data that was available at the time this app was created. WhichDoctor does not take into account agreements other insurers may have with providers or their insured that impact the amounts providers charge and payments insureds must make directly to providers, such as copays. Consequently, *the representation of each provider's 'cost' will probably not be relevant to an individual patient.*

## Table of Contents
- [Introduction](#introduction)
- [Searching for a doctor](#searching-for-a-doctor)
- [Spellchecking](#spellchecking)
- [The Map](#the-map)
- [The Data](#the-data)
- [Installation](#installation)

## Searching for a doctor

WhichDoctor's landing page contains two search boxes. One box allows the user to search for medical treatments by entering a medical specialty, such as 'Optomitrist' or 'eye doctor,'' or a medical procedure, such as 'eye exam.' The other box allows the user to search by location. Users may enter terms into either or both boxes.

![landing page]
(/screen_shots/landing.png)

WhichDoctor will then build a SQLAlchemy query based on the user's input and run it over a PostgreSQL database. The database columns describing provider specialties and procedure descriptions have been indexed, tokenized (broken into individual words), and stemmed (reduced to their root words) using PostgreSQL's full text search capabilities. This allows for a faster search that more closely mirrors natural language queries.

![results]
(/screen_shots/results.png)

The query's results are then loaded into a table on the page with an AJAX request. Clicking on the table's headings lets the user sort by name, specialty, or cost. Each provider's name is linked to a page that displays the doctor's office address.

![provider page]
(/screen_shots/provider.png)

## Spellchecking

WhichDoctor will also check user input for spelling errors and suggests corrections. It does so using a [python algorithm](http://norvig.com/spell-correct.html) that finds all the words with an [edit distance](http://en.wikipedia.org/wiki/Edit_distance) of 2 from the user's input and checking it against a dictionary of known words. Clicking on a suggested word brings the user to a set of search results based on the suggested word.

![spellchecker]
(/screen_shots/spellchecker.png)

## The Map

Each set of search results comes with a map created with the Mapbox Javascript API that shows the location of each provider's office. The colors of the pins correspond to how expensive each provider is likely to be. Mousing over each doctor in the table calls a JQuery function that causes that doctor's pin to enlarge, which is especially useful when many providers share the same address. The map automatically resizes and rezooms to display all of a search results' pins.

![mouseover]
(/screen_shots/mouseover.png)

Users may also change the search area by moving and rezooming the map, and clicking 'Search in Map'. WhichDoctor will then pull the boundary coordinates from the map and find all doctors matching the search terms whose offices fall within those coordinates. Each provider's office address has already been  geocoded using PyGeocoder and the Google Geocoder API.

## The Data

The database was seeded using the data found on the [CMS site](http://www.cms.gov/Research-Statistics-Data-and-Systems/Statistics-Trends-and-Reports/Medicare-Provider-Charge-Data/Physician-and-Other-Supplier.html) The tab separated file found here contains one line for each type of claim each doctor filed in 2012, a code and description for each claim, the number of times that claim was filed, the average amount Medicare will pay for that claim, the average amount submitted to Medicare, and the average amount Medicare actually paid. The cost comparison WhichDoctor uses comes from the average amount each doctor submitted to medicare.

Since WhichDoctor does not change anything about the data, much of the information required by the app can be precalculated and stored in the app. This includes the latitude and longitude of each provider's office, the indices for the specialty columns and procedure descriptions, as well all of the calculations required to make the cost comparison. These calculations were performed using NumPy arrays and built in functions.

In this version of the app, the data is limited to providers that practice in San Francisco.

## Technologies used

PostgreSQL, SQLAlchemy, Python, Numpy, Flask, Jinja, Javascript, JQuery, Bootstrap, Mapbox, PyGeocoder

## Installation

Due to the fact that the data must be highly preprocessed, installation may take a bit of time.

1. Get started by cloning this repo and installing all the required libraries:

	1. Create a python virtual environment::

	        virtualenv env


	2. Activate the virtual environment::

	        source env/bin/activate


	3. Install the requirements::

	        pip install -r requirements.txt

2. Next, set up [PostgreSQL](http://www.postgresql.org/download/) according to the instructions on their site for your operating system.

3. Download the [Medicare Data](http://www.cms.gov/Research-Statistics-Data-and-Systems/Statistics-Trends-and-Reports/Medicare-Provider-Charge-Data/Physician-and-Other-Supplier.html). This is a 1.7G tab separated file.

4. Open model.py in intpretive mode by typing:

		python -i model.py 


	into your terminal. Then type the following line into your terminal to create the tables:

		Base.metadata.create_all(engine)

5. If you don't have an account already, create a google api account and store the API key in your environment. (see [this blog post](http://andrewtorkbaker.com/using-environment-variables-with-django-settings) for an example)

6. With your virtual environment activated, run seed.py. Since each provider's address must be geocoded using google's geocoder api, and it has a rate limit of 5 calls per second, the script will delay to one call per second. As written, the script will take about 40 minutes to run. If you have a paid account with google and do not need to worry about a rate limit, you can comment out line 91 in seed.py to make the script run faster.

7. Next, run calc_avg_std.py to insert each doctor's zscore into the database.

8. Finally, run python app.py in your terminal and send your browser to http://localhost:5000/  Enjoy!

