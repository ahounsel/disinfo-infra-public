# Identifying Disinformation Websites Using Infrastructure Features

Source code and training data for the academic paper available [here.](https://www.usenix.org/conference/foci20/presentation/hounsel)

## Structure

* bin - Contains all entry points for the system

* system - All source code for system, including fetching and classifying data

* analysis - All code to analyze classification performance 


## Installation

### Steps to Develop on disinfo-infra

1. Create Python virtual environment (optional) to avoid conflicts with local
   packages : `python3 -m venv name-of-environment`
2. Activate the virtual environment to install packages in isolated environment:
   `source name-of-environment/bin/activate`
3. Install required dependencies for disinfo-infra via pip: `pip install -r
   requirements.txt`
4. Setup development environment install via setup.py: `python setup.py
  develop` This allows changes to be tracked while developing without
  re-installation on each change
5. Develop!
6. If you want to deactivate the virtual environment: `deactivate`

### Steps to install and run code (**NOT FOR DEVELOPMENT**)

1. Download source
2. pip install -r requirements.txt
3. python setup.py install

## Entry Points

```disinfo_net_data_fetch.py``` - continually fetches new domains and raw data for those domains, implemented domain pipes include reddit, twitter, certstream, and domaintools.

```disinfo_net_train_classifier.py``` - script that trains the classifier from
designated training data.

```disinfo_net_classify.py``` - script to classify raw data fetched by ```disinfo_data_fetch.py```. It extracts features, classifies websites, and inserts them into a database table named by the user. It can be run in "live" mode where it constantly classifies new domains as they are fetched from ```disinfo_data_fetch.py``` or it can classify an entire database of candidate domains at once.

## System Structure

1. Orchestrate - contains a conductor class that handles thread creation for
   domain pipes and worker threads, a worker thread class that fetches raw
   data for a domain, and a classification thread class that extracts features from raw data and classifies them.

2. Classify - Classifier class that has classes and functions for training,
   extracting features, and classifying candidate domains

3. Features - Classes to both fetch raw data and extract features from that raw data.

6. Pipe - contains an abstract base class for domain pipes that creates a
   standard interface for what the system expects when a domain is processed:
   current implementations of this ABC include Reddit, Twitter, Certstream, and DomainTools domain pipes

7. Postgres - Classes to interact with a postgres database including inserting,
   checking, and retrieving data.
   
8. util - various utility classes including classes to unshorten urls, get tlds, and determining ownership of ip addresses

## Database Entries

Our system works in two parts, a data fetching script, which inserts *raw data* into a database table structured as follows:

```javascript
 Attribute (Type) {
 domain (Text) (Primary Key),
 certificate (Text)
 whois (Text),
 html (Text),
 dns (Text),
 post_id (Text)
 platform (Text)
 insertion_time (UTC) 
}
```

Where each attribute is:

* domain - unique domain which the rest of the data is associated with
* certificate - the certificate, in raw string format, of the domain
* whois - the whois response in raw string format
* html - the raw HTML source of the homepage of the domain
* dns - the IP address(es) that the domain was found to map to
* post_id - the unique post id on the given platform of the post (for
verification purposes)
* platform - the platform on which the domain was posted
* insertion_time - time of insertion into the database


The second part of our system, which classifies a domain given raw data about the domain, inserts those classifcations into a database table structured as follows:

```javascript
 Attribute (Type) {
 domain (Text) (Primary Key),
 classification (Text) (one of: unclassified, non_news, disinformation)
 probabilities (JSON),
 insertion_time (UTC) 
}
```

Where each attribute is:

* domain - unique domain which the rest of the data is associated with
* classification - the actual classification of the domain by the classifier, one of: news, non_news, disinformation
* probabilities - the probabilities of each class mentioned above in a JSON dictionary format
* insertion_time - time of insertion to the database


Finally, we have a prepopulated training database, including raw data of all of our training data, in the format of:

```javascript
 Attribute (Type) {
 domain (Text) (Primary Key),
 target (Text) one of: unclassified, non_news, disinformation)
 certificate (Text)
 whois (Text),
 html (Text),
 dns (Text),
}
```

Where each attribute is the same as our raw data table, with *target* being the known label for the domain.

## Using the Chrome extension
Navigate your Chrome browser to chrome://extensions and enable developer mode in the top right. 

Click "Load Unpacked" and upload the contents of the src/plugin/ directory. 

![Chrome developer tutorial](https://developer.chrome.com/static/images/get_started/load_extension.png)

Navigate to any of the sites listed in src/plugins/classified_sites.txt (for example, [needtoknow.news](https://www.needtoknow.news)) and you will see the warning message.
