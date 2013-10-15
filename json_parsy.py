#!/usr/bin/env python

'''
Parse JSON data, put content into separate html files, whose names will take the form "alias".html
The files will be organized according to month and year
'''
import sys
import json
import os.path
import re
import time
from pprint import pprint, pformat
from MySQLdb import connect

#VERSION = 1

def main():
    #read in data
    db = connect(host="localhost", db="intagdb",
            read_default_file="~/.my.cnf")
    db.set_character_set('utf8')
    #eliminate existing data, this script does everything.
    truncate_data(db)
    json_unclean_file_obj = open(sys.argv[1], 'rU')
    json_clean_string = clean_json(json_unclean_file_obj)
    json_data = json.loads(json_clean_string)
    json_unclean_file_obj.close()
    #keep track of aliases, since it's the pkey
    aliases = []
    for data in json_data:
        try:
            t = time.strptime(data["modified"], "%Y-%m-%d %H:%M:%S")
        except ValueError:
            t = time.strptime(data["created"], "%Y-%m-%d %H:%M:%S")
        data['date'] = time.strftime("%Y-%m-%d", t)
        parse_other_fields(data)
        remove_styling_and_empty_elements(data['body'])
        utf_encode(data)
        if data['alias'] not in aliases:
            insert_into_database(db, data)
            aliases.append(data['alias'])
        else:
            #don't insert duplicates, just let us know which ones they are
            print data['alias']
    db.commit()


def truncate_data(db):
    '''
    Remove everything from table.
    '''
    c = db.cursor()
    c.execute("DELETE FROM articles;");
    c.close()

def insert_into_database(db, data):
    '''
    Store data in the database.
    '''
    c = db.cursor()

    # weird encoding errors. this seems to fix them.
    c.execute('SET NAMES utf8;')
    c.execute('SET CHARACTER SET utf8;')
    c.execute('SET character_set_connection=utf8;')

    c.execute("""INSERT INTO articles VALUES (%s, %s, %s, %s, %s, %s)""", \
            (data['alias'], data['author'], data['title'], \
            data['intro_text'], data['body'], data['date']))

    c.close()


def utf_encode(data):
    '''
    Necessary.
    '''
    for k, v in data.items():
        if type(v) == str:
            data[k] = v.encode('utf-8')

    '''
    if data['alias'] == 'el-petroleo-del-yasuni-se-queda-bajo-tierra':
        global VERSION
        filename = "yasuni_{}".format(VERSION)
        f = open(filename,'w')
        f.write(pformat(data))
        VERSION += 1
    '''

def clean_json(doc_text):
    sarray = []
    for line in doc_text:
        sarray.extend(line.split())
    clean_string_json = " ".join(sarray)
    new_clean_string = clean_string_json.replace("\'", "\\'")
    return new_clean_string

def parse_other_fields(data):
    '''
    Add author, intro and body fields.
    '''
    if data['introtext'] and data['fulltext']:
        data['author'], data['intro_text'] = get_author_and_content(data["introtext"])
        data['body'] = data['fulltext']
    else:
        main_content = data['introtext'] or data['fulltext']
        data['author'], data['body'] = get_author_and_content(main_content)
        data['intro_text'] = ''
        #TODO: find a way to parse out an intro
        #TODO: replace <br /> with p tags

def get_author_and_content(intro, body=None):
    '''
    Return the raw author name.
    '''
    regex = '\<h6\>(.*?)\</h6\>(.*)'
    match = re.search(regex, intro)
    if match:
        author = remove_html_tags(match.group(1))
        body = match.group(2)
        return author, body
    return "Los Editores", intro

def remove_html_tags(data):
    '''
    Do final cleaning on author field. Strip tags, whitespace and '*'.
    '''
    p = re.compile(r'<.*?>')
    return p.sub('', data).strip().rstrip('*')

def remove_styling_and_empty_elements(html):
    html_no_inline_styling = re.sub(" style=\".*?\"", "", html)
    html_correct_img_paths = html_no_inline_styling.replace("http://intagnewspaper.org/images/", "../../../img/")
    return html_correct_img_paths

if __name__ == "__main__":
	main()
