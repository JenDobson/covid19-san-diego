from data_scraper.helpers import *
import os

DAILY_STATUS_URL = 'https://www.sandiegocounty.gov/content/sdc/hhsa/programs/phs/community_epidemiology/dc/2019-nCoV/status.html'
DAILY_STATUS_CSV_FILENAME = 'sandiego_daily_status.csv'

CSV_FILE_DIRECTORY = './csv'
PDF_FILE_DIRECTORY = './pdfs'

CITY_BREAKDOWN_CSV_FILENAME = 'sandiego_data_by_city.csv'
CITY_BREAKDOWN_PER100K_CSV_FILENAME = 'sandiego_casesper100K_by_city.csv'
CITY_BREAKDOWN_URL = 'https://www.sandiegocounty.gov/content/dam/sdc/hhsa/programs/phs/Epidemiology/COVID-19%20Daily%20Update_City%20of%20Residence.pdf'
CITY_BREAKDOWN_PDF_FILENAME = "city_breakdown_{timestamp}.pdf".format(timestamp=datetime.now().strftime("%y%m%dT%H%M"))
CITY_PDF_FILEPATH = os.path.join(PDF_FILE_DIRECTORY,CITY_BREAKDOWN_PDF_FILENAME)

ZIPCODE_BREAKDOWN_CSV_FILENAME = 'sandiego_data_by_zipcode.csv'
ZIPCODE_BREAKDOWN_PER100K_CSV_FILENAME = 'sandiego_casesper100K_by_zipcode.csv'
ZIPCODE_BREAKDOWN_URL = 'https://www.sandiegocounty.gov/content/dam/sdc/hhsa/programs/phs/Epidemiology/COVID-19%20Summary%20of%20Cases%20by%20Zip%20Code.pdf'
ZIPCODE_BREAKDOWN_PDF_FILENAME = "zipcode_breakdown_{timestamp}.pdf".format(timestamp=datetime.now().strftime("%y%m%dT%H%M"))
ZIPCODE_PDF_FILEPATH = os.path.join(PDF_FILE_DIRECTORY,ZIPCODE_BREAKDOWN_PDF_FILENAME)


def get_pdfs():
    # Retrieve and write the city breakdown pdf
    
    save_pdf_from_url(CITY_BREAKDOWN_URL,CITY_PDF_FILEPATH)
    save_pdf_from_url(ZIPCODE_BREAKDOWN_URL,ZIPCODE_PDF_FILEPATH)
    
def get_daily_status():
    parse_daily_status(DAILY_STATUS_URL,os.path.join(CSV_FILE_DIRECTORY,DAILY_STATUS_CSV_FILENAME))
    
def get_data_by_city():
    pdffilepath = glob.glob(os.path.join(PDF_FILE_DIRECTORY,'city_breakdown_{date}T*.pdf'.format(date=datetime.now().strftime("%y%m%d"))))[0]
    parse_city_data(pdffilepath,
        os.path.join(CSV_FILE_DIRECTORY,CITY_BREAKDOWN_CSV_FILENAME),
        os.path.join(CSV_FILE_DIRECTORY,CITY_BREAKDOWN_PER100K_CSV_FILENAME))
        
def get_data_by_zipcode():
    pdffilepath = glob.glob(os.path.join(PDF_FILE_DIRECTORY,'zipcode_breakdown_{date}T*.pdf'.format(date=datetime.now().strftime("%y%m%d"))))[0]
    parse_zipcode_data(pdffilepath,
        os.path.join(CSV_FILE_DIRECTORY, ZIPCODE_BREAKDOWN_CSV_FILENAME),
        os.path.join(CSV_FILE_DIRECTORY,ZIPCODE_BREAKDOWN_PER100K_CSV_FILENAME))
        
