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
import random
import time
import pandas as pd

# Get some links
df = pd.read_csv('data/liststoxx600.csv')
df.head()



# Set up
driver = webdriver.Chrome('/Users/corentin/Documents/chromedriver')
url = 'https://www.glassdoor.com/Reviews/index.htm'
search_bar_xpath = '//*[@id="KeywordSearch"]'
df = pd.DataFrame({'company': [], 'link': []})
domain = 'https://fr.glassdoor.be'


