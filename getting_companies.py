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
from selenium.webdriver.common.keys import Keys



# S&P500 companies
def get_sp500():
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    tables = pd.read_html(url)
    table = tables[0]
    table.to_csv('listsp500')
    print('List of sp500 companies successfully imported')

# Stoxx Europe 600 companies
def get_euro600():
    url = 'https://www.stoxx.com/index-details?symbol=SXXP'
    driver = webdriver.Chrome('/Users/corentin/Documents/chromedriver')
    time.sleep(5)
    driver.get(url)