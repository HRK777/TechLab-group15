#Packages
from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import time
import re

#Get all month links
##set the months
months_2019 = ["October", "November", "December"]
months_2020 = ["January", "February", "March", "April", "May"]

##join months & years to a list of urls
end_urls = [("/2019/"+month+"/") for month in months_2019] + [("/2020/"+month+"/") for month in months_2020]
base_url = 'https://www.goodreads.com/book/popular_by_date'

urls = [base_url + end_url for end_url in end_urls]

#define functions

def getPage(url):
    html = urlopen(url)
    Soup = BeautifulSoup(html.read().decode('utf-8'), 'html.parser')
    return Soup

def getBookElements(Soup):
    book_elements = Soup.find_all('tr', itemtype = 'http://schema.org/Book')
    return book_elements

def getMonth(book_elements, url):
    df_overview = pd.DataFrame(None)
    for book in book_elements:
        #id

        #date
        res = re.findall(r'/(\d{4})/([A-Z][a-z]+)', url)
        date = res[0]
        #rank
        rank = book.find('td', class_ = "number").text.strip()
        #title: 
        title = book.find('a', class_ = 'bookTitle')
        title_name = title.text.strip()
        #titlelink:
        title_link = title.attrs['href'].strip()
        #book_id
        ##1. find action button
        action_tag = book.find('div', class_ = 'wtrUp wtrLeft')
        ##2. find book_id
        id_tag = action_tag.find('input', {'id': 'book_id', 'name': 'book_id'})
        book_id = id_tag.attrs['value']
        #author
        author = book.find('a', class_ = "authorName")
        author_name = author.text.strip()
        author_link = author.attrs['href'].strip()
        #rating stats
        rating = book.find('span', class_ = 'minirating').text.strip()
        
        #fill in the dataframe
        temp = pd.DataFrame(
                {
                    'book_id': [book_id],
                    'rank': [rank],
                    'title': [title_name],
                    'title_link': [title_link],
                    'author_name': [author_name],
                    'author_link': [author_link],
                    'publ_date': [date],
                    'ratingstats': [rating]
                })
        
        df_overview = pd.concat([df_overview, temp])
        
    return df_overview   


#loop over all months and create final dataframe
df_overall = pd.DataFrame(None)
for url in urls:
    Soup = getPage(url)
    books = getBookElements(Soup)
    df_month = getMonth(books, url)
    
    df_overall = pd.concat([df_overall, df_month])

    print(f'following url scraped: {url}')
    time.sleep(1)
    
df_overall.to_csv('df_overall.csv')
print(df_overall)
