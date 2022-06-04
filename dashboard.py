import dash
import pandas as pd
import numpy as np
import random
from datetime import datetime, date
import matplotlib.pyplot as plt
import itertools # For slicing dictionaries

# For interactive components like graphs, dropdowns, or date ranges.
from dash import dcc 
# For HTML tags
from dash import html
from dash.dependencies import Input, Output

# Text analysis
import nltk
from nltk.corpus import stopwords
from nltk.sentiment.vader import SentimentIntensityAnalyzer #For social media text sentiment
from gensim.utils import simple_preprocess
from collections import Counter

# For graphics
import plotly
import plotly.express as px 
import plotly.graph_objs as go
from plotly.offline import plot
from plotly.subplots import make_subplots #For subplots

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server # NEW

#Get data
df = pd.read_csv('data/combined_reviews.csv', index_col=0)
#Rename index
df.index.name = 'date'
#Convert to datetime.index
df.index = pd.to_datetime(df.index)

# Exclude from analysis companies with too litle reviews
print(df.groupby('company')['main_rating'].count())
df = df[df['company'].isin(['accenture', 'deloitte', 'ey', 'kpmg', 'pwc', 'bain_and_company'])]

df_original = df.copy() # For visu 2
df_text = df.copy() # For visu 3 review level
df_text2 = df.copy() # For visu 3 company level

# Visualization 1:
def get_month(date):
    """
    Takes a timestamp and returns in what year and month it is but all values in a given month happend the first
    """
    return datetime(date.year, date.month, 1)
df['month_dates'] = df.index.map(get_month)

star_columns = ['main_rating', 'Work/Life Balance', 'Culture & Values', 'Diversity & Inclusion', 'Career Opportunities', 'Compensation and Benefits', 'Senior Management']

monthly_mean_ratings = df.groupby(['company', 'month_dates'])[star_columns].mean()

monthly_mean_ratings.reset_index(inplace=True)
companies = monthly_mean_ratings['company'].unique()

# Splitting df into dfs by company
dfs_companies = {}
for company in companies:
    dfs_companies[company] = monthly_mean_ratings[monthly_mean_ratings['company'] == company]
    
# For each company df compute the rolling mean
dfs_companies_rollingmeans = {}
for company, df in dfs_companies.items(): 
    rolling_values = df.rolling(window=6, min_periods=3).mean()
    dates = df['month_dates']
    dfs_companies_rollingmeans[company] = pd.concat([rolling_values, dates], axis=1)
    
# Merge the dataframes back again
df_rolling_means = pd.DataFrame()
for company, df in dfs_companies_rollingmeans.items(): 
    df['company'] = company
    df_rolling_means = df_rolling_means.append(df)

# Visualization 2:
df_recommendations = df_original[['Business Outlook', 'CEO Approval', 'Recommend', 'company']]

def replace_symbols_numbers(row):
    """
    Function to be mapped on column composed of O, V, - and X
    It will replace these values by np.nan, 1, 0 and -1 respectively.
    """
    if row == 'O':
        return np.nan
    elif row == 'V':
        return 1
    elif row == '-':
        return 0
    elif row == 'X':
        return -1
    else: 
        return 'missing'
    
df_recommendations_clean = pd.DataFrame()

for name, column in df_recommendations.iloc[:, :-1].items():
    df_recommendations_clean[name] = column.map(replace_symbols_numbers)

df_recommendations_clean['company'] = df_recommendations['company']

recommendation_scores = df_recommendations_clean.groupby('company').mean()*100

# Visualization 3:
def get_main_words(text):
    """
    Function to be mapped to pros and cons and returns a column containing the main words for each obs
    """
    return simple_preprocess(text)

df_text['pros_main_words'] = df_text['pros'].map(get_main_words)
df_text['cons_main_words'] = df_text['cons'].map(get_main_words)

