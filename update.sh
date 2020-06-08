#!/bin/bash
source /Users/jen/projects/covid-san-diego/env/covidsd/bin/activate
cd /Users/jen/projects/covid-san-diego
git pull

nozc=$(python get_data.py)

d=$(date +%Y-%m-%d)
t=$(date +%Y%m%dT%H:%M:%S)
echo "Update data for $t" >> scripts/log.txt

#git commit csv/sandiego_data_by_zipcode.csv -m "update for $d; $nozc"
#git commit csv/sandiego_casesper100k_by_zipcode.csv -m "update for $d; $nozc"
#git commit csv/sandiego_data_by_city.csv -m "update for $d"
#git commit csv/sandiego_casesper100k_by_city.csv -m "update for $d"
#git commit csv/sandiego_daily_status.csv -m "update for $d"

#git push