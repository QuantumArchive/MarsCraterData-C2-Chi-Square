# -*- coding: utf-8 -*-
"""
Created on Tue June 6 14:16:48 2016

@author: Chris
"""
import pandas
import numpy
import matplotlib.pyplot as plt
import seaborn
import statsmodels.formula.api as smf
import scipy.stats
import itertools
#from IPython.display import display
%matplotlib inline

#bug fix for display formats to avoid run time errors
pandas.set_option('display.float_format', lambda x:'%f'%x)

#Set Pandas to show all columns in DataFrame
pandas.set_option('display.max_columns', None)
#Set Pandas to show all rows in DataFrame
pandas.set_option('display.max_rows', None)

#data here will act as the data frame containing the Mars crater data
data = pandas.read_csv('D:\\Coursera\\marscrater_pds.csv', low_memory=False)

#convert the latitude and diameter columns to numeric and ejecta morphology is categorical
data['LATITUDE_CIRCLE_IMAGE'] = pandas.to_numeric(data['LATITUDE_CIRCLE_IMAGE'])
data['DIAM_CIRCLE_IMAGE'] = pandas.to_numeric(data['DIAM_CIRCLE_IMAGE'])
data['MORPHOLOGY_EJECTA_1'] = data['MORPHOLOGY_EJECTA_1'].astype('category')

#Any crater with no designated morphology will be replaced with NaN
data['MORPHOLOGY_EJECTA_1'] = data['MORPHOLOGY_EJECTA_1'].replace(' ',numpy.NaN)

#'We'll define the region between -30 and 30 to be equatorial and -90 to -30 and 30 to 90 to be at the pole
def georegion(x):
    if x <= -30:
        return 'POLE'
    elif x <= 30:
        return 'EQUATOR'
    else:
        return 'POLE'

data['LATITUDE_BIN'] = data['LATITUDE_CIRCLE_IMAGE'].apply(georegion)

#Next we split the crater diameters into 4 quartiles to capture the category of crater diameter by percentile
data['DIAM_CIRCLE_BIN'] = pandas.qcut(data['DIAM_CIRCLE_IMAGE'],4)
data['DIAM_CIRCLE_BIN'] = data['DIAM_CIRCLE_BIN'].astype('category')

#recode POLE and EQUATOR to 0 and 1
recodedict = {'POLE':0,'EQUATOR':1}
data['LATITUDE_BIN_RECODE'] = data['LATITUDE_BIN'].map(recodedict)

#contingency table of observed counts
ct1 = pandas.crosstab(data['LATITUDE_BIN'],data['DIAM_CIRCLE_BIN'])
ct1

#divide the contingency table by the sum of each column to get the relative ratio of craters either at the equator and those at the poles
colsum = ct1.sum(axis=0)
colpct = ct1/colsum
print colpct

#chi-square
print('chi-square value, p value, expected counts')
cs1 = scipy.stats.chi2_contingency(ct1)
print(cs1)

#For our post-hoc analysis for the Chi-Square tests, we want to look at the correlation between the 
#different explanatory variables (crater size bin). We first get get a combination of 2 columns from the contingency table
#using itertools, we can then run a Chi-Square test on the subsetted table. For ease of viewing,
#a data frame is created with the explanatory variable and the associated p values given the response variables
p1 = itertools.combinations([x for x in range(len(colpct.columns))],2)

list1 = []
list2 = []

for a in p1:
    colpct2 = colpct.iloc[:,a]
    ct2 = ct1.iloc[:,a]
    cs2 = scipy.stats.chi2_contingency(ct2)
    print('')
    print(colpct2)
    print('')
    print(ct2)
    print('')
    print(cs2)
    templist = list(cs2)
    list1.append(colpct2.columns[0] + ',' + colpct2.columns[1])
    list2.append(templist[1])

newdataframe = pandas.DataFrame({'DIAM_CIRCLE_BIN COMPARISON':list1,'P VALUES':list2})
newdataframe

#Finally we plot the the relative ratio of equatorial craters to polar craters. Above 0.5 would mean that the craters in that bin
#are more weighted towards the equator, whereas a mean less then 0.5 would indicate greater weighting towards the poles.
seaborn.factorplot(x='DIAM_CIRCLE_BIN',y='LATITUDE_BIN_RECODE',kind='bar',data=data,ci=None)
plt.xlabel('DIAM_CIRCLE_BIN (KM)')
plt.ylabel('MEAN OF EQUATORIAL/POLAR CRATERS')
plt.xticks(rotation='vertical')