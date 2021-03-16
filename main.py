'''
1st Assignment

[x] - single page crawling (20pt)
[x] - full crawling (30pt)
[ ] - storing data in db (30pt)
[ ] - report (20pt)
'''

from bs4 import BeautifulSoup
import urllib.request
import timeit
import os

def crawl_naver_news(query, page_nr):
    page_code = 1 #first page; second page = 11 => += 10; max = 41
    news_titles_all_pages = []
    for i in range(page_nr):
        URL = 'https://search.naver.com/search.naver?query='+query+'&where=news&ie=utf8&sm=tab_pge&sort=0&start='+str(page_code) 
        print('Attempting to collect page '+str(page_code//10+1)+'...')
        news_titles_all_pages.append(get_text(URL))
        page_code += 10
    return news_titles_all_pages

def get_text(URL):
    response = urllib.request.urlopen(URL)
    status_code = response.getcode() 
    print('status code:', status_code)
    if status_code == 200:
        print("Ready to collect.")
        soup = BeautifulSoup(response.read(), 'html.parser')
        news_title_links = soup.find_all('a', {'class': 'news_tit'})
        news_titles = []
        for item in news_title_links:
            news_titles.append(item.get('title'))
        print('Collection finished.')
        return news_titles
    else:
        print("Connection error:",status_code)

def main():
    start = timeit.default_timer()
    print('start',start)
    res =crawl_naver_news('LH',5)
    print(*res, sep='\n')
    end = timeit.default_timer() -start
    print('end',end)

if __name__ == '__main__':
    main()


