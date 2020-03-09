import get_labels
import unittest
import json


class TestGetData(unittest.TestCase):

    def setUp(self):
        return super().setUp()

    def test_make_request_url(self):
        """
        test the default query created by the make_request_url
        """
        MANUFACTURER = 'AZ'
        START_DATE = '20200307'
        END_DATE = '20200308'
        API_KEY = '1234'

        ground_truth = 'https://api.fda.gov/drug/label.json?api_key=1234'
        ground_truth += '&search=effective_time:[20200307+TO+20200308]openfda.manufacturer_name:"AZ"'
        ground_truth += '+AND+_exists_:openfda.brand_name+AND+_exists_:openfda.route'
        
        obtained = get_labels.make_request_url(
            START_DATE=START_DATE,
            END_DATE=END_DATE,
            MANUFACTURER=MANUFACTURER,
            API_KEY=API_KEY
        )

        self.assertEqual(obtained, ground_truth, 'obtained:{}, expected: {}'.format(obtained, ground_truth))

    def test_make_request_url_2(self):
        """
        test the default query created by the make_request_url for all manufacturers
        """
        MANUFACTURER = 'ALL'
        START_DATE = '20200307'
        END_DATE = '20200308'
        API_KEY = '1234'

        ground_truth = 'https://api.fda.gov/drug/label.json?api_key=1234'
        ground_truth += '&search=effective_time:[20200307+TO+20200308]'
        ground_truth += '+AND+_exists_:openfda.brand_name+AND+_exists_:openfda.route'
        
        obtained = get_labels.make_request_url(
            START_DATE=START_DATE,
            END_DATE=END_DATE,
            MANUFACTURER=MANUFACTURER,
            API_KEY=API_KEY
        )

        self.assertEqual(obtained, ground_truth, 'obtained:{}, expected: {}'.format(obtained, ground_truth))

    def test_get_data(self):
        """
        tests the data obtained against a query directly made using
        https://open.fda.gov/apis/drug/label/example-api-queries/
        """
        with open('tests/data/results.json', 'rt') as f:
            ground_truth = json.load(f)

        url = get_labels.make_request_url()
        results = get_labels.get_data(request_url=url, LIMIT_RESULTS=2, PAGE_LIMIT=1)
        
        self.assertEqual(results, ground_truth)