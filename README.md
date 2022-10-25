# UPA project - Train timetables
## Requirements:
- Python 3.10 or higher
- pymongo (`python -m pip install pymongo`)
- tqdm (`pip install tqdm`)
- xmltodict (`pip install xmltodict`)
- bs4 (`pip install bs4`)
- requests (`pip install requests`)
- argparse_prompt (`pip install argparse_prompt`)
- docker or podman (optional - note that project uses mongoDB located in docker container)

### Pre-requistes
Make sure you have all the requirements installed and used dataset downloaded, if not you can do so by executing 
```shell
install_modules.sh
```
if the script doesn't work run `chmod +x install_modules.sh` and try again.

### Start MongoDB locally
```shell
docker run --name mongodb -d -p 27017:27017 mongo
```
Please note that start up takes a few seconds. Additionally, if you wish to enter `mongosh` console and databases keyspace run:
```shell
docker exec -it mongodb bash
mongosh
use timetables
```

### Using the cli app
The main goal of the project was creating an app capable of displaying all stations en route from station A to station B on a specified date and time. To run and use this app run
```shell
python cli.py
```
upon startup the user with be prompted with a question of downloading the data and creating a database, this is set to `No` by default however if the app is started for the first time and no database is created then input `yes` or `True`. Please note that due to the sheer volume of the data files, the whole download process as well as the upload of the data to the database will take a while usually around 30-45 minutes. 

After the download has finished or if the user denied the option to download ie. already has the database running and full, the user will be prompted to enter `Source station`, `Destination station` and the date range to be searched with `Time from` and `Time until`. The result of the user's query will be displayed after a brief period.