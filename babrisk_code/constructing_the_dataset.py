# This script can be used to re-create the dataset used in: Stomper A., Radwanski J. "Babylonian Risk Aversion".

# The code is organized in nine steps. Steps (0)-(6) construct and save the output data based on a given sample selection criterion (one of several possible). 
# In steps (7)-(8), all previously created output can be merged and saved as a single Excel file.
 
# (0) Importing the necessary packages, including jdcal (used for calendar conversion).
# (1) Downloading and cleaning the data, adding our own definitions of PART.
# (2) Assigning the Julian Date (JD; see https://en.wikipedia.org/wiki/Julian_day) to each observation recorded in the sample, 
# using the jdcal package, and the conversion tables between the Babylonian and Julian calendars,
# prepared on the basis of Christopher J. Bennett's tables: 
# http://www.tyndalehouse.com/egypt/ptolemies/chron/babylonian/chron_bab_cal.htm. 
# In this step, the user can decide on the version of PART assignment,
# and on the subset of data based on information quality (the less-certain observations 
# are encoded by italic font in the original data of van der Spek) by 
# modifying lines 139-142.  
# (3) Generating expanded set of daily data, and filling it with Gregorian dates, 
# again using jdcal package.
# (4) Defining the indicator variables for the growing/harvest periods (of barley and dates) 
# in the daily dataset, based on the computed Gregorian months and days.
# (5) The daily set with harvest information is collapsed 
# to one with with non-missing price data.
# (6) Computing the returns, and (fractional) growing/harvest indicators. In this step,
# the resulting output is saved to a .pkl file.

# (7) Saving the columns that are common to all datasets, using the broadest range of available 
# observations. The user can ignore step (7) by leaving the code commented out, 
# if the file 'fixed.pkl' is already in the working directory. 
# (8) Merging all previously constructed (and saved) pieces of output,  
# and saving as a single Excel file.

#------------------------------------------------------------------------------
## Step (0)

import pandas as pd
import numpy as np
import os
import jdcal

##-----------------------------------------------------------------------------
## Step (1)

absolute_path = os.path.dirname(__file__)
relative_path_xlsx = 'OriginalData\\babylonia.xlsx'
path_xlsx = os.path.join(absolute_path, relative_path_xlsx)

mydata = pd.read_excel(path_xlsx, sheet_name='Blad1', skipfooter=14)

relative_path_to_append = 'PartDefinitions\\part_definitions.xlsx'
path_to_append = os.path.join(absolute_path, relative_path_to_append)
to_append = pd.read_excel(path_to_append, usecols=[3,4])

mydata = pd.concat((mydata,to_append), axis=1, join='inner')

mydata = mydata.replace(r'^\s+$', np.nan, regex=True)

mydata['LogS_B'] = np.log(mydata['Bar-interpretatie'])
mydata['LogS_D'] = np.log(mydata['Dat-interpretatie'])

mydata = mydata.rename(columns={'Year ':'Year'})

invalid_months = ['I ','X   ','VII ','VI  ','X ','XI  ','XI   ','IV  ','VII   ','XII ','II?',
 'V   ','IX  ','IX    ','VI ','V ','III ','IX ','X  ','I  ','I-IV',
 'VI    ','II  ','I of XIIB','XII?','I   ','XII  ','XII      ','II ',
 'II    ','II     ','VIII ','XI ','IV?','IV ','V  ','VI   ','XI    ','I     ',
 'I','II','III','IV','V','VI','VIB','VII','VIII','IX','X','XI','XII','XIIB']
valid_months = ['I','X','VII','VI','X','XI','XI','IV','VII','XII',np.nan,
 'V','IX','IX','VI','V','III','IX','X','I',np.nan,'VI','II',np.nan,np.nan,
 'I','XII','XII','II','II','II','VIII','XI',np.nan,'IV','V','VI','XI','I',
 'I','II','III','IV','V','VI','VIB','VII','VIII','IX','X','XI','XII','XIIB']
invalid_months_map = dict(zip(invalid_months,valid_months))
mydata['MON'] = mydata['MON'].map(invalid_months_map)

months_orig = ['I','II','III','IV','V','VI','VIB','VII','VIII','IX','X','XI','XII','XIIB']
months_bab = ['Nisanu','Aiaru','Simanu','Duzu','Abu','Ululu','Ululu II','Tashritu',
    'Arahsamnu','Kislimu','Tebetu','Shabatu','Addaru','Addaru II']
months_num = [1,2,3,4,5,6,6.5,7,8,9,10,11,12,12.5]
months_map_to_babnames = dict(zip(months_orig,months_bab))
mydata['MONB'] = mydata['MON']
mydata = mydata.replace({'MONB':months_map_to_babnames})
months_map_to_nums = dict(zip(months_orig,months_num))
mydata['MONN'] = mydata['MON']
mydata = mydata.replace({'MONN':months_map_to_nums})

