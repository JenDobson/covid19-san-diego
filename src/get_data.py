#! /Users/jen/projects/covid-san-diego/env/covidsd/bin/ python

#import sys, os
#THIS_PATH = os.path.abspath(os.path.dirname(__file__))
#sys.path.append(THIS_PATH)
#VIRTUAL_ENV = '/Users/jen/projects/covid-san-diego/env/covidsd/bin/'




import parser as p


print('hello world')
p.get_pdfs()
p.get_daily_status()
p.get_data_by_city()
p.get_data_by_zipcode()

