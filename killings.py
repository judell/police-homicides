import bs4
import requests
from bs4 import BeautifulSoup

import sys
import codecs
sys.stdout = codecs.getwriter('utf8')(sys.stdout)

import re
import datetime, time

import traceback

base = 'http://en.wikipedia.org/wiki/List_of_killings_by_law_enforcement_officers_in_the_United_States,_'

months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

states = [
  'Alabama',
  'Alaska',
  'Arizona',
  'Arkansas',
  'California',
  'Colorado',
  'Connecticut',
  'Delaware',
  'Florida',
  'Georgia',
  'Hawaii',
  'Idaho',
  'Illinois',
  'Indiana',
  'Iowa',
  'Kansas',
  'Kentucky',
  'Louisiana',
  'Maine',
  'Maryland',
  'Massachusetts',
  'Michigan',
  'Minnesota',
  'Mississippi',
  'Missouri',
  'Montana',
  'Nebraska',
  'Nevada',
  'New Hampshire',
  'New Jersey',
  'New Mexico',
  'New York',
  'North Carolina',
  'North Dakota',
  'Ohio',
  'Oklahoma',
  'Oregon',
  'Pennsylvania',
  'Rhode Island',
  'South Carolina',
  'South Dakota',
  'Tennessee',
  'Texas',
  'Utah',
  'Vermont',
  'Virginia',
  'Washington',
  'West Virginia',
  'Wisconsin',
  'Wyoming'
  ]

report = ""
logfile = ""
_states = []

#http://stackoverflow.com/questions/753052/strip-html-from-strings-in-python

from HTMLParser import HTMLParser

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

def log(s):
    global logfile
    print s
    logfile += s + '\n'

def log_traceback():
  global logfile
  logfile += ''.join(traceback.format_stack()) + '\n'
  
def process_page(pagename):
    try:
        log('processing ' + pagename)
        page = get_page(pagename)
        soup = BeautifulSoup(page)
        table = soup.find('table', { 'class': 'wikitable' })
        rows = table.findAll('tr')
        for row in rows[1:]:
            process_row(pagename,row)
    except:
        log('error with ' + pagename)
        log_traceback()

def process_row(pagename,row):
    global report, _states
    try:
        cells = row.findAll('td')
        date = cells[0].text
        date = date.replace(u'\u2011','-')
        ptime = time.strptime(date, '%Y-%m-%d')
        place = cells[2].text

        m = re.search( '([\w\s\.]+)\s*\(([\w\s\.]*)', place)  # Florida (Jacksonville)
        if m is not None and len(m.groups()) is 2:            
            place = m.groups()[1] + ', ' + m.groups()[0]      # normalize to Jacksonville, Florida
        city_state = place.split(',')
        city = ''

        if len(city_state) is 2:        # Jacksonville, Florida
            city = city_state[0]
            state = city_state[1]
        else:
            state = city_state[0]

        state = state.strip()

        if state not in _states:
            _states.append(state)
        
        city = city.strip()

        if state not in states:
            log(state + " not a state")
            return

        if len(city_state) is 2:
            value = date + ',' + state + ',' + city
        else:                         
            state = city_state[0]            
            value = date + ','  + state

        log(value)
        report += value + '\n'

    except:
        log('error with ' + pagename + ' ' + row.text)
        log_traceback()
    
def get_page(pagename):
    url = base + pagename
    r = requests.get(url)
    log(str(r.status_code) + ': ' + url)
    log(r.encoding)
    return r.text

by_year_start = 2009
by_year_end = 2011

by_month_start = 2012
by_month_end = 2014

for year in range(by_year_start, by_year_end + 1, 1):
    process_page(str(year))

for year in range(by_month_start, by_month_end + 1, 1):
  for month in months:
      process_page(month + '_' + str(year))

if len(states) is not len(_states):
    diff = set(states) - set(_states)
    log( 'list of unrepresented states: ' + ','.join(list(diff)) )

f = open('report.csv','w')
f.write(report.encode('utf-8'))
f.close()

f = open('log.txt','w')
f.write(logfile.encode('utf-8'))
f.close()

"""
patterns for extracting citation urls

source:

<sup id="cite_ref-2">

dest:

<li id="cite_note-2">
...
<span class="citation web">

<a href="...">
"""