def get_frequency(word_list):
    """
    Function to be mapped to list of main words for pros and cons, returns the frequency of these words
    """
    freqs = Counter()
    for word in word_list:
        freqs.update(word.lower().split())
    return freqs

df_text['pros_main_words_freq'] = df_text['pros_main_words'].map(get_frequency)
df_text['cons_main_words_freq'] = df_text['cons_main_words'].map(get_frequency)

# Remove these words for the wordcloud
stopwords = set(stopwords.words('english'))

def remove_stopwords(word_list):
    """
    Function to be mapped, expects dictionnary of words, returns dictionarry without stopwords
    """
    to_remove = []
    for word in word_list.keys():
        if word in stopwords:
            to_remove.append(word)
    for word in to_remove:
        del(word_list[word])
    return word_list

df_text['pros_main_words_freq'] = df_text['pros_main_words_freq'].map(remove_stopwords)
df_text['cons_main_words_freq'] = df_text['cons_main_words_freq'].map(remove_stopwords)

# Dictionary-Based Sentiment Analysis
def sentiment_polscores(text):
    """
    Function to be mapped, expects text, returns polarity scores
    """
    sid = SentimentIntensityAnalyzer()
    polarity = sid.polarity_scores(text)['compound']
    return polarity

df_text['pros_sentiment_polscore'] = df_text['pros'].map(sentiment_polscores)
df_text['cons_sentiment_polscore'] = df_text['cons'].map(sentiment_polscores)

reg_df = df_text[['Work/Life Balance',
                  'Culture & Values',
                  'Career Opportunities',
                  'Compensation and Benefits',
                  'Senior Management',
                  'pros_sentiment_polscore',
                  'cons_sentiment_polscore']]
reg_df = reg_df.dropna()

#Merge words for pros and cons separately for each company
blobs = {}
for q in ['pros', 'cons']:
    blobs[q] = {}
    for company in df_text2['company'].unique():
        blobs[q][company] = df_text2[df_text2['company'] == company][q].str.cat(sep=' ').replace('\r\n', ' ')
        
#Simple preprocesses
for key in blobs.keys():
    for company, value in blobs[key].items():
        blobs[key][company] = simple_preprocess(value)
        
#get frequencies of words
for key in blobs.keys():
    for company, value in blobs[key].items():
        freqs = Counter()
        for word in value:
            freqs.update(word.lower().split())
        blobs[key][company] = freqs

#remove stopwords
for key in blobs.keys():
    for company, words in blobs[key].items():
        to_remove = []
        for word in words:
            if word in stopwords:
                to_remove.append(word)
        for word in to_remove:
            del(words[word])
            
#sort by lowest values first
blobs_ordered_high = {}
for key in blobs.keys():
    blobs_ordered_high[key] = {}
    for company, words in blobs[key].items():
        freq_all_words = sum(words.values())
        relative_freq_sorted = {k: v/freq_all_words for k, v in sorted(blobs[key][company].items(), key=lambda item: item[1], reverse=True)}
        blobs_ordered_high[key][company] = relative_freq_sorted
        
# Only 20 most frequent words
for key in blobs_ordered_high.keys():
    for company in blobs[key].keys():
        blobs_ordered_high[key][company] = dict(itertools.islice(blobs_ordered_high[key][company].items(), 12))
        
# Dashboard
rating_names = ['Main rating', 'Work/Life Balance', 'Culture & Values', 'Diversity & Inclusion', 'Career Opportunities', 'Compensation and Benefits', 'Senior Management']
company_names = ['Accenture', 'Bain & Company', 'Deloitte', 'EY', 'KPMG', 'PwC']

# Initializing the dash object
app = dash.Dash(external_stylesheets=external_stylesheets) # Always include

