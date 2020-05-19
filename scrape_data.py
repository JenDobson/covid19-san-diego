from datetime import datetime
import os
import pandas as pd
import re
import glob

# For PDF retrieval and parsing (required for city and zipcode data)
import PyPDF2
import requests

import pathlib


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

def get_pdfs():
    # Retrieve and write the city breakdown pdf
    citypdffilepath = os.path.join(PDF_FILE_DIRECTORY,CITY_BREAKDOWN_PDF_FILENAME)
    save_pdf_from_url(CITY_BREAKDOWN_URL,citypdffilepath)
    
    zippdffilepath = os.path.join(PDF_FILE_DIRECTORY,ZIPCODE_BREAKDOWN_PDF_FILENAME)
    save_pdf_from_url(ZIPCODE_BREAKDOWN_URL,zippdffilepath)
    

def date_retrieved():
    return pd.Timestamp.now().round('s')
    

def save_pdf_from_url(pdfurl,pdffilepath):
    r = requests.get(pdfurl)
    with open(pdffilepath,'wb') as f: 
        f.write(r.content) 

    

def extract_text_from_pdf(filepath):
    file = open(filepath,'rb')
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
    
    save_pdf_from_url(CITY_BREAKDOWN_URL,pdffilepath)
    
    casesfilepath = os.path.join(CSV_FILE_DIRECTORY,CITY_BREAKDOWN_CSV_FILENAME)
    ratesfilepath = casesfilepath.replace('data','casesper100k')
    parse_city_data(pdffilepath,casesfilepath,ratesfilepath)
    
        #
    # txt = extract_text_from_pdf(pdffilepath)
    # txt = re.sub('\n','',txt)
    #
    # # Parse the city data
    # date = re.findall('Data through (?P<date>\d{1,2}/\d{1,2}/\d{4})',txt)[0]
    #
    # #Format change on 4/21
    # if pd.Timestamp(date)>=pd.Timestamp('4/21/2020'):
    #     data = re.findall('(?P<city>[A-Za-z ]+[a-z])\*{0,4}\s+(?P<count>[,\d]+)\s+(?P<percentage>[0-9.]+%)?\s+(\d+.\d+|\*{3})?',txt)
    # else:
    #     data = re.findall('\s+(?P<city>[A-Za-z ]+[a-z])\*{0,4}\s+(?P<count>[,\d]+) (?P<percentage>[0-9.]+%)',txt)
    #
    # # Remove improper use of %
    # df = data_to_df([(x[0],x[1]) for x in data],date)
    # rates_df = data_to_df([(x[0],x[3]) for x in data],date)
    #
    # df_total = format_cities_df(df)
    # rates_total = format_cities_df(rates_df)
    #
    # # Create dataframes
    # #df = pd.DataFrame.from_records(data).transpose()
    #
    #
    #
    #
    # # Write to csv
    # citydatafilepath = os.path.join(CSV_FILE_DIRECTORY,CITY_BREAKDOWN_CSV_FILENAME)
    # write_to_csv(df_total,citydatafilepath)
    #
    # ratesdatafilepath = citydatafilepath.replace('data','casesper100k')
    # write_to_csv(rates_total,ratesdatafilepath)
    
def format_cities_df(df):
    df.columns = df.columns.str.lstrip()
    df.columns = df.columns.str.rstrip()
    df = df.rename(columns={'Incorporated City':'Incorporated', 'Total San Diego County Residents':'Total'})

    incorporated_columns = ['Carlsbad','Chula Vista','Coronado','Del Mar','El Cajon','Encinitas','Escondido','Imperial Beach','La Mesa','Lemon Grove','National City','Oceanside','Poway','San Diego','San Marcos','Santee','Solana Beach','Vista','Incorporated']
    df_incorporated = df.reindex(columns=incorporated_columns)
    df_incorporated = df_incorporated.rename(columns={'Incorporated':'Total'})

    unincorporated_columns = ['Alpine','Bonita','Bonsall','Borrego Springs','Boulevard','Campo',
                            'Descanso','Dulzura','Fallbrook','Jamul','Julian','Lakeside','Pala','Pauma Valley','Potrero','Ramona',
                            'Ranchita','Rancho Santa Fe','Santa Ysabel','Spring Valley','Tecate','Valley Center','Other','Unincorporated']
    df_unincorporated = df.reindex(columns=unincorporated_columns)
    df_unincorporated = df_unincorporated.rename(columns={'Unincorporated':'Total'})

    try:
        df_unknown = df.loc[:,['Unknown']]
    except:
        df_unknown = pd.DataFrame()
        
        
    df_total = df.filter(regex=("Total*"))
    df_total=df_total.rename(columns={'Total':'San Diego County'})

    # Concatenate the dataframes
    pieces = {'Incorporated':df_incorporated,'Unincorporated':df_unincorporated,'Unknown':df_unknown,'Total':df_total}
    
    df_final = pd.concat(pieces,axis=1)
    df_final.columns.names = ['Administration','City']
    df_final = df_final.reorder_levels(['City','Administration'],axis=1)
    df_final.index.name = 'Data through date'
    df_final['Date Retrieved']=df['Date Retrieved']
    return df_final
    
