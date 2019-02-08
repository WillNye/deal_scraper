# Deal Scraper
### NOTE - You need a proxy or you will get IP Banned. I've had success with https://myiphide.com/

Pulls local inventory from the trending deals by category and/or Brand to get a single, easy to use page with price drop detection and discount thresholds


#### Getting Started
- You need python 3.5+
- Go to docker_eck and follow the steps to getting the backend and UI running to display the deal
- Run `pip install -r requirements.txt`
- Setup your host with `python cli.py setup --proxy YourProxyIPandPortGoesHere --zip_code YourZip`
- `python cli.py deals` to start scanning for deals


### Tips
* Retrieve a new proxy for each request, it seems like you get stale results after batch submission


### Todos

 - Ability to specify a brand and or category

 
License
----

It's a public repo, do whatever. 

