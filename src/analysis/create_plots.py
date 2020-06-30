import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

from numpy.polynomial import polynomial as P
import matplotlib.pyplot as plt


THIS_PATH = os.path.abspath(os.path.dirname(__file__))
PLOTS_FILE_DIRECTORY = os.path.join(THIS_PATH,'../../plots')
CSV_FILE_DIRECTORY = os.path.join(THIS_PATH,'../../csv')

# Load the data and find differences
sddata = pd.read_csv(os.path.join(CSV_FILE_DIRECTORY,'sandiego_data_by_zipcode.csv'),index_col=0)
sddata = sddata.drop(columns='Date Retrieved').fillna(0)
sddata.sort_values(sddata.index[-1],axis=1,ascending=False,inplace=True)
sddiff = sddata.diff()

seven_day_average = sddiff.rolling(7).mean()

# Get linear fit to most recent 7 days
days = np.arange(0,7)
fitfun = lambda cases: P.polyfit(days,cases,1)
fit = sddiff.iloc[-7:,:].apply(fitfun)
fit['fit_coef'] = ['c0','c1']
fit = fit.set_index('fit_coef')

# Bin by rate of increase
df = fit.transpose()
bins = [-10,-.5,-.25,.25,.5,10]
df['bin'] = pd.cut(df.c1,bins,labels=['decreasing fastest','decreasing','about the same','increasing','increasing fastest'])
df[df.bin=='increasing fastest']

colormap = {'decreasing fastest':'blue','decreasing':'green','about the same':'yellow','increasing':'orange','increasing fastest':'red'}
df = df.replace({"bin": colormap})
df = df.rename(columns={'bin': 'color'})
df.index.name = 'zip'
df['color'].to_frame()
df['label']=df["color"].replace({v: k for k, v in colormap.items()})

# Create Figures
from jdcv19.figures.figures import create_map, create_timeseries, link_map_and_timeseries
from jdcv19.gis.gis import ZipCodeGIS
from jdcv19.dataset.accessors import ZipAccessor, TSAccessor
from jdcv19.figures.figures import create_map, create_timeseries

from bokeh.plotting import figure, output_file
from bokeh.io import show
from bokeh.layouts import row, column

#from bokeh.resources import CDN
#from bokeh.embed import file_html

output_file(os.path.join(PLOTS_FILE_DIRECTORY,'new_cases.html'), title='San Diego Covid-19 Plots')
 
gis = ZipCodeGIS(sddata.columns)
title = "San Diego County: Hover to Select Zip Code"
mapfig = create_map(gis,df[['color','label']],title=title)


tsfig = create_timeseries(seven_day_average.drop(columns=['Unknown','TOTAL']),title="New Cases Per Day by Selected Zip Code")
(mapfig, tsfig) = link_map_and_timeseries(mapfig,tsfig,seven_day_average.ts.value_dict)


total_ts = figure(height=530,width=400,x_axis_type='datetime',x_axis_label='Date',
                  y_axis_label='Reported New Cases Per Day',title='San Diego County: New Reported Cases Per Day')
# add a circle renderer with a size, color, and alpha
total_ts.circle(pd.to_datetime(sddiff.index),sddiff['TOTAL'].values, size=5, color="navy", alpha=0.5,legend_label="Reported New Cases")
total_ts.line(pd.to_datetime(seven_day_average.index),seven_day_average['TOTAL'].values,legend_label="Seven Day Average")
total_ts.toolbar.logo = None
total_ts.toolbar_location = None

show(column(row(mapfig,total_ts),tsfig))

#html = file_html(column(row(mapfig,total_ts),tsfig),CDN,os.path.join(PLOTS_FILE_DIRECTORY,'new_cases.html'))