def df_from_text(txt):
    date = re.findall('Data through (?P<date>\d{1,2}/\d{1,2}/\d{4})',txt)[0]
    
        
    #zipregex = '(919[0-9]{2}|920[0-9]{2}|921[0-9]{2})'
    #zipcodes = re.findall(zipregex,txt)
    #zipcodes.extend(['Unknown*\n','TOTAL\n','Unknown','Total','Total\n'])
    
    #if text has a long string of numbers (i.e. no formatting), use one extraction method
    if re.search('\d{20}',txt):
        cases = data_from_unstructured_text(txt)
        rates = None
    #if text has formatting, use formatting to extract data
    else:
        (cases,rates) = data_from_zip_text_with_rates(txt)
        
    df = data_to_df(cases,date)
    rates_df = data_to_df(rates,date)
    return (df,rates_df)

'''data is list of (zipcode,number) CASES or RATES'''
def data_to_df(data,date):
    
    df = pd.DataFrame(data).transpose()
    
    df.columns = df.iloc[0]; df=df.iloc[1:]; df.columns.name = ''

    df = df.rename({'Unknown****':'Unknown','Unknown***':'Unknown','Unknown*\n':'Unknown','Unknown*':'Unknown','Unknown\n':'Unknown','TOTAL\n':'TOTAL','Total':'TOTAL','Total\n':'TOTAL'},axis=1) # REMOVE AFTER PDF FORMAT FIXED
    
    df['Date Retrieved']=date_retrieved()
    df.index=[pd.Timestamp(date).date()]; df.index.name='Data through'
    return df

def data_from_unstructured_text(txt):
    zipcodes = [x[0] for x in re.findall('(?P<zip>(919|920|921)[0-9]{2})',txt)]
    headers = zipcodes.extend(['Unknown*\n','TOTAL\n','Unknown','Unknown*','Unknown\n','Total','Total\n'])
    for k in range(0,len(headers)):
        txt = txt.replace(headers[k],'ZIP{n:03}ZIP'.format(n=k))
    maskregex = 'ZIP(?P<idx>[0-9]{3})ZIP\n?(?P<cases>[0-9]+)'
    res = re.findall(maskregex,txt)
    data=[]
    for (idx,ncases) in res:
        data.append([zipcodes[int(idx)],int(ncases)])
    return data
    
def data_from_zip_text_with_rates(txt):
    txt = txt.replace(',','')
    pattern = '(Unknown.{0,4}|Total|[0-9]{5})\n(?P<count>[0-9]*,{0,1}[0-9]*)\n{0,1}([0-9]+\.?[0-9]+|\*{1,3})'
    data = re.findall(pattern,txt,re.IGNORECASE)
    cases = [(x[0],x[1]) for x in data]
    rates = [(x[0],x[2]) for x in data]      
    return cases,rates


def concat_dfs(df,filepath):
    
    
    
    try:
        dfold = pd.read_csv(filepath)
        dfold.index = dfold['Data through']
        dfold = dfold.drop(['Data through'],axis=1)
    
        catdf = pd.concat([dfold,df],join='outer')
        
        zipcodes_not_in_csv = df.columns[~df.columns.isin(dfold.columns)]
        unreported_zipcodes = dfold.columns[~dfold.columns.isin(df.columns)]
        
        print('Zipcodes with no reporting:  {s}; Reported zipcodes not recorded: {s2}'.format(s=', '.join(unreported_zipcodes),s2=', '.join(zipcodes_not_in_csv)))
    except:
        catdf = df
            
    
    
    
    columns = sorted(catdf.columns)
    columns = columns[0:-3]+['Unknown','TOTAL','Date Retrieved']
    catdf = catdf.reindex(columns,axis=1)
    catdf = catdf.loc[:,~catdf.columns.duplicated()]
    
    return catdf
        
