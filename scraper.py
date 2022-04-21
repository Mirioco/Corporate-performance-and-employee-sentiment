#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 19 15:13:57 2022

@author: corentin
"""

# Imports
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

import random
import time
import pandas as pd

# Get NOKIA link for testing
df = pd.read_csv('data/links_sample.csv')
link = df[df['company'] == 'NOKIA']['link'].values[0]


# Set up
driver = webdriver.Chrome('/Users/corentin/Documents/chromedriver')
url = link
driver.get(url)
time.sleep(random.uniform(2, 3))
# Setting window size to make sure the scrolls get to where they are supposed to
driver.set_window_size(1920, 1080)

# !!! Rarely works, either fix it in this code or collect UK links !!!
# Set site language to english 
time.sleep(random.uniform(2, 4))
driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
language_choice = driver.find_element_by_xpath('//*[@id="Footer"]/nav/ul[2]/li[3]/div/div/div[1]')
language_choice.click()
time.sleep(random.uniform(2, 4))
# Scrolls down to not get intercepted by "accept cookies" overlay, window has to be big enough for it to be able to see the choice and not be blocked by cookies thing
united_kingdom = driver.find_element_by_xpath('//*[@id="option_21_b86d8f6-5681-fa3c-88-db6c1ebe86f"]')
united_kingdom.click()
time.sleep(random.uniform(2, 4))


# Get only english reviews
filter_button = driver.find_element_by_xpath('//*[@id="MainContent"]/div/div[1]/div[1]/div[1]/div/div[1]/div[2]/div[2]/button/span')
filter_button.click()
time.sleep(random.uniform(2, 4))
language_button = driver.find_element_by_xpath('//*[@id="MainContent"]/div/div[1]/div[1]/div[1]/div/div[1]/div[3]/div[2]/div[2]/div/div[1]')
language_button.click()
time.sleep(random.uniform(2, 4))
english = driver.find_element_by_xpath('//*[@id="option_eng"]')
english.click()
time.sleep(random.uniform(2, 4))


# Start with most recent reviews
driver.execute_script('window.scrollTo(0, 450)')
freshness_button = driver.find_element_by_xpath('//*[@id="MainContent"]/div/div[1]/div[1]/div[2]/div/span/div/div/div[1]')
freshness_button.click()
time.sleep(random.uniform(2, 4))
most_recent = driver.find_element_by_xpath('//*[@id="option_DATE"]')
most_recent.click()
time.sleep(random.uniform(2, 4))

# Initializating variables
rating_classes = {'css-xd4dom': '*',
               'css-18v8tui': '**',
               'css-vl2edp': '***',
               'css-1nuumx7': '****',
               'css-s88v13': '*****'}
subcategories = ['work_life_balance', 
                 'culture_and_values', 
                 'diversity_and_inclusion', 
                 'career_opportunities',
                 'compensation_and_benefits',
                 'senior_management']

def scrape_ratings(post):
    """
    Returns a string with the main rating and a list with subrating
    """
    # Main rating
    main_rating = post.find('span', class_ = 'ratingNumber mr-xsm').string
    
    # Subratings
    try:
        rating_categories = post.find('div', class_ = 'content')
        sub_ratings = rating_categories.find_all('li') # Each rating has a different class, it's the only way to differentiate

        ratings = []
        for sub_rating in sub_ratings:
            rating_class = sub_rating.find_all('div')[1]['class'][0]
            rating = rating_classes[rating_class]
            ratings.append(rating)
    except:
        ratings = [None for i in range(6)] 
    
    return main_rating, ratings
        
        
def single_page_scraper(html): #Needs the driver.page_source
    """
    Scrapes rating, subrating, post_title, date_and_job, recommend, CEO approval,
    business outlook, pros and cons of all postings on a single page and
    returns a dataframe
    """
    
    soup = BeautifulSoup(html, 'lxml')
    
    # Get postings on a single page
    # First and other nince reviews have different classes
    first_posting = soup.find_all('li', class_ = 'empReview cf pb-0 mb-0')
    next_postings = soup.find_all('li', class_ = 'noBorder empReview cf pb-0 mb-0')
    # Extending first_posting with the nine other and renaming the variable adequatly
    first_posting.extend(next_postings)
    postings = first_posting
    
    df = pd.DataFrame({'main_rating': [],
                       'work_life_balance_rating': [], 
                       'culture_and_values_rating': [], 
                       'diversity_and_inclusion_rating': [], 
                       'career_opportunities_rating': [],
                       'compensation_and_benefits_rating': [],
                       'senior_management_rating': []
                       })
    
    # Looping into
    for post in postings:
        main_rating, subratings = scrape_ratings(post)
        print(main_rating, subratings)
        
        #Populating the dataframe
        df = df.append(({'main_rating': main_rating,
                         'work_life_balance_rating': subratings[0], 
                         'culture_and_values_rating': subratings[1], 
                         'diversity_and_inclusion_rating': subratings[2], 
                         'career_opportunities_rating': subratings[3],
                         'compensation_and_benefits_rating': subratings[4],
                         'senior_management_rating': subratings[5]}),
                        ignore_index=True)
    
    return df
        
    

    
    
    
# To remove overlay    
driver.execute_script("""
javascript:(function(){
  document.getElementsByClassName('hardsellOverlay')[0].remove();
  document.getElementsByTagName("body")[0].style.overflow = "scroll";
  let style = document.createElement('style');
  style.innerHTML = `
    #LoginModal {
      display: none!important;
    }
  `;
  document.head.appendChild(style);
  window.addEventListener("scroll", function (event) {
    event.stopPropagation();
  }, true);
})();
""")    
    
    
    
    
    