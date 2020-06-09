#!/bin/bash
cd /Users/jen/projects/covid-san-diego
git pull

#python -c 'import data_scraper.parser as p; p.get_pdfs()'
#python -c 'import data_scraper.parser as p; p.get_daily_status()'
#python -c 'import data_scraper.parser as p; p.get_data_by_city()'
#nozc=$(python -c 'import data_scraper.parser as p; p.get_data_by_zipcode()')
/Users/jen/projects/covid-san-diego/env/covidsd/bin/python /Users/jen/projects/covid-san-diego/get_data.py



d=$(date +%Y-%m-%d)
echo "Update data for $d"

t=$(date +%Y%m%dT%H:%M:%S)
echo "Update data for $t" >> scripts/log.txt

#git commit csv/sandiego_data_by_zipcode.csv -m "update for $d; $nozc"
#git commit csv/sandiego_casesper100k_by_zipcode.csv -m "update for $d; $nozc"
#git commit csv/sandiego_data_by_city.csv -m "update for $d"
#git commit csv/sandiego_casesper100k_by_city.csv -m "update for $d"
#git commit csv/sandiego_daily_status.csv -m "update for $d"

#git push