import requests
import json
from bs4 import BeautifulSoup
import sqlite3 as sqlite
import codecs
import sys

sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)

CACHE_FNAME = "dbpedia-cache.json"
DB_NAME = "dbpedia.sqlite"

try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()
except:
    CACHE_DICTION = {}

def create_database():
    f = open(DB_NAME,"w")
    f.close()
    conn = sqlite.connect(DB_NAME)
    cur = conn.cursor()
    create_keyword_table = '''
        CREATE TABLE 'Keywords' (
        'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
        'Keyword' TEXT NOT NULL,
        'Entities' INTEGER
        )
    '''
    cur.execute(create_keyword_table)
    create_entity_table = '''
        CREATE TABLE 'Entities' (
        'Id' INTEGER PRIMARY KEY,
        'Label' TEXT NOT NULL,
        'Type' TEXT,
        'Url' TEXT NOT NULL,
        'Description' TEXT
        )
    '''
    cur.execute(create_entity_table)
    create_place_table = '''
        CREATE TABLE 'Locations' (
        'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
        'EntityId' INTEGER NOT NULL,
        'Latitude' INTEGER NOT NULL,
        'Longitude' INTEGER NOT NULL
        )
    '''
    cur.execute(create_place_table)
    create_link_table = '''
        CREATE TABLE 'Links' (
        'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
        'EntityId' INTEGER NOT NULL,
        'LinkUrl' TEXT NOT NULL,
        'LinkLabel' TEXT NOT NULL
        )
    '''
    conn.commit()
    conn.close()


def get_dbpedia_data(keyword):
    page_url = "http://dbpedia.org/fct/facet.vsp?qxml=%3C%3Fxml%20version%3D%221.0%22%20encoding%3D%22UTF-8%22%20%3F%3E%3Cquery%20inference%3D%22%22%20same-as%3D%22%22%20view3%3D%22%22%20s-term%3D%22%22%20c-term%3D%22%22%20agg%3D%22%22%3E%3Ctext%3E{}%3C%2Ftext%3E%3Cview%20type%3D%22text-d%22%20limit%3D%2240000%22%20offset%3D%220%22%20%2F%3E%3C%2Fquery%3E".format(keyword.replace(" ","%20"))
    if keyword in CACHE_DICTION:
        main_html = CACHE_DICTION[keyword]
    else:
        query_pages_html = []
        main_response_object = requests.get(page_url)
        main_page_json_obj = json.dumps(main_response_object.text)
        CACHE_DICTION[keyword] = json.loads(main_page_json_obj)
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close()
        main_html = CACHE_DICTION[keyword]
    main_soup = BeautifulSoup(main_html, 'html.parser')
    table_element = main_soup.find("tbody")
    entity_elemnts = table_element.find_all('tr')
    entity_html_list = []
    for element in entity_elemnts:
        title = element.find(class_="describe")["title"]
        if title.split(":")[0] == "dbr": #this ensures that only dbr and not wikidata entities are scraped
            href_attr = element.find("a")["href"]
            entity_url = "http://dbpedia.org()".format(href_attr)
            if entity_url in CACHE_DICTION:
                entity_html = CACHE_DICTION[entity_url]
            else:
                entity_html_response_object = requests.get(entity_url)
                entity_json_obj = json.dumps(entity_html_response_object.text)
                CACHE_DICTION[entity_url]=json.loads(entity_json_obj)
                dumped_json_cache = json.dumps(CACHE_DICTION)
                fw = open(CACHE_FNAME,"w")
                fw.write(dumped_json_cache)
                fw.close()
                entity_html = CACHE_DICTION[entity_url]
            entity_html_list.append(entity_html)
    conn = sqlite.connect(DB_NAME)
    cur = conn.cursor()
    #later add an if else section to give users the option to update the table
    update_keyword_table = '''
    INSERT INTO 'Keywords' (Keyword, Entities)
    VALUES (?,?)
    '''
    cur.execute(update_keyword_table,[keyword, len(entity_html_list)])
    conn.commit()
    conn.close()
    return entity_html_list

def generate_db_entity_data(entity_html_list):
    conn = sqlite.connect(DB_NAME)
    cur = conn.cursor()
    for entity_html in entity_html_list:
        entity_soup = BeautifulSoup(entity_html,'html_parser')
        desc = entity_soup.find(class_="subj_desc").string
        label = entity_soup.find(class_='page_resource_info').find("a").string
        url = entity_soup.find(class_='page_resource_info').find("a")["href"]
        id = entity_soup.find(property='dbo:wikiPageID').string
        insert_entities = '''
        INSERT INTO 'Entities'
        VALUES (?,?,NULL,?,?)
        '''
        cur.execute(insert_entities,[id,label,url,desc])
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_database()
    sample_pages = get_dbpedia_data("kowloon walled city")
    generate_db_entity_data(sample_pages)