def get_zipcode_breakdowns():
    
    zipcodedatafilepath = os.path.join(CSV_FILE_DIRECTORY,ZIPCODE_BREAKDOWN_CSV_FILENAME)
    zipcodes = get_zipcodes_from_csv(zipcodedatafilepath)
        
    pdffilepath = os.path.join(PDF_FILE_DIRECTORY,ZIPCODE_BREAKDOWN_PDF_FILENAME)
    save_pdf_from_url(ZIPCODE_BREAKDOWN_URL,pdffilepath)
    txt = extract_text_from_pdf(pdffilepath)
    
    (cases_df,rates_df) = df_from_text(txt)
    
    cases_df = concat_dfs(cases_df,zipcodedatafilepath)
    
    
    ratesdatafilepath = zipcodedatafilepath.replace('data','casesper100k')
    rates_df = concat_dfs(rates_df,ratesdatafilepath)
    

    
    cases_df.to_csv(zipcodedatafilepath)
    rates_df.to_csv(ratesdatafilepath)
    
    
    # write_to_csv(df,zipcodedatafilepath)

def get_zipcodes_from_csv(csvfile):
    df = pd.read_csv(csvfile)
    return df.filter(regex="\d{5}").columns.values

# WORKING WITH CITY DATA IN PANDAS:
# Get one city's data for example with: df_final.iloc[:, df_final.columns.get_level_values(1)=='Carlsbad']
# Get all incorporated cities:  df_final.iloc[:,df_final.columns.get_level_values(0)=='Incorporated']



    
def cases_and_rates_from_txt(txt):
    txt = re.sub(',','',txt)
    txt = re.sub('Unknown\*+','Unknown',txt)
    txt = re.sub('Unknown\n','Unknown\n',txt)
    txt = re.sub('Total\n','TOTAL',txt)
    prior_cases = pd.read_csv('csv/sandiego_data_by_zipcode.csv')
    prior_rates = pd.read_csv('csv/sandiego_casesper100k_by_zipcode.csv')
    prior_cases = prior_cases.iloc[-2]
    prior_rates = prior_rates.iloc[-2]
    prior_cases = prior_cases.drop(['Data through','Date Retrieved'],axis=0)
    strlength = prior_cases.apply(lambda x: len(str(int(x))))
    zipcodes = prior_cases.index.values

    data = []
    for k in range(0,len(zipcodes)):
    	zip=zipcodes[k]
    	casespattern='[0-9]'*strlength[k]
    	tokens = re.search(rf"(?P<zip>{zip})\n?(?P<cases>{casespattern})\n?(?P<rate>[0-9]+\.[0-9]|\*\*)",txt,re.IGNORECASE)
    	data.append(tokens.groupdict())

    return data
    
    
    

def date_retrieved(pdffilepath):
    fname = pathlib.Path(pdffilepath)
    return pd.Timestamp(datetime.fromtimestamp(fname.stat().st_mtime)).ceil('s')

