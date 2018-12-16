from statistics import mean

import nltk
import re
import sqlite3
from sqlite3 import Error
import pprint
import json
import  pyarabic.araby
nltk.data.path.append("/media/weiss/Data/nltk_data")



def name_exists(dic, name):
    for k in dic:
        if (k == name):
            return True
    return False


def postag_exists(dic, postag):
    for k in dic:
        if (k == postag):
            return True
    return False


def update_entry(dic, entry):
    name = entry['name']
    print(entry,"----\n")
    if (name_exists(dic, name)):

        if (postag_exists(dic[name], entry['posTag'])):
            dic[name][entry['posTag']] = dic[name][entry['posTag']] + entry['defs']
            dic[name][entry['posTag']] = list(set(dic[name][entry['posTag']]))
        else:
            dic[name][entry['posTag']] = list(set(entry['defs']))
    else:
        dic[name] = {entry['posTag']: entry['defs']}


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return None


def query(conn,dico,data):

    if(dico is "elghani"):
        cur = conn.cursor()
        cur.execute('SELECT  root,word,meaning,explination from WordsTable WHERE root is not "" and explination is "(معجم الغني)" ;')

        rows = cur.fetchall()
        for row in rows:
            match = nltk.re.search("^(\([^|]+?\)).+?(\|.+)", row[2])
            if (match):
                if(len(match.group(1))>0):
                    print(row[3])
                    obj = {'name': row[0], 'posTag': match.group(1), 'defs': [x[2:] for x in match.group(2).split("|")[1:]]}
                    update_entry(data, obj)
                else:
                    print(row[2])

    if(dico is "elra2id"):
        print("TODO")
        cur = conn.cursor()
        cur.execute(
            'SELECT  root,word,meaning,explination from WordsTable WHERE root is not "" and explination is "(معجم الرائد)";')

        for row in rows:
            match = nltk.re.search("(\([^\|]+?\))\.?\|(.+)", row[2])
            if (match):
                if (match.group(1)):
                    obj = {'name': row[0], 'posTag': match.group(1), 'defs': [x[2:] for x in match.group(2).split("|")]}
                    update_entry(data, obj)

    if (dico is "elwassit"):
        cur = conn.cursor()
        cur.execute(
            'SELECT  root,word,meaning,explination from WordsTable WHERE  explination is "(معجم الوسيط)";')

        rows = cur.fetchall()
        print(rows)
        for row in rows:
            obj = {'name': pyarabic.araby.strip_tashkeel(pyarabic.araby.strip_tatweel(row[1])), 'posTag': "Undefinied", 'defs': [x for x in row[2].split("|")]}
            update_entry(data, obj)
            # pprint.pprint(obj)




def writeToJSONFile(path, fileName, data):
    filePathNameWExt = './' + path + '/' + fileName + '.json'
    with open(filePathNameWExt, 'w', encoding='utf8') as fp:
        json.dump(data, fp, indent=6, ensure_ascii=False)
        fp.close()


def main(dico,data):
    database = "/home/weiss/APKs/almaany/assets/databases/AlmaanyArArFinal_NEW.db"

    # create a database connection
    conn = create_connection(database)
    with conn:
        query(conn,dico,data)
        writeToJSONFile("./", dico, data)

# elghani = open("elghani.json", 'r')
# elghani_data = json.load(elghani)
# print(len(elghani_data))
#
# elra2id= open("elra2id.json", 'r')
# elra2id_data = json.load(elra2id)
# print(len(elra2id_data))


# dicos =['elghani','elra2id','elwassit']
dicos=['elwassit']
for dico in dicos:
    dico_data = json.load(open(dico+".json", 'r'))
    print(len(dico_data))
    # main(dico,data=dico_data)
    # words = dico_data
    # exceeded = [(key, pos) for key in words for pos in words[key] if len(pos) >= 200 or len(key) >= 200]
    # print(exceeded)

