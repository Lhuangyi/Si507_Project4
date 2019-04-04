import requests, json, csv
from bs4 import BeautifulSoup
from advanced_expiry_caching import Cache
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

START_URL = "https://www.nps.gov/index.htm"
FILENAME = "national_sites_cache.json"

PROGRAM_CACHE = Cache(FILENAME)


def access_page_data(url):
    data = PROGRAM_CACHE.get(url)
    if not data:
        data = requests.get(url).text
        PROGRAM_CACHE.set(url, data)
    return data


main_page = access_page_data(START_URL)

main_soup = BeautifulSoup(main_page, features="html.parser")
list_of_states = main_soup.find('ul', {'class': 'dropdown-menu SearchBar-keywordSearch'})
all_links = list_of_states.find_all('a')

states_pages = []
for l in all_links:
    state_page_data = access_page_data('https://www.nps.gov/' + l.get('href'))
    soup_of_page = BeautifulSoup(state_page_data, features="html.parser")
    ul_sites = soup_of_page.find('ul', {'id': 'list_parks'})
    li_sites = ul_sites.find_all('li', {'class': 'clearfix'})
    states_pages.append(li_sites)


def wash_data(a_string):
    washed_data = ""
    for i in range(len(a_string) - 1):
        string_combination = a_string[i] + a_string[i + 1]
        if string_combination.isalpha():
            if string_combination.isupper():
                washed_data += string_combination + ', '
    return washed_data[:-2]


sites_information = [['ParkName', 'Type', 'Description', 'Location', 'State']]
for item in states_pages:
    for every_li in item:
        site_information = []
        if every_li.find('h2').get_text():
            site_name = every_li.find('h2').get_text()
            site_information.append(site_name)
        else:
            site_information.append('None')
        if every_li.find('a').get_text():
            site_type = every_li.find('a').get_text()
            site_information.append(site_type)
        else:
            site_information.append('None')
        if every_li.find('p').get_text():
            site_discription = every_li.find('p').get_text()[1:]
            site_information.append(site_discription)
        else:
            site_information.append('None')
        if every_li.find('h4').get_text():
            site_location = every_li.find('h4').get_text()
            site_information.append(site_location)
        else:
            site_information.append('None')
        site_states = wash_data(site_location)
        site_information.append(site_states)
        sites_information.append(site_information)

with open("national_sites.csv", "w", encoding='utf8', newline='') as mycsv:
    writer = csv.writer(mycsv)
    writer.writerows(sites_information)
