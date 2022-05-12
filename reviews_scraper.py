#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 19 15:13:57 2022

@author: corentin
"""

# Imports
from selenium import webdriver
from bs4 import BeautifulSoup
#from selenium.webdriver.common.keys import Keys
#from selenium.webdriver.common.action_chains import ActionChains

import random
import time
import pandas as pd
import numpy as np


# Initializating variables
subrating_classes = {'css-xd4dom': '*',
               'css-18v8tui': '**',
               'css-vl2edp': '***',
               'css-1nuumx7': '****',
               'css-s88v13': '*****'}
shape_styles = {'css-10xv9lv-svg': 'O',
         'css-1kiw93k-svg': 'X',
         'css-1h93d4v-svg': '-',
         'css-hcqxoa-svg': 'V'}

# Get Deloitte link for testing
url = 'https://nl.glassdoor.be/Reviews/Deloitte-Reviews-E2763.htm'


# Set up
def setup_driver():
    """
    Launches driver, maximizes window size
    """
    driver = webdriver.Chrome('/Users/corentin/Documents/chromedriver')
    time.sleep(random.uniform(2, 4))
    # Setting window size to make sure the scrolls get to where they are supposed to
    driver.set_window_size(1920, 1080)
    driver.implicitly_wait(10)
    return driver

def setup_url_site(driver, url):
    """
    Gets the url, sets the site in english, set the reviews in english and sets the 
    reviews to chronologically order
    """
    
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
    
    # Only belgian reviews
    time.sleep(random.uniform(2, 4))
    filter_button = driver.find_element_by_xpath('//*[@id="MainContent"]/div/div[1]/div[1]/div[1]/div/div[1]/div[2]/div[2]/button/span')
    filter_button.click()
    time.sleep(random.uniform(2, 4))
    location_box = driver.find_element_by_xpath('//*[@id="MainContent"]/div/div[1]/div[1]/div[1]/div/div[1]/div[3]/div[2]/div[1]/div/div[1]')
    location_box.click()
    time.sleep(random.uniform(2, 4))
    location_input = driver.find_element_by_xpath('//*[@id="MainContent"]/div/div[1]/div[1]/div[1]/div/div[1]/div[3]/div[2]/div[1]/div/div[1]/div/div/div/input')
    location_input.send_keys('Belgium')
    belgium = driver.find_element_by_xpath('//*[@id="option_N,25"]/span')
    belgium.click()
    
    # For Interns and full time and part time
    time.sleep(random.uniform(2, 4))
    filter_button = driver.find_element_by_xpath('//*[@id="MainContent"]/div/div[1]/div[1]/div[1]/div/div[1]/div[2]/div[2]/button/span')
    filter_button.click()
    time.sleep(random.uniform(2, 4))
    jobs_category = driver.find_element_by_xpath('//*[@id="MainContent"]/div/div[1]/div[1]/div[1]/div/div[1]/div[3]/div[1]/div[2]/div/div[1]')
    jobs_category.click()
    jobs_categories = driver.find_element_by_xpath('//*[@id="option_INTERN"]/div')
    jobs_categories.click()
    
    
    # Returns modified url with all filters
    url = driver.current_url
    return url

driver = setup_driver()
url = setup_url_site(driver, url)


# Scraping functions
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
        subratings = {'Work/Life Balance': np.nan,
                      'Culture & Values': np.nan, 
                      'Diversity & Inclusion': np.nan, 
                      'Career Opportunities': np.nan,
                      'Compensation and Benefits': np.nan,
                      'Senior Management': np.nan}
    
    return main_rating, subratings
   

   
   
   
def single_page_scraper(html): #Needs the driver.page_source
    """
    Scrapes rating, subrating, post_title, date_and_job, recommend, CEO approval,
    business outlook, pros and cons of all postings on a single page and
    returns a dataframe
    """
    #Initializing df
    df = pd.DataFrame({'main_rating': [],
                       'Work/Life Balance': [], 
                       'Culture & Values': [], 
                       'Diversity & Inclusion': [], 
                       'Career Opportunities': [],
                       'Compensation and Benefits': [],
                       'Senior Management': []
                       })
    soup = BeautifulSoup(html, 'lxml')
    
    # Get postings on a single page
    # First and other nine reviews have different classes
    first_posting = soup.find_all('li', class_ = 'empReview cf pb-0 mb-0')
    next_postings = soup.find_all('li', class_ = 'noBorder empReview cf pb-0 mb-0')
    # Extending first_posting with the nine other and renaming the variable adequatly
    first_posting.extend(next_postings)
    postings = first_posting
    
    
    # Looping on postings
    for post in postings:
        # Get status
        status = post.find('span', class_ = 'pt-xsm pt-md-0 css-1qxtz39 eg4psks0').string
        # Get general opinion 
        post_title = post.find('h2', class_ = 'mb-xxsm mt-0 css-93svrw el6ke055').string
        # Get date and job title
        date_and_job = post.find('span', class_ = 'authorInfo').text        
        # Get pros and cons
        pros = post.find('span', {'data-test': 'pros'}).string
        cons = post.find('span', {'data-test': 'cons'}).string
        # Get shapes for Recommend, CEO approval, Business outlook for a single post
        other_scores = {'Recommend': '',
                       'CEO Approval': '',
                       'Business Outlook': ''}
        bar_shapes = post.find('div', class_ = 'd-flex my-std reviewBodyCell recommends css-1y3jl3a e1868oi10')
        for i, element in  enumerate(bar_shapes.find_all('svg')):
            other_scores[list(other_scores)[i]] = shape_styles[element['class'][1]]
        #Initating row for dataframe 
        post_data = {'date_and_job': date_and_job,
                     'post_title': post_title,
                     'status': status,
                     'pros': pros,
                     'cons': cons,
                     'Recommend': other_scores['Recommend'],
                     'CEO Approval': other_scores['CEO Approval'],
                     'Business Outlook': other_scores['Business Outlook']}
        # Getting ratings
        main_rating, subratings = scrape_ratings(post)
        post_data['main_rating'] = main_rating
        for key, value in subratings.items():
            post_data[key] = value
             
        #Populating the dataframe
        df = df.append((post_data),
                        ignore_index=True)
    return df
        
def scrape_all_pages(url): # Would like to be able to scrape 5 years back, you can try to use date in date_and_job column
    """
    Takes link of first setted (english, recent) reviews, scrapes it and 
    goes automatically to next pages scrapes them etc
    """
    domain_page_url = 'https://www.glassdoor.com/Reviews/'
    filter_url = '.htm?sort.sortType=RD&sort.ascending=false&filter.iso3Language=eng&filter.employmentStatus=PART_TIME&filter.employmentStatus=REGULAR&filter.employmentStatus=INTERN'
    first_page_base = url.replace(domain_page_url, '').replace(filter_url, '')
    
    df = pd.DataFrame()
    page = 1
    while page < 3:
        next_page = domain_page_url + first_page_base + '_P' + str(page) + filter_url
        driver.get(next_page)
        time.sleep(random.uniform(7, 13))
        df_page = single_page_scraper(driver.page_source)
        df = df.append(df_page, ignore_index=True)
        page +=1
        
    return df
    
    
   
#To remove overlay 
# driver.execute_script("""
# javascript:(function(){
#   document.getElementsByClassName('hardsellOverlay')[0].remove();
#   document.getElementsByTagName("body")[0].style.overflow = "scroll";
#   let style = document.createElement('style');
#   style.innerHTML = `
#     #LoginModal {
#       display: none!important;
#     }
#   `;
#   document.head.appendChild(style);
#   window.addEventListener("scroll", function (event) {
#     event.stopPropagation();
#   }, true);
# })();
# """)    
    
    
    
    
    