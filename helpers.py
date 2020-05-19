from datetime import datetime

import pandas as pd
import re
import glob

# For PDF retrieval and parsing (required for city and zipcode data)
import PyPDF2
import requests

import pathlib

INCORPORATED_CITIES = []
def date_retrieved(pdffilepath):
    fname = pathlib.Path(pdffilepath)
    return pd.Timestamp(datetime.fromtimestamp(fname.stat().st_mtime)).ceil('s').strftime('%y-%m-%d %H:%m:%S')
    
def save_pdf_from_url(pdfurl,pdffilepath):
    r = requests.get(pdfurl)
    with open(pdffilepath,'wb') as f: 
        f.write(r.content) 
        
    
def write_to_csv(df,filepath):
    files_present = glob.glob(filepath)
    if files_present:
        write_df = pd.DataFrame(df.loc[df.index[-1]]).transpose()
        write_df.to_csv(filepath,mode='a',header=False)
    else:
        df.to_csv(filepath)   
        
def parse_daily_status(daily_status_url,daily_status_csv_filepath):
    
    # Grab and parse the data
    county_data = pd.read_html(daily_status_url)[0]
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
    df_final['Date Retrieved']=pd.Timestamp.now().round('s')

    # Write to CSV
    write_to_csv(df_final,daily_status_csv_filepath)
    
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
    txt = re.sub(',','',txt)
    
    # Parse the city data
    date = re.findall('Data through (?P<date>\d{1,2}/\d{1,2}/\d{4})',txt)[0]
    
    #Format change on 4/21
    if pd.Timestamp(date)>=pd.Timestamp('4/21/2020'):
        data = re.findall('(?P<city>[A-Za-z ]+[a-z])\*{0,4}\s+(?P<count>[,\d]+)\s*(?P<percentage>[0-9]+\.[0-9]+%)?\s+(\d+.\d+|\*{3})?',txt)
    else:
        data = re.findall('\s+(?P<city>[A-Za-z ]+[a-z])\*{0,4}\s+(?P<count>[,\d]+) (?P<percentage>[0-9.]+%)',txt)
    
    # Remove improper use of %
    df = data_to_df([(x[0],x[1]) for x in data],date,date_retrieved(pdffilepath))
    rates_df = data_to_df([(x[0],x[3]) for x in data],date,date_retrieved(pdffilepath))
    
    df_total = format_cities_df(df)
    rates_total = format_cities_df(rates_df)
    
    # Create dataframes
    df = pd.DataFrame.from_records(data).transpose()
    
    # Write to csv
    write_to_csv(df_total,casesfilepath)
    write_to_csv(rates_total,ratesfilepath)
    

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
    txt = re.sub('San Diego County T\n','TOTAL',txt)
    
    #prior_cases = pd.read_csv(casesfilepath)
    #prior_rates = pd.read_csv(ratesfilepath)
    #prior_cases = prior_cases.iloc[-1]
    #prior_rates = prior_rates.iloc[-1]
    #prior_cases = prior_cases.drop(['Data through','Date Retrieved'],axis=0)
    #prior_cases = prior_cases.fillna(0)
    #strlength = prior_cases.apply(lambda x: len(str(int(float(x)))))
    #zipcodes = prior_cases.index.values
    
    prior_cases = pd.read_csv(casesfilepath)
    prior_cases = prior_cases.iloc[-1]
    prior_cases = prior_cases.drop(['Data through','Date Retrieved'],axis=0)
    zipcodes,strlength = get_case_string_length(prior_cases)
    
    
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

    write_to_csv(cases_df,casesfilepath)
    write_to_csv(rates_df,ratesfilepath)


def get_case_string_length(prior_cases):
    prior_cases = prior_cases.fillna(0)
    strlength = prior_cases.apply(lambda x: len(str(int(float(x)))))
    indexvalues = prior_cases.index.values
    return indexvalues, strlength 
    
    
    
def data_to_df(data,date,date_ret):
    
    df = pd.DataFrame(data).transpose()
    
    df.columns = df.iloc[0]; df=df.iloc[1:]; df.columns.name = ''

    df = df.rename({'Unknown****':'Unknown','Unknown***':'Unknown','Unknown*\n':'Unknown','Unknown*':'Unknown','Unknown\n':'Unknown','TOTAL\n':'TOTAL','Total':'TOTAL','Total\n':'TOTAL'},axis=1) # REMOVE AFTER PDF FORMAT FIXED
    
    df['Date Retrieved']=date_ret
    df.index=[pd.Timestamp(date).date()]; df.index.name='Data through'
    return df
    
def extract_text_from_pdf(filepath):
    file = open(filepath,'rb')
    fileReader = PyPDF2.PdfFileReader(file)
    pg0 = fileReader.getPage(0)
    txt = pg0.extractText()
    file.close()
    return txt 
    
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
        
    