import requests
from config import API_KEY, START_DATE, END_DATE, LIMIT_RESULTS, PAGE_LIMIT, MANUFACTURER
from typing import Dict, List


def get_data(
        request_url: str,
        LIMIT_RESULTS: int = LIMIT_RESULTS,
        PAGE_LIMIT: int = PAGE_LIMIT
    ) -> List[Dict]:
    """
    executes a query on the FDA API.
    :param request_url: the url encoding the search
    :param LIMIT_RESULTS: the maximum number of results to be provided
    :param PAGE_LIMIT: the number of results per page
    :return: JSON results
    """

    results = list()

    # Iterate through pages to avoid timing out
    for page in range(LIMIT_RESULTS // PAGE_LIMIT):
        page_limiter = '&limit={}&skip={}'.format(PAGE_LIMIT, PAGE_LIMIT * page)
        url = request_url + page_limiter

        # Ideally add more error checking in case we get timed-out or another response
        data = requests.get(url).json()
        
        # Assuming here that each ingredient will be comma separated
        # technically this should be validated later to avoid entry errors
        # database errors.
        if 'results' in data.keys():
            results += [
                {
                    'year': entry['effective_time'][0:4],
                    'ingredients': entry['spl_product_data_elements'][0],
                    'n_ingredients': len(entry['spl_product_data_elements'][0].split(',')),
                    'drug_name': entry['openfda']['brand_name'][0],
                    'route': entry['openfda']['route'][0]
                } 
                for entry in data['results']
            ]

    return results


def make_request_url(
        START_DATE:str = START_DATE,
        END_DATE: str = END_DATE,
        MANUFACTURER:str = MANUFACTURER,
        API_KEY: str=API_KEY
    ) -> str:
    """
    produces a url for a query on the openFDA API.
    :param START_DATE: records initial date
    :param END_DATE: records end date
    :param MANUFACTURER: manufacturer queried
    :return: url string
    """
    # The search prefix conditions on the manufacturer being AZ
    if MANUFACTURER == 'ALL':
        MANUFACTURER = ''
    else:
        MANUFACTURER = 'openfda.manufacturer_name:"{}"'.format(MANUFACTURER)
    
    query = '&search=effective_time:[{}+TO+{}]{}'.format(
        START_DATE, END_DATE, MANUFACTURER
    )

    # adding constraints for having the name of the drug and route
    query += '+AND+_exists_:openfda.brand_name+AND+_exists_:openfda.route'

    return 'https://api.fda.gov/drug/label.json?api_key={}{}'.format(API_KEY, query)

