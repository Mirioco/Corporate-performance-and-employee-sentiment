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


# Initializating variables
subrating_classes = {'css-xd4dom': '*',
               'css-18v8tui': '**',
               'css-vl2edp': '***',
               'css-1nuumx7': '****',
               'css-s88v13': '*****'}
rating_subcategories = ['Work/Life Balance',
                   'Culture & Values',
                   'Diversity & Inclusion',
                   'Career Opportunities',
                   'Compensation and Benefits',
                   'Senior Management']

# Get NOKIA link for testing
link = 'https://www.glassdoor.com/Reviews/Nokia-Reviews-E3494.htm'


# Set up
def setup_driver():
    """
    Launches driver, maximizes window size
    """
    driver = webdriver.Chrome('/Users/corentin/Documents/chromedriver')
    time.sleep(random.uniform(2, 4))
    # Setting window size to make sure the scrolls get to where they are supposed to
    driver.set_window_size(1920, 1080)
    driver.implicitly_wait(30)
    return driver
    
driver = setup_driver()

def setup_url_site(driver, link):
    """
    Gets the url, sets the site in english, set the reviews in english and sets the 
    reviews to chronologically order
    """
    
    url = link
    driver.get(url)
    
    # Set site language to us
    time.sleep(random.uniform(2, 4))
    driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
    time.sleep(random.uniform(2, 4))
    language_choice = driver.find_element_by_xpath('//*[@id="Footer"]/nav/ul[2]/li[3]/div/div/div[1]')
    language_choice.click()
    soup = BeautifulSoup(driver.page_source, 'lxml')
    language_click_box = soup.find('div', class_='dropdownOptions dropdownExpanded animated above')
    for li in language_click_box.find_all('li'):
        country = li.find_all('span')[1].string
        if country == 'United States':
            us_id = li.get('id')
            break
    time.sleep(random.uniform(2, 4))
    us = driver.find_element_by_id(us_id)
    us.click()
    
    # Get only english reviews
    time.sleep(random.uniform(2, 4))
    filter_button = driver.find_element_by_xpath('//*[@id="MainContent"]/div/div[1]/div[1]/div[1]/div/div[1]/div[2]/div[2]/button/span')
    filter_button.click()
    time.sleep(random.uniform(2, 4))
    language_button = driver.find_element_by_xpath('//*[@id="MainContent"]/div/div[1]/div[1]/div[1]/div/div[1]/div[3]/div[2]/div[2]/div/div[1]')
    language_button.click()
    time.sleep(random.uniform(2, 4))
    english = driver.find_element_by_xpath('//*[@id="option_eng"]')
    english.click()

    # Start with most recent reviews
    time.sleep(random.uniform(2, 4))
    driver.execute_script('window.scrollTo(0, 450)')
    time.sleep(random.uniform(2, 4))
    freshness_button = driver.find_element_by_xpath('//*[@id="MainContent"]/div/div[1]/div[1]/div[2]/div/span/div/div/div[1]')
    freshness_button.click()
    time.sleep(random.uniform(2, 4))
    most_recent = driver.find_element_by_xpath('//*[@id="option_DATE"]')
    most_recent.click()
    time.sleep(random.uniform(2, 4))


def scrape_ratings(post):
    """
    Returns a string with the main rating and a list with subrating
    """
    # Main rating
    main_rating = post.find('span', class_ = 'ratingNumber mr-xsm').string
    
    # Subratings
    try:
        rating_categories = post.find('div', class_ = 'content')
        ratings = rating_categories.find_all('li') # Each rating has a different class, it's the only way to differentiate

        subratings = {}
        for subrating in ratings:
            #Get categories, it's not always 6 of them
            subrating_category = subrating.find_all('div')[0].string
            subrating_class = subrating.find_all('div')[1]['class'][0]
            subrating = subrating_classes[subrating_class]
            subratings[subrating_category] = subrating
    except:
        subratings = {'Work/Life Balance': None,
                      'Culture & Values': None, 
                      'Diversity & Inclusion': None, 
                      'Career Opportunities': None,
                      'Compensation and Benefits': None,
                      'Senior Management': None}
    
    return main_rating, subratings
   
   
def single_page_scraper(html): #Needs the driver.page_source
    """
    Scrapes rating, subrating, post_title, date_and_job, recommend, CEO approval,
    business outlook, pros and cons of all postings on a single page and
    returns a dataframe
    """
    
    soup = BeautifulSoup(html, 'lxml')
    print('soup ok')
    
    # Get postings on a single page
    # First and other nine reviews have different classes
    first_posting = soup.find_all('li', class_ = 'empReview cf pb-0 mb-0')
    next_postings = soup.find_all('li', class_ = 'noBorder empReview cf pb-0 mb-0')
    # Extending first_posting with the nine other and renaming the variable adequatly
    first_posting.extend(next_postings)
    postings = first_posting
    print(len(postings))
    
    df = pd.DataFrame({'main_rating': [],
                       'Work/Life Balance': [], 
                       'Culture & Values': [], 
                       'Diversity & Inclusion': [], 
                       'Career Opportunities': [],
                       'Compensation and Benefits': [],
                       'Senior Management': []
                       })
    
    # Looping into
    for post in postings:
        main_rating, subratings = scrape_ratings(post)
        print('Ratings gotten: ', main_rating, subratings)
            
        post_ratings = {'main_rating': main_rating}
        
        for subcategory in rating_subcategories:
            #post_ratings[subcategory] = subratings[subcategory]
            print(subratings[subcategory])
             
            #Populating the dataframe
            df = df.append((post_ratings),
                            ignore_index=True)
    
    return df
        
    
df = single_page_scraper(driver.page_source)
    
    
   
# To remove overlay
# =============================================================================
# try:
#     whatever
# except ElementClickInterceptedException:    
#     driver.execute_script("""
#     javascript:(function(){
#       document.getElementsByClassName('hardsellOverlay')[0].remove();
#       document.getElementsByTagName("body")[0].style.overflow = "scroll";
#       let style = document.createElement('style');
#       style.innerHTML = `
#         #LoginModal {
#           display: none!important;
#         }
#       `;
#       document.head.appendChild(style);
#       window.addEventListener("scroll", function (event) {
#         event.stopPropagation();
#       }, true);
#     })();
#     """)    
# =============================================================================
    
    
    
    
    