def parse_city_data(pdffilepath,casesfilepath,ratesfilepath):
    """Create and write DataFrame for city data
    
    PDFFILEPATH:  Path to pdf file of case data
    CASESFILEPATH: Path to csv file of case data
    RATESFILEPATH: Path to csv file of case per 100k data
    
    pdffilepath = 'pdfs/city_breakdown_200517T0601.pdf'
    casesfilepath = 'csv/sandiego_data_by_city.csv'
    ratesfilepath = 'csv/sandiego_casesper100k_by_city.csv' 
    
    import parser as p
    p.parse_city_data(pdffilepath,casesfilepath,ratesfilepath)
    """
    
    txt = extract_text_from_pdf(pdffilepath)
    
    # Parse the city data
    date = re.findall('Data through (?P<date>\d{1,2}/\d{1,2}/\d{4})',txt)[0]
    
    #Format change on 4/21
    if pd.Timestamp(date)>=pd.Timestamp('4/21/2020'):
        data = re.findall('(?P<city>[A-Za-z ]+[a-z])\*{0,4}\s+(?P<count>[,\d]+)\s+(?P<percentage>[0-9.]+%)?\s+?(\d+.\d+|\*{3}|)?',txt)
    else:
        data = re.findall('\s+(?P<city>[A-Za-z ]+[a-z])\*{0,4}\s+(?P<count>[,\d]+) (?P<percentage>[0-9.]+%)',txt)
    
    unknown_tuple = re.search('(Unknown)\*{0,4}\s?(\d+)()()',txt,re.IGNORECASE).groups()
    
    df = pd.DataFrame(data).transpose()
    df['Unknown'] = pd.Series(unknown_tuple)
    
    df = df.drop(index=[2])
    df.columns = df.iloc[0]
    df = df.drop(index=0)

    df['Date Retrieved'] = [date_retrieved(pdffilepath),date_retrieved(pdffilepath)]
    df.index.name='Data through' 
    
    cases_df = df.drop(index=3)
    cases_df.index.name = 'Data through'
    cases_df.index=[pd.Timestamp(date).date()]
    
    rates_df = df.drop(index=1)
    rates_df.index.name = 'Data through'
    rates_df.index=[pd.Timestamp(date).date()]
    
    
    cases_df_total = format_cities_df(cases_df)
    rates_df_total = format_cities_df(rates_df)
    
    # Write to csv
    write_to_csv(cases_df_total,casesfilepath)
    write_to_csv(rates_df_total,ratesfilepath)

def parse_zipcode_data(pdffilepath,casesfilepath,ratesfilepath):
    """Create and write DataFrame for zip code data
    
    PDFFILEPATH:  Path to pdf file of case data
    CASESFILEPATH: Path to csv file of case data
    RATESFILEPATH: Path to csv file of case per 100k data
    
    pdffilepath = 'pdfs/zipcode_breakdown_200517T0601.pdf'
    casesfilepath = 'csv/sandiego_data_by_zipcode.csv'
    ratesfilepath = 'csv/sandiego_casesper100k_by_zipcode.csv' 
    
    import parser as p
    p.parse_zipcode_data(pdffilepath,casesfilepath,ratesfilepath)
    """
    

    txt = extract_text_from_pdf(pdffilepath)
    
    txt = re.sub(',','',txt)
    txt = re.sub('Unknown\*+','Unknown',txt)
    txt = re.sub('Unknown\n','Unknown\n',txt)
    txt = re.sub('Total\n','TOTAL',txt)
    prior_cases = pd.read_csv(casesfilepath)
    prior_rates = pd.read_csv(ratesfilepath)
    prior_cases = prior_cases.iloc[-3]
    prior_rates = prior_rates.iloc[-3]
    prior_cases = prior_cases.drop(['Data through','Date Retrieved'],axis=0)
    prior_cases = prior_cases.fillna(0)
    strlength = prior_cases.apply(lambda x: len(str(int(x))))
    zipcodes = prior_cases.index.values

    zipcodes_in_text = re.findall('(919\d{2}|920\d{2}|921\d{2})',txt)

    if len(zipcodes)-2 != len(zipcodes_in_text):
        diff = set(zipcodes_in_text)-set(zipcodes)
        print('Unreported zipcode: ' + ', '.join(diff))



    datematch = re.search('Data through (?P<date>[0-9]{1,2}/[0-9]{1,2}/2020)',txt)
    date = pd.Timestamp(datematch.groups()[0]).date()

    data = []
    for k in range(0,len(zipcodes)):
        zipcode=zipcodes[k]
        casespattern='[0-9]'*strlength[k]
        tokens = re.search(rf"(?P<zipcode>{zipcode})\n?(?P<Cases>{casespattern})\n?(?P<Rates>[0-9]+\.[0-9]|\*\*)",txt,re.IGNORECASE)
        data.append(tokens.groupdict())

    datadf = pd.DataFrame(data)
    datadf.index = datadf['zipcode']
    datadf = datadf.drop(columns='zipcode').transpose()
    datadf.index.name = 'Data through'
    datadf['Date Retrieved'] = [date_retrieved(pdffilepath), date_retrieved(pdffilepath)]

    cases_df = datadf.drop(index='Rates')
    cases_df = cases_df.rename(index={'Cases':date})

    rates_df = datadf.drop(index='Cases')
    rates_df = rates_df.rename(index={'Rates':date})

    cases_df = concat_dfs(cases_df,casesfilepath)

    rates_df = concat_dfs(rates_df,ratesfilepath)



    write_to_csv(cases_df,casesfilepath)
    write_to_csv(rates_df,ratesfilepath)
