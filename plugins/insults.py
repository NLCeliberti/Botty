from bs4 import BeautifulSoup
import requests
import urllib.request

def insult():
    url = "http://www.insultsgenerator.com/"
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
    headers = {'User-Agent': user_agent}
    soup = BeautifulSoup(requests.get(url).text, 'lxml')
    return soup.b.text
