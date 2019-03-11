# Dockerized ES and Kibana
Runs a local ES and Kibana instance with Docker. 
This is the where records are kept and how they are visualized.

### Getting started
First, you'll need docker and docker compose to use this.
* https://docs.docker.com/install/#server
* https://docs.docker.com/compose/install/


Once Docker is up run these command to start ES and Kibana
```bash

# This is where the records are stored locally
docker volume create esData
docker volume create cerebroConf

# Runs everything on host machine
./run_as_${HOST_OS}.sh  # host os must be mac or ubuntu

```

After a few minutes you should be able to open this page:

##### For Ubuntu
http://127.0.0.1:9000/#/overview?host=http:%2F%2Flocalhost:9200

##### For Mac
http://127.0.0.1:9000/#/overview?host=http:%2F%2Felasticsearch:9200


1. In the top, left hand corner of the page click "More" and select "Index Templates"
2. On the right side of the page there will be and area to create template.
3. Fill in "Product" for the name
4. Copy the content in index_template.json into the area below name, replacing the initial content
5. Click create in the bottom, right hand corner of the page
> This allows the deals to be stored


Once deals have been created go to http://127.0.0.1:5601
1. Click on the Management cog on the right side of the screen
2. Select "Saved Objects"
3. Click the Import button, click Import on the pop up
4. Select the export.json file


