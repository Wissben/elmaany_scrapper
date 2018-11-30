import nltk
import re
import sqlite3
from sqlite3 import Error
import pprint
import json
nltk.data.path.append("/media/weiss/Data/nltk_data")


file = open("dbjson.json",'r')
data = json.load(file)


def name_exists(dic,name):
    for k in dic:
        if(k==name):
            return True
    return False

def postag_exists(dic,postag):
    for k in dic:
        if(k==postag):
            return True
    return False


def update_entry(dic,entry):
    name = entry['name']
    if(name_exists(dic,name)):
        if(postag_exists(dic[name],entry['posTag'])):
            dic[name][entry['posTag']] = dic[name][entry['posTag']] + entry['defs']
            dic[name][entry['posTag']] =list(set(dic[name][entry['posTag']]))
        else:
            dic[name][entry['posTag']]=list(set(entry['defs']))
    else:
        print(name)
        dic[name]={entry['posTag']:entry['defs']}


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


def select_task_by_priority(conn, priority):
    """
    Query tasks by priority
    :param conn: the Connection object
    :param priority:
    :return:
    """
    cur = conn.cursor()
    cur.execute('SELECT root,word,meaning from WordsTable WHERE root is not "" and explination is "(معجم الغني)";')

    rows = cur.fetchall()
    for row in rows:
        match = nltk.re.search("^(\(.+?\))\.(.+)", row[2])
        if(match):
            obj = {'name': row[0], 'posTag': match.group(1), 'defs': [x[2:] for x in match.group(2).split("|")][1:]}
            # pprint.pprint(obj)
            update_entry(data, obj)
        # pprint.pprint(match)



    # pprint.pprint(rows)
    return rows

def main():
    database = "/home/weiss/APKs/almaany/assets/databases/AlmaanyArArFinal_NEW.db"

    # create a database connection
    conn = create_connection(database)
    with conn:
        print("1. Query task by priority:")
        rows = select_task_by_priority(conn, 1)
        writeToJSONFile("./","dbjson",data)




def writeToJSONFile(path, fileName, data):

    filePathNameWExt = './' + path + '/' + fileName + '.json'
    with open(filePathNameWExt, 'w',encoding='utf8') as fp:
        json.dump(data, fp,indent=6,ensure_ascii=False)
        fp.close()


main()

