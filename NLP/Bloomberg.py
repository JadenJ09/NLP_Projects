import requests
import csv
from bs4 import BeautifulSoup

url = 'https://www.bloomberg.com/news/articles'
response = requests.get(url)

soup = BeautifulSoup(response.content, 'html.parser')

articles = soup.find_all('article', class_='bb-arc-article')

with open('bloomberg_news.csv', mode='w', newline='') as csv_file:
    fieldnames = ['title', 'summary', 'url', 'date']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    writer.writeheader()

    for article in articles:
        title = article.find('h2', class_='lede-text-only__highlight').text.strip()
        summary = article.find('div', class_='lede-text-only__highlight').text.strip()
        url = article.find('a')['href']
        date = article.find('time')['datetime']
        writer.writerow({'title': title, 'summary': summary, 'url': url, 'date': date})
