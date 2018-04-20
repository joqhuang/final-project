import model
import sqlite3 as sqlite
import unittest

class TestCreateDB(unittest.TestCase):

    def test_init_db(self):
        try:
            model.create_database()
        except:
            self.fail()

    def test_populate_db(self):
        keyword = "Kowloon Walled City"
        html_list = model.get_dbpedia_data(keyword)
        model.generate_db_entity_data(html_list)
        conn = sqlite.connect(model.DB_NAME)
        cur = conn.cursor()
        statement = '''
            SELECT *
            FROM 'Keywords'
        '''
        rows = cur.execute(statement)
        tup_list = []
        for row in rows:
            tup_list.append(row)
        count = len(tup_list)
        self.assertNotEqual(count,0)
        statement = '''
            SELECT *
            FROM 'Entities'
            WHERE Description LIKE "%Kowloon Walled City%"
        '''
        rows = cur.execute(statement)
        tup_list = []
        for row in rows:
            tup_list.append(row)
        count = len(tup_list)
        bool = (count > 0)
        self.assertTrue(bool)
        statement = '''
            SELECT *
            FROM Entities
            WHERE Id = 1391000
        '''
        rows = cur.execute(statement)
        rows = rows.fetchall()
        expected_result = len(rows)
        self.assertEqual(expected_result,1)
        statement = '''
            SELECT COUNT(*)
            FROM Locations
        '''
        rows = cur.execute(statement)
        count = rows.fetchone()[0]
        bool = (count > 0)
        self.assertTrue(bool)
        conn.close()

    def test_no_results(self):
        conn = sqlite.connect(model.DB_NAME)
        cur = conn.cursor()
        keyword = "fasklfdjasf"
        html_list = model.get_dbpedia_data(keyword)
        statement = "SELECT Entities FROM Keywords"
        rows = cur.execute(statement)
        rows = rows.fetchall()
        keyword_count = len(rows)
        self.assertEqual(keyword_count,1)
        entity_count = rows[0][0]
        self.assertEqual(entity_count,0)
        statement = '''SELECT * FROM Entities WHERE Description LIKE "%fasklfdjasf%"'''
        cur.execute(statement)
        self.assertEqual(entity_count,0)
        conn.close()

class TestCreateClassObjects(unittest.TestCase):
    def setUp(self):
        keyword = "Kowloon Walled City"
        self.sample_obj_list = model.generate_entities_list(keyword)

    def test_objectlist(self):
        self.assertNotEqual(len(self.sample_obj_list),0)
        id_list = []
        for item in self.sample_obj_list:
            id_list.append(item.id)
            if item.id == 1391000:
                sample1 = item
            if item.id == 269024:
                sample2 = item
        self.assertIn(1391000,id_list)
        self.assertIn(269024,id_list)
        self.assertEqual(sample1.id,1391000)
        self.assertEqual(sample1.label,"Lok Fu Station")
        self.assertEqual(sample1.url,"http://dbpedia.org/resource/Lok_Fu_Station")
        self.assertEqual(sample1.subjectcount,6)
        self.assertEqual(sample2.id,269024)
        self.assertEqual(sample2.label,"Kowloon Walled City")
        self.assertEqual(sample2.url,"http://dbpedia.org/resource/Kowloon_Walled_City")
        self.assertEqual(sample2.lat,22.332280555555556)
        self.assertEqual(sample2.lon,114.19027777777778)

if __name__ == '__main__':
    unittest.main()
