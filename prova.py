import openpyxl
import pandas as pd
import snscrape.modules.twitter as sntwitter
#import spacy
import streamlit as st
import datetime
import re
import xlsxwriter
from io import BytesIO
import requests


url = 'https://github.com/nicolorosso/prova/blob/main/Parlamento_sito_ADL.xlsx?raw=true'
myfile = requests.get(url)

import concurrent.futures

# Load the Italian language model
# Page layout
## Page expands to full width
st.set_page_config(layout="wide")
#---------------------------------#
# Title

st.title('Monitoraggio attività stakeholder su Twitter')
st.markdown("""
Questa app offre la possibilità di monitorare i tweet più rilevanti!
""")
#---------------------------------#
# About
expander_bar = st.expander("Come usare l'app")
expander_bar.markdown("""
1. Seleziona la data di inizio e fine ricerca 
2. Inserisci i nomi utenti per la ricerca (Luigi Marattin diventa marattin)
3. Inserisci le parole chiave per la tua ricerca
4. Premi il tasto invio
""")


#---------------------------------#
# Page layout (continued)
## Divide page to 3 columns (col1 = sidebar, col2 and col3 = page contents)
col1 = st.sidebar
col2, col3 = st.columns((2,1))

#---------------------------------#
# Sidebar + Main panel
col1.header('Opzioni Ricerca')


## Sidebar
account = pd.read_excel(myfile.content)
#governo= pd.read_excel(r'C:\Users\nickr\Downloads\account_governo_twitter.xlsx', sheet_name = 'Sheet1', engine='openpyxl')

account['username'] = account['LINK PAGINA TWITTER'].str.split('/').str[-1]
account['username'] = account['username'].str.split('?').str[0]
account = account.dropna(subset=['username'])
account['nome_cognome'] = account['NOME'].str.cat(account['COGNOME'], sep=' ')
account = account.reset_index()

#governo['LINK PAGINA TWITTER'] = governo['LINK PAGINA TWITTER'].str.split('/').str[-1]
#governo['LINK PAGINA TWITTER'] = governo['LINK PAGINA TWITTER'].str.split('?').str[0]


start_date = st.sidebar.date_input("Start date", datetime.date(2013, 1, 1))
start_date = str(start_date)
end_date = st.sidebar.date_input("End date", datetime.date(2025, 1, 31))
end_date = str(end_date)
#users = st.sidebar.text_input('Scrivere il nome utenti separato da una virgola:', "")

# Create a list of the 'nome_cognome' values
options = account['nome_cognome'].tolist()

# Display the dropdown menu and store the selected values in a list called 'selected_options'
#selected_options_indexes = st.sidebar.multiselect('Scegli il politico', options)
#selected_options = account.loc[account['nome_cognome'].isin(selected_options_indexes), 'username'].tolist()
container = st.sidebar.container()
#all = st.sidebar.checkbox("Select all")

# Set the index of the account dataframe to nome_cognome
account = account.set_index('nome_cognome')

# Add a checkbox to select all options
select_all = st.sidebar.checkbox("Seleziona tutti")

# Use nome_cognome as the options for the multiselect
if select_all:
    selected_options = account.index.tolist()
    selected_usernames = account.loc[selected_options, 'username']
    selected_usernames = selected_usernames[selected_usernames != ''].tolist()
else:
    selected_options = st.sidebar.multiselect(
        "Seleziona uno o più Stakeholder:",
        account.index.tolist())
    selected_usernames = account.loc[selected_options, 'username'].tolist()


# Get the corresponding usernames for the selected options
#selected_usernames = account.loc[selected_options, 'username'].tolist()
topics = list((num) for num in st.sidebar.text_input('Scrivere le parole chiave separate da una virgola:', "").strip().split(","))

numero = st.sidebar.slider('Numero di Tweet', 10, 100, 25)


with st.sidebar:
    with st.form(key='my_form'):
        submit_button = st.form_submit_button(label='Invia')

#-----------------------------------------------------------------------------------------#
@st.cache(suppress_st_warning=True)
def scrape_tweets_for_user(topic, username, since, until):
    tweets_list1 = []
    for i, tweet in enumerate(sntwitter.TwitterSearchScraper(f"{topic} from:{username} since:{since} until:{until}").get_items()):
        if i>100:
            break
        tweets_list1.append([tweet.user.displayname,
                            tweet.date,
                            tweet.rawContent,
                             tweet.id,
                            tweet.url
                              ])
    return tweets_list1

def scraper(parole, users, since, until):
    tweets_list1 = []
    with concurrent.futures.ProcessPoolExecutor(30) as executor:
        results = [executor.submit(scrape_tweets_for_user, p, n, since, until) for p in parole for n in users]
        for future in concurrent.futures.as_completed(results):
            tweets_list1.extend(future.result())

    df = pd.DataFrame(tweets_list1, columns=['Nome Utente',
                                              'Data',
                                              'Text',
                                             'Tweet ID',
                                              'URL'
                                              ])
    if df.empty:
        st.error("Non sono stati trovati Tweet con le parole chiave selezionate!", icon="🚨")
    else:
        df['Data'] = df['Data'].dt.date
        df.sort_values(by='Data', ascending=False, inplace=False)
        st.dataframe(df)

        # Write files to in-memory strings using BytesIO
        output = BytesIO()


        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            # Write each dataframe to a different worksheet.
            df.to_excel(writer, sheet_name='Dati Scraper', index=False)
            writer.save()

            st.download_button(
                label="Download foglio Excel",
                data=output.getvalue(),
                file_name="scraper.xlsx",
                mime="application/vnd.ms-excel")


list_of_users = account['username'].tolist()

since = "2022-12-24"
until = "2022-12-29"

list_of_parole = ['Fondazione De Gasperi', 'Lorenzo Malagola']
if submit_button:
    scraper(topics, selected_usernames, start_date, end_date)


#if governo_button:
    #scrape_tweets(topics, users, selected_options, start_date, end_date, governo_button)



#---------------------------------------------------------------------------------
#print(account['username'].dropna())
#print(selected_options)