# Application layout: 
app.layout = html.Div(
    children=[
        html.H1(children='Employee satisfaction dashboard consultancy firms'),
        
        # Explanation
        dcc.Markdown('''
            This is a dashboard for students to compare employee satisfaction and wellbeing among big consultancy firms in Belgium and Luxembourg.
        '''),
        
        # First graph
        dcc.Markdown('''
            ### A comparison between companies over time
        '''),
        
        # Explanations for graph
        dcc.Markdown('''
            Please select the rating(s) of interest and a time period.
        '''),
        
        html.Div([
            html.Label('Rating:'),
            dcc.Dropdown(
                id='rating',
                options=[{'label': rating_names[i], 'value': star_columns[i]} for i in range(len(star_columns))],
                value='Work/Life Balance',
                placeholder='Rating',
                multi=True
                )
            ],
            style={'width': '15%', 'display': 'inline-block', 'margin-bottom': '20px'}),
        
        dcc.Markdown(''' '''),
        
        html.Div([
            html.Label('Time Period:'),
            dcc.DatePickerRange(
                id='dates',
                min_date_allowed=date(2012, 1, 1),
                max_date_allowed=date(2022, 5, 1),
                initial_visible_month=date(2015, 1, 1),
                start_date=date(2019, 1, 1),
                end_date=date(2022, 5, 1)
                )
            ],
        style={'width': '30%', 'display': 'inline-block', 'margin-bottom': '20px'}),
        
        dcc.Markdown(''' '''),
        
        html.Div([
            html.Label('Companies:'),
            dcc.Checklist(
                id='companies',
                options=[{'label': company_names[i], 'value': companies[i]} for i in range(len(companies))],
                value=['accenture', 'deloitte'],
                inline=True
                )
            ],
        style={'width': '35%', 'display': 'inline-block', 'margin-bottom': '20px'}),
        
        dcc.Graph(
            id='ratings_plot',
            style={'width': '60%'}#, 'display': 'inline-block', 'margin-bottom': '20px'}   
        ),
        
        # Second graph
        dcc.Markdown('''
            ### Business outlook, CEO Approval and Would recommend
        '''),
        
        # Explanation
        dcc.Markdown('''
            Please select which company(ies) you are interested in.
            This visualization compares different companies on multiple aspects, namely:
            - How employees feel about the business outlook of the company
            - How employees feel about the CEO, or the senior management in general
            - If employees would recommend the firm to friends
            Note: The y-axis does not represent frequency but is a score.
        '''),
        
        dcc.Checklist(
            id='companies2',
            options=[{'label': company_names[i], 'value': companies[i]} for i in range(len(companies))],
            value=['ey', 'deloitte', 'accenture'],
            inline=True
        ),
        
        dcc.Graph(
            id='recommendations_plot',
            style={'width': '60%', 'display': 'inline-block', 'margin-bottom': '20px'}   
        ),
        
        # Third graph
        dcc.Markdown('''
            ### A comparison in review word-use for different companies
        '''),
        
        dcc.Markdown('''
            This last visualization allows you to compare the most frequently used words in employee reviews.
            You can select two companies and compare what words are the most used in the pros and in the cons separately.
        '''),
        
        html.Div([
            html.Label('Company 1:'),
            dcc.Dropdown(
                id='company3',
                options=[{'label': company_names[i], 'value': companies[i]} for i in range(len(companies))],
                value='kpmg',
                placeholder='company',
                multi=False
                )
            ],
            style={'width': '15%', 'display': 'inline-block', 'margin-bottom': '20px'}),
        
        html.Div([
            html.Label('Company 2:'),
            dcc.Dropdown(
                id='company4',
                options=[{'label': company_names[i], 'value': companies[i]} for i in range(len(companies))],
                value='accenture',
                placeholder='company',
                multi=False
                )
            ],
            style={'width': '20%', 'display': 'inline-block', 'margin-bottom': '20px'}),
        
        dcc.Markdown(''' '''),
        
        dcc.Graph(
            id='words_plot1',
            style={'width': '60%', 'display': 'inline-block', 'margin-bottom': '20px'}   
        ),
        
        dcc.Graph(
            id='words_plot2',
            style={'width': '60%', 'display': 'inline-block', 'margin-bottom': '20px'}   
        ),
        
        html.Div(id='test_tex')
    ]
)  

