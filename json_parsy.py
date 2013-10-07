#!/usr/bin/env python

'''
Parse JSON data, put content into separate html files, whose names will take the form "alias".html
The files will be organized according to month and year
'''

import sys
import json
import os.path
import re
import datetime
import time

def main():
    #read in data
    json_unclean_file_obj = open(sys.argv[1], 'rU')
    json_clean_string = clean_json(json_unclean_file_obj)
    json_data = json.loads(json_clean_string)
    json_unclean_file_obj.close()
    #parse json
    for data in json_data:
        try:
            t = time.strptime(data["modified"], "%Y-%m-%d %H:%M:%S")
        except ValueError:
            t = time.strptime(data["created"], "%Y-%m-%d %H:%M:%S")
        file_path = os.path.join('content', str(t.tm_year), str(t.tm_mon), data["alias"]+'.html')
        dir = os.path.dirname(file_path)
        if not os.path.exists(dir):
            os.makedirs(dir)
        structured_html = add_head_and_body(data)
        html_file = open(file_path , 'w')
        html_file.write(structured_html.encode("utf-8"))
        html_file.close()

def clean_json(doc_text):
    sarray = []
    for line in doc_text:
        sarray.extend(line.split())
    clean_string_json = " ".join(sarray)
    new_clean_string = clean_string_json.replace("\'", "\\'")
    return new_clean_string

def add_head_and_body(html):
    '''
    Add necessary html tags to generate a page.
    '''
    prepend = "<html><head><meta http-equiv=\"content-type\" content=\"text/html; charset=utf-8\" /><title>" + html["title"] + "</title></head><body>"
    h1 = "<h1>" + html["title"] + "</h1>"
    author = get_author(html["introtext"])
    author_html = '<p class="author">' + author + '</p>'
    body = author_html + html["fulltext"] or html["introtext"]
    return prepend + h1 + body  + "</body></html>"


def get_author(html):
    '''
    Return the raw author name.
    '''
    if html:
        regex = '\<h6\>(.*?)\</h6\>'
        match = re.search(regex, html)
        if match:
            return remove_html_tags(match.group(1))
    return "Los Editores"

def remove_html_tags(data):
    '''
    Do final cleaning on author field. Strip tags, whitespace and '*'.
    '''
    p = re.compile(r'<.*?>')
    return p.sub('', data).strip().rstrip('*')

if __name__ == "__main__":
	main()
