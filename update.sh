#!/bin/bash
source //Users/jen/projects/covid-san-diego/covidsd/bin/activate
cd /Users/jen/projects/covid-san-diego
git pull

python -c 'import parser; parser.get_pdfs()'
python -c 'import parser; parser.get_daily_status()'
python -c 'import parser; parser.get_data_by_city()'
nozc=$(python -c 'import parser; parser.get_data_by_zipcode()')

d=$(date +%Y-%m-%d)
echo "Update data for $d"

#git commit csv/sandiego_data_by_zipcode.csv -m "update for $d; $nozc"
#git commit csv/sandiego_casesper100k_by_zipcode.csv -m "update for $d; $nozc"
#git commit csv/sandiego_data_by_city.csv -m "update for $d"
#git commit csv/sandiego_casesper100k_by_city.csv -m "update for $d"
#git commit csv/sandiego_daily_status.csv -m "update for $d"

#git push