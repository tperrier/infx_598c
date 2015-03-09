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
	df['ground'] = GT[key]
	df = pd.concat([df,GT.loc[:,['economic','internet','mobiles','urban','english']]],axis=1)
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

def runModel(features,data,reg=0,verbose=0):
	if reg:
		model = ols("ground ~ "+features, data).fit_regularized(alpha=0.2,maxiter=1000,Lt_wt=1)
	else:
		model = ols("ground ~ "+features, data).fit()
	if verbose:
		print model.summary()
	else:
		print model.rsquared#+model.params+model.pvalues
	return model

def getDataSplit(data,count):
	print 'SIZE: %s'%data.shape[0]
	idx = np.arange(data.shape[0])
	np.random.shuffle(idx)
	bin_size = math.ceil(data.shape[0]/float(count))
	buckets = [idx[bin_size*i:bin_size*(i+1)] for i in xrange(count)]
	for i in range(count):
		frt = buckets[0:i]
		end = buckets[i+1:]
		front = []
		for e in frt:
			front.extend(e)
		for e in end:
			front.extend(e)
		print front
		yield data.iloc[front], data.iloc[buckets[i]]



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