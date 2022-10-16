# UPA project - Train timetables
## Requirements:
- Python 3.10 or higher
- pymongo (`python -m pip install pymongo`)
- pandas (`pip install pandas`)
- tqdm (`pip install tqdm`)
- tkinter (`pip install tk`)
- docker or podman (optional - if you wish to start your own DB in container)

### Start Apache Cassandra DB locally
```shell
docker run --name mongodb -d -p 27017:27017 mongo
```
Please note that start up takes a few seconds. Additionally, if you wish to enter `cqlsh` console and databases keyspace run: