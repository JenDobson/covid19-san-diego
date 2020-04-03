#!/bin/bash
source //Users/jen/projects/covid-san-diego/covidsd/bin/activate
cd /Users/jen/projects/covid-san-diego
git pull

python -c 'import scrape_data; scrape_data.get_daily_status()'
python -c 'import scrape_data; scrape_data.get_city_breakdowns()'
python -c 'import scrape_data; scrape_data.get_zipcode_breakdowns()'

d=$(date +%Y-%m-%d)
echo "Update data for $d"

git commit -am "Update data for $d"
git push