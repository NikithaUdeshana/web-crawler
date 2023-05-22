# Web Crawler

Web crawler is a python based microservice which is used to fetch all links within a given domain. This solution is also capable of fetching associated links per each given page link. It accepts one page URL as an input parameter and crawl through all links that are reachable either directly or indirectly from the original page URL. Furthermore, this solution omits the links that are outside of the domain associated with the original URL.

## Setup

First, use pip to install the dependencies.

```bash
pip install -r requirements.txt
```

Run the Web crawler by executing the following command from the root direcotry.

```bash
python3 app/main.py
```

## Details

Use `/crawl` endpoint with the following parameters:

* url
* depth
* no_of_pages

It will return a JSON dictionary with all page links within a given domain and with all the associated links per each given page link. Depth parameter defines how deep that you want to crawl using the Web Crawler in the page hierarchy of the website. No_of_pages parameter defines the maximum pages that needs to be crawled using the web crawler.
A sample curl command is given below.

    curl "http://127.0.0.1:5000/crawl?url=https://bbc.co.uk&depth=3&no_of_pages=50"
