
import os
import sys
sys.path.insert(0, 'spaCy-training')
import comparison, jobdesc_parser
from jobspy import scrape_jobs
import pandas as pd
import requests

def get_location():
    url = 'http://ip-api.com/json/'
    data = requests.get(url).json()
    city = data['city']
    country = data['country']
    return city, country

def convert_country(api_country):
    country_map = {
        'Czechia': 'Czech Republic',
        'The Netherlands': 'Netherlands',
        'United States': 'USA',
        'United Kingdom': 'UK',
    }

    if api_country in country_map:
        return country_map[api_country]
    return api_country

city, api_country = get_location()
accepted_country = convert_country(api_country)


def main(jobdesc, cv):
    result, name, keywords, similarity = comparison.total_score(jobdesc, cv)
    return result, name, keywords, similarity

def job_search_params(jobdesc):
    details = jobdesc_parser.job_desc_details(jobdesc)
    city, api_country = get_location()
    accepted_country = convert_country(api_country)
    role = details['occupation']
    return city, accepted_country, role


def jobs(city, country, title):
    jobs: pd.DataFrame = scrape_jobs(
        site_name=["indeed"],
        search_term=title,
        distance=10,
        location=city,
        results_wanted=5,
        country_indeed=country,
        verbose=0
    )
    if os.path.isfile("databases/jobs.csv") == True:
        jobs.to_csv("databases/jobs.csv", mode='a', sep=',', index=False)
    else:
        jobs.to_csv("databases/jobs.csv", sep=',', index=False)
    
    csv = pd.read_csv('databases/jobs.csv')

    columns = ['job_url', 'title', 'company', 'location', 'job_type', 'date_posted', 'min_amount', 'max_amount', 'currency']
    description = csv['description']
    selected_columns_df = csv[columns]
    return selected_columns_df, description
    