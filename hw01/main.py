'''
1st Assignment

[x] - single page crawling (20pt)
[x] - full crawling (30pt)
[x] - storing data in db (30pt)
[x] - report (20pt)
'''

from bs4 import BeautifulSoup
import urllib.request
import timeit
import re
import datetime as dt
from pymongo import MongoClient

def check_db_exists():
    host = "localhost"
    port = 27017
    mongo = MongoClient(host, port)
    naver_news_db = mongo["naver_news_db"] #create db
    naver_news_info = naver_news_db["naver_news_info"] #create collection
    #naver_news_info.delete_many({})    
    return naver_news_info

def retrieve_naver_news_info(query, page_nr):
    page_code = 1 #first page; second page = 11 => += 10; max = 41
    rows_to_add = []
    for i in range(page_nr):
        URL = 'https://search.naver.com/search.naver?query='+query+'&where=news&ie=utf8&sm=tab_pge&sort=0&start='+str(page_code) 
        print('Attempting to collect page '+str(page_code//10+1)+'...')
        parsed_news_info_rows = (parse_info_from_soup(URL))
        print("Created {} new rows.".format(len(parsed_news_info_rows)))
        rows_to_add.append(parsed_news_info_rows)
        page_code += 10
    return rows_to_add

'''
#NOTE: Retrieve the news area (div.news_area) to parse out the info
news_press = div.info_group > a.info press > (after span.thumb_box)
news_date = div.info_group > span.info 
news_title = a.news_tit
news_description = div.news_dsc > div.dsc_wrap > a.apit_txt_lines dsc_txt_wrap
'''
def parse_dt_from_str(str_val):
    time_dt = re.findall(r'\d+', str_val)
    try:
        time_interval = int(time_dt[0])
    except ValueError:
        raise Exception('Not parseable data: %s'%str_val)
    
    if '시간' in str_val:
        td = dt.timedelta(minutes=time_interval*60)
    elif '분' in str_val:
        td = dt.timedelta(minutes=time_interval)
    elif '일' in str_val:
        td = dt.timedelta(days = time_interval)
    elif '초' in str_val:
        td = dt.timedelta(seconds=time_interval)
    else:
        raise Exception('Time format does not exist: %s' %str_val)
    
    parsed_dt = dt.datetime.now().replace(microsecond=0) - td
    return parsed_dt


def find_all_dates(soup_elm):
    str_date = soup_elm.find_all('span',{'class','info'})[-1].text
    converted_date = parse_dt_from_str(str_date)
    if converted_date:
        return converted_date
    else:
        return 'na'

def find_all_press(soup_elm):
    press = soup_elm.find('a',{'class':'press'}).text
    exclude = r'\s선정|언론사'
    if press:
        press = re.sub(exclude, '', press)
        return press
    else:
        return 'na'

def find_all_titles(soup_elm):
    title = soup_elm.find('a', {'class': 'news_tit'}).text
    if title:
        return title
    else:
        return 'na'

def parse_info_from_soup(URL):
    response = urllib.request.urlopen(URL)
    status_code = response.getcode() 
    print('status code:', status_code)
    if status_code == 200:
        print("Ready to collect.")
        soup = BeautifulSoup(response.read(), 'html.parser')
        news_area = soup.find_all('div',{'class':'news_area'})
        rows_to_add  = []
        for area in news_area:
            title = find_all_titles(area)
            date = find_all_dates(area)
            press = find_all_press(area)
            new_row = {'news_title':title, 'news_date':date, 'news_press':press}
            if new_row:
                rows_to_add.append(new_row)
        print('Collection finished.')
        return rows_to_add
    else:
        print("Connection error:",status_code)

def main():
    naver_news_info_collection = check_db_exists()
    if naver_news_info_collection:
        start = timeit.default_timer()
        print('start',start)
        new_rows = retrieve_naver_news_info('LH',5)
        for rows in new_rows:
            naver_news_info_collection.insert_many(rows)
        end = timeit.default_timer() -start
        print('end',end)

if __name__ == '__main__':
    main()


