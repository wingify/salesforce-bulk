# Salesforce Bulkipy

A Python library for the Salesforce Bulk API (that actually works)

## Changes over [salesforce-bulk](https://github.com/heroku/salesforce-bulk)

The [salesforce-bulk](https://github.com/heroku/salesforce-bulk) library was used to export 18k records to [Wingify](https://github.com/wingify)'s Salesforce system. Even though the library was super useful, it's broken, not maintained anymore and was a pain to work with while figuring out the bugs. [@bholagabbar](https://github.com/bholagabbar) decided to fix all the issues faced and release a new, usable library **salesforce-bulkipy**. This library has been tested successfully on our Salesforce Sandbox.

* Added support for [Two-Factor Authentication](https://developer.salesforce.com/docs/atlas.en-us.identityImplGuide.meta/identityImplGuide/security_require_two-factor_authentication.htm) by routing authentication via [simple-salesforce](https://github.com/simple-salesforce/simple-salesforce)
* Added support for [Salesforce Sandbox](https://test.salesforce.com)
* Added support for parsing unicode characters in CSV
* Fixed various other bugs

**salesforce-bulkipy** will be actively maintained, unlike salesforce-bulk

## Installation

**```sudo pip install salesforce-bulkipy```** (not yet available)

Incase your setup fails, you may have a few essential tools missing. Try
`sudo apt-get install build-essential libssl-dev libffi-dev python-dev`


## Authentication

To access the Bulk API, you need to authenticate a user into Salesforce. There are 2 possible ways to achieve this. These methods work irrespective of whether your organisation has [Two-Factor Authentication](https://developer.salesforce.com/docs/atlas.en-us.identityImplGuide.meta/identityImplGuide/security_require_two-factor_authentication.htm) enabled or not, so that's a massive overhead taken care of.

##### The code samples shown read credentials from a [config.properties](https://docs.python.org/2/library/configparser.html) file. Feel free to adapt the input method to your setting

#### 1. username, password, [security_token](https://success.salesforce.com/answers?id=90630000000glADAAY)
```
from salesforce_bulkipy import SalesforceBulkipy
import ConfigParser

config = ConfigParser.RawConfigParser()
config.read('config.properties')

username = config.get('Section', 'username')
password = config.get('Section', 'password')
security_token = config.get('Section', 'security_token')

bulk = SalesforceBulkipy(username=username, password=password, security_token=security_token) #optional parameter: sandbox=True

# Authentication Successful!
```

#### 2. session_id, host
```
from salesforce_bulkipy import SalesforceBulkipy
import ConfigParser

config = ConfigParser.RawConfigParser()
config.read('config.properties')

session_id = config.get('Section', 'session_id')
session_id = config.get('Section', 'session_id')

bulk = SalesforceBulkipy(session_id=session_id, host=host) #optional parameter: sandbox=True

# Authentication Successful!
```

## Operations

The basic sequence for driving the Bulk API is:

1. Create a new job
2. Add one or more batches to the job
3. Wait for each batch to finish
4. Close the job

## Bulk Insert, Update, Delete

All Bulk upload operations work the same. You set the operation when you create the
job. Then you submit one or more documents that specify records with columns to
insert/update/delete. When deleting you should only submit the Id for each record.

For efficiency you should use the `post_bulk_batch` method to post each batch of
data. (Note that a batch can have a maximum 10,000 records and be 1GB in size.)
You pass a generator or iterator into this function and it will stream data via
POST to Salesforce. For help sending CSV formatted data you can use the
salesforce_bulk.CsvDictsAdapter class. It takes an iterator returning dictionaries
and returns an iterator which produces CSV data.


**Concurrency mode**: When creating the job, you can pass `concurrency=Serial` or `concurrency=Parallel` to set the
concurrency mode for the job.


## Bulk Insert Example

```
from salesforce_bulkipy import SalesforceBulkipy
from salesforce_bulkipy import CsvDictsAdapter

bulk = SalesforceBulkipy(username=username, password=password, security_token=security_token)

records_to_insert = [{}, {}]  # A list of A Custom Object dict

# Bulk Insert
job = bulk.create_insert_job("CustomObjectName", contentType='CSV')
csv_iter = CsvDictsAdapter(iter(records_to_insert))
batch = bulk.post_bulk_batch(job, csv_iter)
bulk.wait_for_batch(job, batch)
bulk.close_job(job)
```


## Bulk Query Example

```
from salesforce_bulkipy import SalesforceBulkipy

bulk = SalesforceBulkipy(username=username, password=password, security_token=security_token)

records_to_insert = [{}, {}]  # A list of A Custom Object dict

# Bulk Query
query = '' # SOQL Query
job = bulk.create_query_job("PushCrew_Account__c", contentType='CSV')
batch = bulk.query(job, query)
bulk.wait_for_batch(job, batch)
bulk.close_job(job)
# Result
results = bulk.get_batch_result_iter(job, batch, parse_csv=True)
```

## Credits and Contributions

This repository is a maintained fork of [heroku/salesforce-bulk](https://github.com/heroku/salesforce-bulk). The changes incorporated here are a result of a joint effort by [@lambacck](https://github.com/lambacck), [@Jeremydavisvt](https://github.com/Jeremydavisvt), [@alexhughson](https://github.com/alexhughson) and [@bholagabbar](https://github.com/bholagabbar). Thanks to [@heroku](https://github.com/heroku) for creating the original useful library.

Feel free to contribute by creating Issues and Pull Requests. We'll test and merge them.