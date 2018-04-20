import requests
import json
from datetime import datetime
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
        'Entities' INTEGER,
        'SearchDate' TEXT
        )
    '''
    cur.execute(create_keyword_table)
    create_entity_table = '''
        CREATE TABLE 'Entities' (
        'Id' INTEGER PRIMARY KEY,
        'Label' TEXT NOT NULL,
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
    cur.execute(create_link_table)
    conn.commit()
    conn.close()

def get_dbpedia_data(keyword):
    keyword = keyword.lower()
    page_url = "http://dbpedia.org/fct/facet.vsp?qxml=%3C%3Fxml%20version%3D%221.0%22%20encoding%3D%22UTF-8%22%20%3F%3E%3Cquery%20inference%3D%22%22%20same-as%3D%22%22%20view3%3D%22%22%20s-term%3D%22%22%20c-term%3D%22%22%20agg%3D%22%22%3E%3Ctext%3E{}%3C%2Ftext%3E%3Cview%20type%3D%22text-d%22%20limit%3D%2240000%22%20offset%3D%220%22%20%2F%3E%3C%2Fquery%3E".format(keyword.replace(" ","%20"))
    if keyword in CACHE_DICTION:
        main_html = CACHE_DICTION[keyword]
    else:
        query_pages_html = []
        print("Searching {} on dbpedia...".format(keyword))
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
    dbpedia_html_list = []
    for element in entity_elemnts:
        title = element.find(class_="describe")["title"]
        if title.split(":")[0] == "dbr": #this ensures that only dbr and not wikidata entities are scraped
            href_attr = element.find("a")["href"]
            entity_url = "http://dbpedia.org{}".format(href_attr)
            if entity_url in CACHE_DICTION:
                entity_html = CACHE_DICTION[entity_url]
            else:
                print("Extracting entities...s")
                entity_html_response_object = requests.get(entity_url)
                entity_json_obj = json.dumps(entity_html_response_object.text)
                CACHE_DICTION[entity_url]=json.loads(entity_json_obj)
                dumped_json_cache = json.dumps(CACHE_DICTION)
                fw = open(CACHE_FNAME,"w")
                fw.write(dumped_json_cache)
                fw.close()
                entity_html = CACHE_DICTION[entity_url]
            entity_soup = BeautifulSoup(entity_html,'html.parser')
            dbpedia_url = entity_soup.find(class_='page_resource_info').find("a")["href"]
            if dbpedia_url in CACHE_DICTION:
                dbpedia_html = CACHE_DICTION[dbpedia_url]
            else:
                dbpedia_html_response_object = requests.get(dbpedia_url)
                dbpedia_json_obj = json.dumps(dbpedia_html_response_object.text)
                CACHE_DICTION[dbpedia_url]=json.loads(dbpedia_json_obj)
                dumped_json_cache = json.dumps(CACHE_DICTION)
                fw = open(CACHE_FNAME,"w")
                fw.write(dumped_json_cache)
                fw.close()
                dbpedia_html = CACHE_DICTION[dbpedia_url]
            dbpedia_html_list.append(dbpedia_html)
    conn = sqlite.connect(DB_NAME)
    cur = conn.cursor()
    #later add an if else section to give users the option to update the table
    add_to_keyword_table = '''
    INSERT INTO 'Keywords' (Keyword, Entities, SearchDate)
    VALUES (?,?,?)
    '''
    add_params = []
    add_params.append(keyword)
    add_params.append(len(dbpedia_html_list))
    add_params.append(datetime.now().strftime("%x"))
    cur.execute(add_to_keyword_table, add_params)
    conn.commit()
    conn.close()
    return dbpedia_html_list

def generate_db_entity_data(dbpedia_html_list):
    conn = sqlite.connect(DB_NAME)
    cur = conn.cursor()
    existing_ids = []
    existing_id_statement = "SELECT Id FROM Entities"
    rows = cur.execute(existing_id_statement)
    for row in rows:
        existing_ids.append(row[0])
    entity_dict = {} #putting info into a dictionary ensures that ids are unique, since dictionary keys must be unique
    for dbpedia_html in dbpedia_html_list:
        try:
            dbpedia_soup = BeautifulSoup(dbpedia_html,'html.parser')
            desc = dbpedia_soup.find(class_="lead").string
            label = dbpedia_soup.find(class_="page-header").find("a").string
            url = dbpedia_soup.find(class_="page-header").find("a")["href"]
            id = dbpedia_soup.find(property="dbo:wikiPageID").string
            entity_dict[id] = {
                "desc":desc,
                "label":label,
                "url":url
                }
        except:
            print("Entity missing some element, skipping.")
        try:
            subjectrow = dbpedia_soup.find(href="http://purl.org/dc/terms/subject")
            subjects = subjectrow.parent.parent.find_all(class_="literal")
        except:
            subjects = []
        subj_list = []
        for subject in subjects:
            label = subject.find("small").next_sibling[1:]
            uri = subject.find("a")["href"]
            subj_list.append((label,uri))
        entity_dict[id]["subjects"] = subj_list
        try:
            points = dbpedia_soup.find(property = "georss:point").string
            entity_dict[id]["lat"] = points.split()[0]
            entity_dict[id]["lon"] = points.split()[1]
        except:
            pass
    for key in entity_dict:
        if key not in existing_ids:
            params = [key,
                entity_dict[key]["label"],
                entity_dict[key]["url"],
                entity_dict[key]["desc"]
                ]
            insert_entities = '''
            INSERT INTO 'Entities'
            VALUES (?,?,?,?)
            '''
            cur.execute(insert_entities, params)
        if len(entity_dict[key]['subjects']) == 0:
            print("{} has no subjects".format(key))
        else:
            for subject in entity_dict[key]['subjects']:
                params = [key,subject[1],subject[0]]
                subject_statement = '''
                INSERT INTO 'Links' (EntityId, LinkUrl, LinkLabel)
                VALUES (?,?,?)
                '''
                cur.execute(subject_statement, params)
            print("{} links were added for {}".format(len(entity_dict[key]['subjects']),key))
        try:
            params = [key, entity_dict[key]['lat'], entity_dict[key]['lon']]
            Locations_statement = '''
            INSERT INTO 'Locations' (EntityId, Latitude, Longitude)
            VALUES (?,?,?)
            '''
            cur.execute(Locations_statement,params)
        except:
            print("{} is not a location".format(key))
    conn.commit()
    conn.close()

class Entity():
    def __init__(self, entity_tuple):
        self.label = entity_tuple[1]
        self.url = entity_tuple[2]
        self.desc = entity_tuple[3]
        self.id = entity_tuple[0]

    def getsubject(self, subject_tup_list):
        self.subjects = subject_tup_list
        self.subjectcount = len(subject_tup_list)

    def getcoordinates(self, coordinates_tuple):
        self.lat = coordinates_tuple[0]
        self.lon = coordinates_tuple[1]

    def __str__(self):
        return "{}: {}".format(self.label, self.desc)

def generate_entities_list(keyword):
    conn = sqlite.connect(DB_NAME)
    cur = conn.cursor()
    find_entities = '''
        SELECT Id, Label, Url, Description
        FROM Entities
        WHERE Description LIKE "%{}%"
    '''.format(keyword)
    rows = cur.execute(find_entities)
    entities_obj_list = []
    for row in rows:
        entities_obj_list.append(Entity(row))
    for entity in entities_obj_list:
        find_links = '''
            SELECT LinkUrl, LinkLabel
            FROM Links
            WHERE EntityId = {}
        '''.format(entity.id)
        rows = cur.execute(find_links).fetchall()
        entity.getsubject(rows)
    for entity in entities_obj_list:
        find_places = '''
            SELECT Latitude, Longitude
            FROM Locations
            WHERE EntityId = {}
        '''.format(entity.id)
        result = cur.execute(find_places).fetchall()
        if len(result)>0:
            entity.getcoordinates(result[0])
    conn.close()
    return entities_obj_list

def get_sorted_objects(entities_obj_list, sortby='name', sortorder='desc'):
    rev = (sortorder == 'desc')
    if sortby == 'name':
        sorted_objects = sorted(entities_obj_list, key= lambda x: x.label, reverse=rev)
    elif sortby == 'relations':
        sorted_objects = sorted(entities_obj_list, key= lambda x: x.subjectcount, reverse=rev)
    else:
        sorted_objects = sorted(entities_obj_list, key= lambda x: x.id, reverse=rev)
    return sorted_objects

if __name__ == "__main__":
    #create_database()
    #Give option to work with existing data or get new data
    # sample_pages = get_dbpedia_data("Shanghai Book City")
    # if len(sample_pages) > 0:
    #     generate_db_entity_data(sample_pages)
    sample = generate_entities_list("Gate")
    # sorted = get_sorted_objects(sample, 'relations', 'asc')
    # for item in sorted:
    #     print(item)
    sorted2 = get_sorted_objects(sample, 'relations', 'desc')
    for item in sorted2:
        print(item)
