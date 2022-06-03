# Corporate-performance-and-employee-sentiment

## Description:
The goal of this project is to build a dashboard for students to compare employee satisfaction and wellbeing among big consultancy firms in Belgium and Luxembourg. This is done by scraping Glassdoor reviews, making different visualizations and finally hosting it on herokuapp.

## Usage:
### Scraping:
#### Getting the links
The scraping happens in two steps. A first one is getting the link for the first page for each company. This is done with getting_links.ipynb. It needs to be fed a list of companies, it will then open an automated browser and look up each company on glassdoor. These links will then be stored in a csv file. It is unlikely all the links are going to be the right ones and that it will find all companies even though they exist. It is recommended to use this notebook for getting the bigger chunk of the links and then continue by hands to fill in the missing links.

#### Reviews scraper
It needs to be fed the links. It will alter the links to get all pages and add filter. The code can easily be altered to change the filters. It will then loop over all the pages for each link and write the reviews to csv in the data folder.

### Cleaning:
The next step is cleaning. Indeed the reviews contain stars instead of numbers for the ratings. It's also important to extract the date out of a string composed of data, function and location and then convert it to datetime for future use. Lastly it will merge all the csv's of reviews and create two additional columns, one for company one for location to keep track of the differences between the reviews. This can be done with the file prepare_reviews.ipynb

### Creating the dashboard:
The dashboard contains three different visualizations. The dashboard.ipynb takes these visualizations one by one, cleans and formats the data and finally plots them into a dashboard.

## End result:
Available at: 
