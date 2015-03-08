import numpy as np
import pandas as pd
from sklearn import datasets, linear_model
import collections,os
from code import interact as CI

DATA_DIR = 'data'
#GROUND KEYS: year	hiv	tb	economic	internet	mobiles	urban	english

def get_csv(key):
	#Return the csv file for key name
	filename = os.path.join(DATA_DIR,'%s.csv'%key)
	return pd.read_csv(filename)
#Get ground truth data
GT = get_csv('ground')

def get_data(key,**kwargs):
	if key not in ['hiv','tb']:
		raise ValueError('Data for key %s not found'%s)
	#DATA KEYS: country	year	zeros	1	2	3	4	5	6	7	8	9	10	11	12
	df = get_csv(key)
	df = pd.concat([df,GT.loc[:,[key,'economic','internet','mobiles','urban','english']]],axis=1)
	df = df.dropna() #Drop all rows with a nan in it

	#filter rows with more than 5 zeros
	df = filter_years(df,year=kwargs.get('year',2011))
	df = filter_zeros(df)
	return df

def filter_years(df,year=2011):
	years = df.loc[:,'year']
	return df[years>=year]

def filter_zeros(df):
	zeros = df.loc[:,'zeros']
	return df[zeros<=5]


'''
zeros = data[:,2]
years = data[:,1]
d_filter = np.logical_and(np.logical_and(zeros<=5,years>=2011),~np.isnan(ground[:,ground_index]))
# d_filter = ~np.isnan(ground[:,ground_index])
dx = data[d_filter,3:]
dy = ground[d_filter,ground_index]
code.interact(local=locals())

lin = linear_model.LinearRegression()

lin.fit(dx,dy)

print lin.score(dx,dy)
'''