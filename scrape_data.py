from datetime import datetime
import os
import pandas as pd
import re
import glob

# For PDF retrieval and parsing (required for city and zipcode data)
import PyPDF2
import requests


DAILY_STATUS_URL = 'https://www.sandiegocounty.gov/content/sdc/hhsa/programs/phs/community_epidemiology/dc/2019-nCoV/status.html'
DAILY_STATUS_CSV_FILENAME = 'sandiego_daily_status.csv'

CSV_FILE_DIRECTORY = './csv'
PDF_FILE_DIRECTORY = './pdfs'

CITY_BREAKDOWN_CSV_FILENAME = 'sandiego_data_by_city.csv'
CITY_BREAKDOWN_URL = 'https://www.sandiegocounty.gov/content/dam/sdc/hhsa/programs/phs/Epidemiology/COVID-19%20Daily%20Update_City%20of%20Residence.pdf'
CITY_BREAKDOWN_PDF_FILENAME = "city_breakdown_{timestamp}.pdf".format(timestamp=datetime.now().strftime("%y%m%dT%H%M"))


ZIPCODE_BREAKDOWN_CSV_FILENAME = 'sandiego_data_by_zipcode.csv'
ZIPCODE_BREAKDOWN_URL = 'https://www.sandiegocounty.gov/content/dam/sdc/hhsa/programs/phs/Epidemiology/COVID-19%20Summary%20of%20Cases%20by%20Zip%20Code.pdf'
ZIPCODE_BREAKDOWN_PDF_FILENAME = "zipcode_breakdown_{timestamp}.pdf".format(timestamp=datetime.now().strftime("%y%m%dT%H%M"))


def date_retrieved():
    return pd.Timestamp.now().round('s')
    

def extract_text_from_pdf_url(pdfurl,pdffilepath):
    r = requests.get(pdfurl)
    with open(pdffilepath,'wb') as f: 
        f.write(r.content) 

    file = open(pdffilepath,'rb')
    fileReader = PyPDF2.PdfFileReader(file)
    pg0 = fileReader.getPage(0)
    txt = pg0.extractText()
    file.close()
    return txt
    
def write_to_csv(df,filepath):
    files_present = glob.glob(filepath)
    if files_present:
        df.to_csv(filepath,mode='a',header=False)
    else:
        df.to_csv(filepath)   
        
def get_daily_status():
    # Grab and parse the data
    county_data = pd.read_html(DAILY_STATUS_URL)[0]
    date_updated = re.findall('(?P<date>[A-Z][a-z]+\s+\d{1,2},\s+\d{4}).',county_data.iloc[0,0])[-1]
    date_updated = pd.Timestamp(datetime.strptime(date_updated,'%B %d, %Y'))

    # Set up dataframe headers
    age_headers = ['0-9 years','10-19 years','20-29 years','30-39 years','40-49 years','50-59 years','60-69 years','70-79 years','80+ years','Age Unknown']
    gender_headers = ['Female','Male','Unknown']
    hospitalization_headers = ['Hospitalizations','Intensive Care','Deaths']

    # Get dataframes for each header category
    age_df = county_data[county_data.iloc[:,0].isin(age_headers)]
    age_df = age_df.rename(index=age_df.iloc[:,0])
    age_df = age_df.drop(columns=0).transpose()

    gender_df = county_data[county_data.iloc[:,0].isin(gender_headers)]
    gender_df = gender_df.rename(index=gender_df.iloc[:,0])
    gender_df= gender_df.drop(columns=0).transpose()

    hospitalization_df = county_data[county_data.iloc[:,0].isin(hospitalization_headers)]
    hospitalization_df = hospitalization_df.rename(index=hospitalization_df.iloc[:,0])
    hospitalization_df=hospitalization_df.drop(columns=0).transpose()

    total_df = county_data[county_data.iloc[:,0]=='Total Positives']
    total_df = total_df.rename(index=total_df.iloc[:,0])
    total_df=total_df.drop(columns=0).transpose()

    # Concatenate the dataframes
    pieces = {'Age':age_df,'Gender':gender_df,'Hospitalization':hospitalization_df,'Total':total_df}
    df_final = pd.concat(pieces,axis=1)
    df_final = df_final.rename(index={1:date_updated}); df_final.index.name='Cases as of date'
    df_final['Date Retrieved']=date_retrieved()

    # Write to CSV
    countydatafilepath = os.path.join(CSV_FILE_DIRECTORY,DAILY_STATUS_CSV_FILENAME)
    write_to_csv(df_final,countydatafilepath)

    
