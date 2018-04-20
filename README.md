# final-project

Data Sources
This project uses dbpedia as a dataset. dbpedia xtracts structured data from Wikipedia, and other Wiki projects, and presents it as linked data. More general information can be found about dbpedia at http://wiki.dbpedia.org/about.

In particular, this project uses the precision search and find interface found at http://dbpedia.org/fct/facet.vsp. The interface has a permalink feature, with a standard way to list queries, such as search terms, number of results, etc. Queries are not case-sensitive. The program automatically reformats queries to to fit the permalink URL format.

Other Info
Aside from Flask, I use two plotly modules to display data:
 scatter plots: https://plot.ly/python/line-and-scatter/
 scatter maps: https://plot.ly/python/scatter-plots-on-maps/
These are directly integrated into flask application for display.

Code Structure
The model.py file structures the data, which is funneled through to app.py to be formatted for display.

The get_dbpedia_data function extracts data from dbpedia. It caches the search result for a keyword, and then crawls that list, retrieving and caching information for each particular search result, and returns a list of the html for each result. Because different queries can have overlapping results, this function checks each result before caching, so that only requests for new results are made to the dbpedia website. 

The generate_db_entity_data function takes the returned list of result html, and extracts relevant data to populate database tables. All results are populated into entities table. Additionally, if links or coordinates are available, location or link information will be added to their respective tables, pointing back to the primary key of the entity id.

The generate_entities_list function queries the database for entities with the query term in the description. It then refers to the Entity class and generates entity objects for each returned item that matches the keyword search. The returned entity list can then be used by other functions and for display.

User Guide
To run the program, run the controller.py file. It will automatically create a sqlite database, if none exists. The command line will then provide the option to retrieve additional data from dbpedia or work with existing data. Once the user is done retrieving data, a flask application will be started. The index page gives a sample url for user data and explains how to make database queries directly through the url. There are two links to view a map of results that are locations or the distribution of links (how many subjects have each number of relations). The table of results can be sorted alphabetically or by the number of relations, and if the user clicks on the number of links for an entry, it takes the user to a separate page with a list of the links for part particular search result.

