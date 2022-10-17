# UPA project - Train timetables
## Requirements:
- Python 3.10 or higher
- pymongo (`python -m pip install pymongo`)
- tqdm (`pip install tqdm`)
- xmltodict ( pip install xmltodict )
- docker or podman (optional - if you wish to start your own DB in container)

### Pre-requistes
Make sure you have all the requirements installed and used dataset downloaded, if not you can do so by executing 
```
download_data.sh
install_req.sh
```

### Start MongoDB locally
```shell
docker run --name mongodb -d -p 27017:27017 mongo
```
Please note that start up takes a few seconds. Additionally, if you wish to enter `mongosh` console and databases keyspace run:
```
docker exec -it mongodb bash
mongosh
use timetables
```