mydata = mydata.dropna(subset=['YEAR','MON'],how='any') 
mydata = mydata[['YEAR','MON','MONB','MONN','Year','Mon','Day','PART','PARTclass_v0',
    'PARTclass_v1','LogS_B','LogS_D','italicBarint','italicDatint']]

##-----------------------------------------------------------------------------
## Step (2)

# Reading our Excel versions of Christopher J. Bennett's tables:
relative_path_month_table = 'ConversionTables\\month_table.xlsx'
relative_path_day_table = 'ConversionTables\\day_table.xlsx'
path_month_table = os.path.join(absolute_path, relative_path_month_table)
path_day_table = os.path.join(absolute_path, relative_path_day_table)

month_table = pd.read_excel(path_month_table)
month_table.index = month_table['Year_Left']
day_table = pd.read_excel(path_day_table)
day_table.index = day_table['Year_Left']

T = len(mydata.index)
jd = np.zeros(T)

# The loop below asssigns the Julian Date to every observation.
# The Bennett's tables inform about the first day of each Babylonian month;
# We add 4, 14, or 24 days (by convention), depending on PART classification.  
 
counter = 0 
for index, row in mydata.iterrows():
    part_now = row['PARTclass_v1']
    year_julian_bc_now = row['Year']
    year_julian_ce_now = -(year_julian_bc_now-1)
    
    if year_julian_bc_now >= 331: 
        
        month_julian_now = row['Mon']
        day_julian_now = row['Day']
        jd_now = jdcal.jcal2jd(year_julian_ce_now,month_julian_now,day_julian_now)
        jd[counter] = sum(jd_now)+4
        
    if year_julian_bc_now < 331: 
        
        year_left_index_now = -row['YEAR']+1 
        month_bab_now = row['MONB'] 
        month_julian_now = month_table.loc[year_left_index_now,month_bab_now]
        day_julian_now = day_table.loc[year_left_index_now,month_bab_now]
        jd_now = jdcal.jcal2jd(year_julian_ce_now,month_julian_now,day_julian_now)
        if part_now == 'b':
            jd[counter] = sum(jd_now)+4
        if part_now == 'm':
            jd[counter] = sum(jd_now)+14
        if part_now == 'e':
            jd[counter] = sum(jd_now)+24

    counter = counter+1

mydata = mydata.assign(JD=jd)
mydata_yearmonth = mydata.groupby('JD')[['YEAR','MON','PARTclass_v0','PARTclass_v1']].first()
mydata = mydata.sort_values('JD')
mydata.index = mydata['JD']

PARTclass_v0 = (mydata['PARTclass_v0']=='b')|(mydata['PARTclass_v0']=='m')|(mydata['PARTclass_v0']=='e')
PARTclass_v1 = (mydata['PARTclass_v1']=='b')|(mydata['PARTclass_v1']=='m')|(mydata['PARTclass_v1']=='e')
allavail = (mydata.index>0)
nonital = (mydata['italicBarint']==0) & (mydata['italicDatint']==0)

##--------------------
# Define the subset of the data by uncommenting exactly one row 150-153: 
#subset = PARTclass_v1 & allavail; postfix = '__PT1_ALL' # 97 obs
#subset = PARTclass_v1 & nonital; postfix = '__PT1_NIT' # 59 obs
#subset = PARTclass_v0 & allavail; postfix = '__PT0_ALL' # 62 obs
subset = PARTclass_v0 & nonital; postfix = '__PT0_NIT' # 38 obs
##--------------------

mydata = mydata[['JD','LogS_B','LogS_D']]
mydata = mydata.loc[subset,:]
mydata = mydata.groupby(mydata.index).mean()
mydata = mydata.dropna(subset=['LogS_B','LogS_D'],how='any')
mydata_allpaired = mydata

## Step (3)
##-----------------------------------------------------------------------------

first_day = int(mydata.index[0]-0.5)
last_day = int(mydata.index[-1]-0.5)
jd_index = pd.Series(range(first_day,last_day+1))+0.5
mydata_alldays = mydata.reindex(jd_index,fill_value=np.nan)
mydata_alldays = mydata_alldays[['JD']]
Tlong = len(mydata_alldays.index)
juliandays_all = np.zeros((Tlong,2))
juliandays_all[:,0] = 2400000.5
juliandays_all[:,1] = jd_index-2400000.5
gregorian_all = np.zeros((Tlong,4))
for t in range(Tlong):
    jd_now = tuple(juliandays_all[t,:])
    gregorian_all[t,:] = jdcal.jd2gcal(*jd_now)
mydata_alldays = mydata_alldays.assign(GYEAR=gregorian_all[:,0])
mydata_alldays = mydata_alldays.assign(GMONTH=gregorian_all[:,1])
mydata_alldays = mydata_alldays.assign(GDAY=gregorian_all[:,2])

##-----------------------------------------------------------------------------
# Step (4)

