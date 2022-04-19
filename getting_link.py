#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 19 15:06:14 2022

@author: corentin
"""
# IMports
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
import random
import time
import pandas as pd


# Main scraping function
def getting_company_reviews_urls_bs(companies):
    """
    Takes a list of company names as input and returns the url of the review 
    section of each company in a dataframe
    """
    driver = webdriver.Chrome('/Users/corentin/Documents/chromedriver')
    time.sleep(5)
    url = 'https://www.glassdoor.com/Reviews/index.htm'
    search_bar_xpath = '//*[@id="KeywordSearch"]'
    df = pd.DataFrame({'company': [], 'link': []})
    domain = 'https://fr.glassdoor.be'

    
    for company in companies:
        try:
            #Searching for the company
            driver.get(url)
            time.sleep(random.uniform(2, 4))
            company_search = driver.find_element_by_xpath(search_bar_xpath)
            company_search.send_keys(company)
            time.sleep(random.uniform(1, 2))
            company_search.send_keys(Keys.ENTER)

            #Going on the first company's page
            time.sleep(random.uniform(2, 4))
            driver.find_element_by_xpath('//*[@id="MainCol"]/div/div[1]/div/div[1]/div/div[2]/h2/a').click()
            # soup = BeautifulSoup(driver.page_source, 'lxml')
            # first_company_box = domain + soup.find('a', class_ = 'sqLogoLink').get('href')

            #Going in the reviews section of the page and getting the url
            time.sleep(random.uniform(2, 4))
            # sauce = requests.get(first_company_box)
            # soup = BeautifulSoup(sauce.text, 'lxml')
            soup = BeautifulSoup(driver.page_source, 'lxml')
            reviews_url = domain + soup.find('a', class_ = 'd-flex align-items-center pt-std css-1qnp674 e16bqfyh1').get('href')
            #reviews_url = domain + soup.find('a', {'data-test': 'reviewSeeAllLink'}).get('href')
            #reviews_url = soup.find('a', class_ 'eiCell cell reviews ').get('href')
            print('Reviews for ' + company + reviews_url)
            print('Search for the company succesful')

            #Populating the dataframe
            df = df.append({'company': company,
                            'link': reviews_url},
                           ignore_index=True)
        except:
            continue
    
    return df

## Code to remove annoying login overlay 
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

# Trying 
df = pd.read_csv('listsp500')