def get_city_breakdowns():

    # Retrieve and write the city breakdown pdf
    pdffilepath = os.path.join(PDF_FILE_DIRECTORY,CITY_BREAKDOWN_PDF_FILENAME)
    
    txt = extract_text_from_pdf_url(CITY_BREAKDOWN_URL,pdffilepath)
    txt = re.sub('\n','',txt)

    # Parse the city data
    date = re.findall('Data through (?P<date>\d{1,2}/\d{1,2}/\d{4})',txt)[0]
    data = re.findall('\s+(?P<city>[A-Za-z ]+[a-z])\*?\s+(?P<count>[,\d]+) (?P<percentage>[0-9.]+%)',txt)

    # Create dataframes
    df = pd.DataFrame.from_records(data).transpose()
    df.columns = df.iloc[0]; df=df.iloc[1:]; df.columns.name = ''
    df.index=[pd.Timestamp(date).date(),'Percent of Total']; df.index.name=''
    df = df.rename(columns={'of Overall Total Incorporated City':'Incorporated', 'Total San Diego County Residents':'Total'})
    df = df.drop(['Percent of Total'])

    incorporated_columns = ['Carlsbad','Chula Vista','Coronado','Del Mar','El Cajon','Encinitas','Escondido','Imperial Beach','La Mesa','Lemon Grove','National City','Oceanside','Poway','San Diego','San Marcos','Santee','Solana Beach','Vista','Incorporated']
    df_incorporated = df.reindex(columns=incorporated_columns)
    df_incorporated = df_incorporated.rename(columns={'Incorporated':'Total'})

    unincorporated_columns = ['Bonita','Fallbrook','Lakeside','Ramona','Rancho Santa Fe','Spring Valley','Other','Unincorporated']
    df_unincorporated = df.reindex(columns=unincorporated_columns)
    df_unincorporated = df_unincorporated.rename(columns={'Unincorporated':'Total'})

    df_unknown = df.loc[:,['Unknown']]
    df_total = df.loc[:,['Total']]
    df_total=df_total.rename(columns={'Total':'San Diego County'})

    # Concatenate the dataframes
    pieces = {'Incorporated':df_incorporated,'Unincorporated':df_unincorporated,'Unknown':df_unknown,'Total':df_total}
    df_final = pd.concat(pieces,axis=1)
    df_final.columns.names = ['Administration','City']
    df_final = df_final.reorder_levels(['City','Administration'],axis=1)
    df_final.index.name = 'Data through date'
    df_final['Date Retrieved']=date_retrieved()

    # Write to csv
    citydatafilepath = os.path.join(CSV_FILE_DIRECTORY,CITY_BREAKDOWN_CSV_FILENAME)
    write_to_csv(df_final,citydatafilepath)
    
    
    
def get_zipcode_breakdowns():
        
    pdffilepath = os.path.join(PDF_FILE_DIRECTORY,ZIPCODE_BREAKDOWN_PDF_FILENAME)
    txt = extract_text_from_pdf_url(ZIPCODE_BREAKDOWN_URL,pdffilepath)

    date = re.findall('Data through (?P<date>\d{1,2}/\d{1,2}/\d{4})',txt)[0]
    data = re.findall('(\d{5}|Unknown\*|TOTAL)\n(?P<count>[,\d]+)',txt)


    df = pd.DataFrame.from_records(data).transpose()
    df.columns = df.iloc[0]; df=df.iloc[1:]; df.columns.name = ''
    df['Date Retrieved']=date_retrieved()
    df.index=[pd.Timestamp(date).date()]; df.index.name='Data through'

    zipcodedatafilepath = os.path.join(CSV_FILE_DIRECTORY,ZIPCODE_BREAKDOWN_CSV_FILENAME)

    dfold = pd.read_csv(zipcodedatafilepath)
    dfold.index = dfold['Data through']
    dfold = dfold.drop(['Data through'],axis=1)

    catdf = pd.concat([dfold,df])
    catdf = catdf[catdf.columns.sort_values()]
    catdf = pd.concat([catdf[catdf.columns[0:-3]],catdf['Unknown*'],catdf['TOTAL'],catdf['Date Retrieved']],axis=1)

    catdf.to_csv(zipcodedatafilepath)
    # write_to_csv(df,zipcodedatafilepath)



# WORKING WITH CITY DATA IN PANDAS:
# Get one city's data for example with: df_final.iloc[:, df_final.columns.get_level_values(1)=='Carlsbad']
# Get all incorporated cities:  df_final.iloc[:,df_final.columns.get_level_values(0)=='Incorporated']