# --- NEW --- 
# callback decorator + a function that manipulates the data and returns a dictionary

@app.callback(
    dash.dependencies.Output('ratings_plot', 'figure'),
    dash.dependencies.Input('rating', 'value'),
    dash.dependencies.Input('companies', 'value'),
    dash.dependencies.Input('dates', 'start_date'),
    dash.dependencies.Input('dates', 'end_date'))

# def update_graph(input 1,input 2)

def update_graph(ratings, companies, start, end):
    if None in [companies, ratings, start, end]:
        return px.line()
    else: 
        df_companies = df_rolling_means[df_rolling_means['company'].isin(companies)]
        df_filtered_end = df_companies[df_companies['month_dates'] <= datetime.strptime(end, '%Y-%m-%d')]
        df = df_filtered_end[df_filtered_end['month_dates'] >=datetime.strptime(start, '%Y-%m-%d')]

        fig = px.line(df, 
                      x='month_dates', 
                      y=ratings, 
                      color="company", 
                      hover_name="company",
                      line_shape="spline", 
                      render_mode="svg",
                      labels={'month_dates': 'Date'})

        return fig
        
@app.callback(
    dash.dependencies.Output('recommendations_plot', 'figure'),
    dash.dependencies.Input('companies2', 'value'))

# def update_graph(input 1,input 2)

def update_barchart(companies2):
    if None in [companies2]:
        return go.Figure()
    else:
        # Prepare subplots for pros and cons
        fig = make_subplots(rows=1, cols=2)
        
        # Filter the data
        df_companies2 = recommendation_scores[recommendation_scores.index.isin(companies2)]
        
        #Create figure
        data = []
        for company in companies2:
            data.append(go.Bar(name=company, x=df_companies2.columns, y=df_companies2.loc[company]))
        
        fig = go.Figure(data=data)
        fig.update_layout(barmode='group')
        
        return fig
    
@app.callback(
    dash.dependencies.Output('words_plot1', 'figure'),
    dash.dependencies.Input('company3', 'value'))

# def update_graph(input 1,input 2)

def update_wordbars1(company3):
    if company3 is None:
        return go.Figure()
    else:
        fig = make_subplots(rows=1, cols=2)
        
        fig.add_trace(go.Bar(name='Pros', x=list(blobs_ordered_high['pros'][company3].values()), 
                             y=list(blobs_ordered_high['pros'][company3].keys()), orientation='h'), row=1, col=1)
        fig.add_trace(go.Bar(name='Cons', x=list(blobs_ordered_high['cons'][company3].values()), 
                             y=list(blobs_ordered_high['cons'][company3].keys()), orientation='h'), row=1, col=2)
        fig.update_layout(title_text=f"Pros & Cons for {company3}")
        
        return fig
    
@app.callback(
    dash.dependencies.Output('words_plot2', 'figure'),
    dash.dependencies.Input('company4', 'value'))

# def update_graph(input 1,input 2)

def update_wordbars2(company4):
    if company4 is None:
        return go.Figure()
    else:
        fig = make_subplots(rows=1, cols=2)
        
        fig.add_trace(go.Bar(name='Pros', x=list(blobs_ordered_high['pros'][company4].values()), 
                             y=list(blobs_ordered_high['pros'][company4].keys()), orientation='h'), row=1, col=1)
        fig.add_trace(go.Bar(name='Cons', x=list(blobs_ordered_high['cons'][company4].values()), 
                             y=list(blobs_ordered_high['cons'][company4].keys()), orientation='h'), row=1, col=2)
        fig.update_layout(title_text=f"Pros & Cons for {company4}")
        
        return fig
    
app.run_server() # simple function to run the app on a local server