def insert_season(dataset,begin_m,begin_d,end_m,end_d,new_varname):
    gmonth = dataset['GMONTH']; gday = dataset['GDAY']
    condition = ((gmonth==begin_m) & (gday>=begin_d)) | ((gmonth>begin_m) & (gmonth<end_m)) | ((gmonth==end_m) & (gday<=end_d))
    dataset[new_varname] = np.where(condition,1,0)

# Any additional growing/harvest periods can be defined here, in a similar way:
# If this is done, the lists of variables (currently lines: 198, 223, 227) should be updated/extended. 
insert_season(mydata_alldays,3,1,5,30,'BH_3_5')
insert_season(mydata_alldays,8,1,10,30,'DH_8_10')

##-----------------------------------------------------------------------------
# Step (5):

reg_varnames = ['BH_3_5','DH_8_10']
mydata_alldays = mydata_alldays.fillna(method='ffill')
mydata_daycount = mydata_alldays.groupby('JD')[reg_varnames].sum()
mydata_daycount[['GYEAR','GMONTH','GDAY']] = mydata_alldays.groupby('JD')[['GYEAR','GMONTH','GDAY']].first()
mydata = mydata.merge(mydata_daycount,how='inner',left_index=True,right_index=True)
mydata = mydata.merge(mydata_yearmonth,how='inner',left_index=True,right_index=True)

#-----------------------------------------------------------------------------
# Step (6):

mydata['SG_B'] = mydata['LogS_B'].diff().shift(-1)
mydata['SG_D'] = mydata['LogS_D'].diff().shift(-1)
mydata['DG_B'] = mydata['SG_B']-mydata['SG_D']
mydata['DAY_DIFF'] = mydata['JD'].diff().shift(-1)
mydata = mydata.dropna(subset=['DAY_DIFF'],how='any')
mydata['SG_B'] = mydata['SG_B']/mydata['DAY_DIFF']*10 # the 'per-ten-days' convention; use *30 for 'per-month', etc.
mydata['SG_D'] = mydata['SG_D']/mydata['DAY_DIFF']*10
mydata['DG_B'] = mydata['DG_B']/mydata['DAY_DIFF']*10
for i in reg_varnames:
    mydata[i] = mydata[i]/mydata['DAY_DIFF']
    mydata[i+'_C'] = 1-mydata[i]
tdelta_max = 30*6
mydata = mydata[mydata['DAY_DIFF']<=tdelta_max]

# Organizing and saving the current dataset (for given choice of the 'subset' variable):
mydata = mydata[['YEAR','MON','PARTclass_v0','PARTclass_v1','GYEAR','GMONTH','GDAY',\
    'LogS_B','LogS_D','SG_B','SG_D','DG_B','DAY_DIFF','BH_3_5','DH_8_10']]

mydata.rename(columns={'SG_B':'SG','DG_B':'DG'}, inplace=True) # dropping the numeraire info
colnames_init = ['SG','DG','DAY_DIFF','BH_3_5','DH_8_10']
mydata_tosave = mydata[colnames_init]
colnames_renamed = [colname+postfix for colname in colnames_init]
mydata_tosave.columns = colnames_renamed
picklename = 'dataset'+postfix+'.pkl'
mydata_tosave.to_pickle(picklename)

##-----------------------------------------------------------------------------
## Step (7):

# Uncomment lines 238-239 and run just once, with the broadest subset of the data (uncommented line 150 - __PT1_ALL).
# mydata_fixed = mydata[['GYEAR','GMONTH','GDAY']]
# mydata_fixed.to_pickle('fixed.pkl')

##-----------------------------------------------------------------------------
## Step (8):

# Merging all output into a single Excel file.
# Uncomment lines 248-263 after constructing all datasets and making sure 
# that 'fixed.pkl' has been created and saved in Step (7). 

fixed = pd.read_pickle('fixed.pkl')
final_data = fixed

mydata__PT1_ALL = pd.read_pickle('dataset__PT1_ALL.pkl')
mydata__PT1_NIT = pd.read_pickle('dataset__PT1_NIT.pkl')
mydata__PT0_ALL = pd.read_pickle('dataset__PT0_ALL.pkl')
mydata__PT0_NIT = pd.read_pickle('dataset__PT0_NIT.pkl')

final_data = final_data.merge(mydata__PT1_ALL,how='outer',left_index=True,right_index=True)
final_data = final_data.merge(mydata__PT1_NIT,how='outer',left_index=True,right_index=True)
final_data = final_data.merge(mydata__PT0_ALL,how='outer',left_index=True,right_index=True)
final_data = final_data.merge(mydata__PT0_NIT,how='outer',left_index=True,right_index=True)

final_data.reset_index(inplace=True)
final_data = final_data.drop(['JD'],axis=1)
final_data.index.rename('INDEX',inplace=True)

filename_to_save = 'final_dataset.xlsx'
final_data.to_excel(filename_to_save) 