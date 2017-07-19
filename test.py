from __future__ import print_function
import re
import time
import unittest

try:
    raw_input = input
except NameError:
    pass

from salesforce_bulkipy import SalesforceBulkipy, CsvDictsAdapter


class SalesforceBulkTest(unittest.TestCase):
    def __init__(self, testName, endpoint, sessionId):
        super(SalesforceBulkTest, self).__init__(testName)
        self.endpoint = endpoint
        self.sessionId = sessionId

    def setUp(self):
        self.jobs = []

    def tearDown(self):
        if hasattr(self, 'bulk'):
            for job_id in self.jobs:
                print("Closing job: %s" % job_id)
                self.bulk.close_job(job_id)

    def test_raw_query(self):
        bulk = SalesforceBulkipy(self.sessionId, self.endpoint)
        self.bulk = bulk

        job_id = bulk.create_query_job("Contact")
        self.jobs.append(job_id)
        self.assertIsNotNone(re.match("\w+", job_id))

        # test the job state method
        self.assertEqual(bulk.job_state(job_id=job_id), 'Open')

        batch_id = bulk.query(job_id, "Select Id,Name,Email from Contact Limit 1000")
        self.assertIsNotNone(re.match("\w+", batch_id))

        while not bulk.is_batch_done(job_id, batch_id):
            print("Job not done yet...")
            print(bulk.batch_status(job_id, batch_id))
            time.sleep(2)

        results = bulk.get_all_results_for_batch(batch_id=batch_id, job_id=job_id)
        results = list(list(x) for x in results)

        self.assertTrue(len(results) > 0)
        self.assertTrue(len(results[0]) > 0)
        self.assertIn('"', results[0][0])

        results = bulk.get_batch_result_iter(batch_id=batch_id, job_id=job_id)
        results = list(results)

        self.assertTrue(len(results) > 0)
        self.assertTrue(len(results[0]) > 0)
        self.assertIn('"', results[0][0])

    def test_csv_query(self):
        bulk = SalesforceBulkipy(self.sessionId, self.endpoint)
        self.bulk = bulk

        job_id = bulk.create_query_job("Account")
        self.jobs.append(job_id)
        self.assertIsNotNone(re.match("\w+", job_id))

        batch_id = bulk.query(job_id, "Select Id,Name,Description from Account Limit 10000")
        self.assertIsNotNone(re.match("\w+", batch_id))
        bulk.wait_for_batch(job_id, batch_id, timeout=120)

        results = bulk.get_all_results_for_batch(batch_id=batch_id, job_id=job_id, parse_csv=True)
        results = list(list(x) for x in results)

        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0][0], ['Id', 'Name', 'Description'])
        self.assertTrue(len(results[0]) > 3)

        results = bulk.get_batch_result_iter(batch_id=batch_id, job_id=job_id, parse_csv=True)
        results = list(results)

        self.assertTrue(len(results) > 3)
        self.assertTrue(isinstance(results[0], dict))
        self.assertIn('Id', results[0])
        self.assertIn('Name', results[0])
        self.assertIn('Description', results[0])

    def test_csv_upload(self):
        batches_count = 5
        object_type = 'Contact'
        bulk = SalesforceBulkipy(self.sessionId, self.endpoint)
        self.bulk = bulk

        job_id = bulk.create_insert_job(object_type)
        self.jobs.append(job_id)
        self.assertIsNotNone(re.match("\w+", job_id))

        batch_ids = []
        content = open("example.csv").read()

        for i in range(batches_count):
            batch_id = bulk.query(job_id, content)
            self.assertIsNotNone(re.match("\w+", batch_id))
            batch_ids.append(batch_id)

        for batch_id in batch_ids:
            bulk.wait_for_batch(job_id, batch_id, timeout=120)

        self.results = None

        def save_results1(rows, failed, remaining):
            self.results = rows

        for batch_id in batch_ids:
            flag = bulk.get_upload_results(job_id, batch_id, callback=save_results1)
            self.assertTrue(flag)
            results = self.results
            self.assertTrue(len(results) > 0)
            self.assertTrue(isinstance(results, list))
            # self.assertEqual(results[0], UploadResult('Id','Success','Created','Error'))
            self.assertEqual(len(results), 3)

        self.results = None
        self.callback_count = 0

        def save_results2(rows, failed, remaining):
            self.results = rows
            self.callback_count += 1

        batch = len(results) / 3
        self.callback_count = 0
        flag = bulk.get_upload_results(job_id, batch_id, callback=save_results2, batch_size=batch)
        self.assertTrue(self.callback_count >= 3)

    def test_delete(self):
        # this assumes there are items in SalesForce with the format 'test_name_%'
        where_clause = "Name like 'test_name_%'"
        object_type = 'Contact'

        self.bulk = SalesforceBulkipy(self.sessionId, self.endpoint)
        job_id = self.bulk.create_delete_job(object_type)
        self.jobs.append(job_id)
        result = self.bulk.bulk_delete(job_id=job_id, object_type=object_type, where=where_clause)

        # Note: verify manually in SalesForce that the expected objects were deleted
        self.assertTrue(len(result) > 0)
        self.assertIsNotNone(re.match("\w+", result[0]))

    def test_post_bulk_batch(self):
        # modify these according to your SalesForce setup
        object_type = 'Contact'
        records_to_insert = [
            {
                'Name': 'test_name_1',
            },
            {
                'Name': 'test_name_2',
            }
        ]

        self.bulk = SalesforceBulkipy(self.sessionId, self.endpoint)
        job = self.bulk.create_insert_job(object_type, contentType='CSV')
        csv_iter = CsvDictsAdapter(iter(records_to_insert))
        batch = self.bulk.post_bulk_batch(job, csv_iter)
        self.bulk.wait_for_batch(job, batch)
        self.bulk.close_job(job)

        # Note: verify manually in SalesForce that the records were added

    def test_split_csv(self):
        self.bulk = SalesforceBulkipy(self.sessionId, self.endpoint)
        test_csv = (
            'Name,Description',
            '"test1","test 1"',
            '"test2","test 2"',
            '"test3","test 3"',)
        test_csv = '\n'.join(test_csv)
        expected_result = [
            'Name,Description\n"test1","test 1"\n',
            'Name,Description\n"test2","test 2"\n"test3","test 3"'
        ]

        results = self.bulk.split_csv(test_csv, 2)

        self.assertIn(expected_result[0], results)
        self.assertIn(expected_result[1], results)

    def test_bulk_csv_upload(self):
        test_csv = (
            'Name',
            'test_name_1',
            'test_name_2',
            'test_name_3',
            'test_name_4',
            'test_name_5'
        )
        test_csv = '\n'.join(test_csv)
        object_type = 'Contact'

        self.bulk = SalesforceBulkipy(self.sessionId, self.endpoint)
        job_id = self.bulk.create_insert_job(object_type)
        self.jobs.append(job_id)
        batch_ids = self.bulk.bulk_csv_upload(job_id, test_csv, 2)
        for batch in batch_ids:
            self.bulk.wait_for_batch(job_id, batch)
        self.assertTrue(len(batch_ids) == 3)

        # Note: check manually that the items were created in SalesForce


if __name__ == '__main__':
    username = raw_input("Salesforce username: ")
    password = raw_input("Salesforce password: ")
    security_token = raw_input("Salesforce security token: ")

    sessionId, host = SalesforceBulkipy.login_to_salesforce_using_username_password(
        username=username,
        password=password,
        security_token=security_token,
        sandbox=True)

    suite = unittest.TestSuite()
    suite.addTest(SalesforceBulkTest("test_csv_upload", host, sessionId))
    unittest.TextTestRunner().run(suite)
