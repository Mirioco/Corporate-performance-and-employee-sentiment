#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 19 15:11:06 2022

@author: corentin
"""

# Imports
import pandas as pd
from bs4 import BeautifulSoup
import time
from selenium import webdriver



# S&P500 companies
def get_sp500():
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    tables = pd.read_html(url)
    table = tables[0]
    table.to_csv('listsp500')
    print('List of sp500 companies successfully imported')

# Stoxx Europe 600 companies
def get_euro600():
    
    # Intiate variables and get chromedriver to the right page
    df = pd.DataFrame({'name': [], 'supersector': [], 'country': [], 'link': []})
    url = 'https://www.stoxx.com/index-details?symbol=SXXP'
    driver = webdriver.Chrome('/Users/corentin/Documents/chromedriver')
    time.sleep(5)
    driver.get(url)
    components = driver.find_element_by_xpath('//*[@id="portlet_STOXXIndexDetailsportlet_WAR_STOXXIndexDetailsportlet"]/div/div/div/div[2]/div[1]/div/div/ul/li[2]/a')
    components.click()
    print('On components')
    
    # Get the table on the first page
    time.sleep(3)
    page = 1
    soup = BeautifulSoup(driver.page_source, 'lxml')
    table = soup.find('tbody', {'id': 'components-table-body'})
    rows = table.find_all('tr')
    print('Got rows')
    
    # Loop over all the pages
    while page <= 3:
        
        #Append name, link, supersector and country to df
        for row in rows:
            elements = row.find_all('td')
            name = elements[0].text.strip()
            link = elements[0].find('input').get('value')
            supersector = elements[1].text
            country = elements[2].text
            df = df.append({'name': name, 
                       'supersector': supersector, 
                       'country': country,
                       'link': link}, 
                      ignore_index=True)
            print(name)
        
        # Go to the next page
        driver.execute_script('window.scrollTo(0, 3865)')
        time.sleep(3)
        next_page = driver.find_element_by_xpath('//*[@id="paginator"]/div/div/ul/li[4]')
        next_page.click()
        page += 1
        print('Got on page ' + str(page))
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, 'lxml')
        table = soup.find('tbody', {'id': 'components-table-body'})
    rows = table.find_all('tr')
    
    return df
    # Sending df to csv
    #df.to_csv('liststoxx600')
    
listos = get_euro600() 

        
