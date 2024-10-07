import csv
from dotenv import load_dotenv
import os

load_dotenv()


def get_website_pairs(max_num: int = 20):
    '''
    Get the pairs of websites to analyze. The list is read from the TOP_WEBSITE_LIST environment variable.
    Return a dictionary of website URL to (English) website name.
    '''
    top_website_list = os.environ.get("TOP_WEBSITE_LIST")

    website_list = {}
    with open(top_website_list, 'r') as f:
        reader = csv.reader(f)
        next(reader)
        for i, row in enumerate(reader):
            if max_num and i >= max_num:
                break
            name, url = row[1], row[2]
            website_list[url] = name
    return website_list


def get_website_list(varient='alexa', max_num: int = 20):
    '''
    Get the list of websites to analyze. The list is read from the TOP_WEBSITE_LIST environment variable.
    Return a list of website URLs.
    '''
    top_website_list = os.environ.get("TOP_WEBSITE_LIST")

    if varient == 'alexa':
        website_list = []
        with open(top_website_list, 'r') as f:
            reader = csv.reader(f)
            next(reader)
            for i, row in enumerate(reader):
                if max_num and i >= max_num:
                    break
                name, url = row[1], row[2]
                website_list.append(url)
        return website_list
    elif varient == 'tranco':
        website_list = []
        with open(top_website_list, 'r') as f:
            reader = csv.reader(f)
            for i, row in enumerate(reader):
                if max_num and i >= max_num:
                    break
                url = row[1]
                website_list.append(url)
        return website_list
    else:
        raise ValueError(f"Unknown varient: {varient}")
