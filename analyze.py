import numpy as np
import pandas as pd
from sklearn import datasets, linear_model
import matplotlib.pyplot as plt
from statsmodels.formula.api import ols
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

def split_by(df,key):
	quartiles = pd.qcut(df[key],4,labels=False)
	for s in range(4):
		yield df.loc[quartiles==s]

def run_levels(data,features='median+sd'):
	split_labels = ['economic','internet','mobiles','urban','english']
	table = []
	df = pd.DataFrame(columns=['split','l0','l1','l2','l3','all'])
	print features
	for ix,label in enumerate(split_labels):
		row = [label]
		for split in split_by(data,label):
			model = runModel(split,features,verbose=0)
			row.append(model.rsquared)
		model = runModel(data,features,verbose=-1)
		row.append(model.rsquared)
		df.loc[ix] = row
		table.append(row)
		
	return df

def show_stats(df):
	print df.loc[:,['country','year','ground','avg','median','sd','economic','mobiles','internet']]


def runModel(data,features,reg=0,verbose=0,**kwargs):
	if verbose > -1:
		print 'Making Model: %s Data Shape: %s'%(features,data.shape)
	if reg:
		alpha = kwargs.get('alpha',0.2)
		maxiter = kwargs.get('maxiter',1000)
		wt = kwargs.get('wt',1000)
		model = ols("ground ~ "+features, data).fit_regularized(alpha=alpha,maxiter=maxiter,L1_wt=wt)
	else:
		model = ols("ground ~ "+features, data).fit()
	if verbose > 0:
		print model.summary()
	elif verbose == 0:
		print 'R2: %s Coef: %s'%(model.rsquared,model.params)
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