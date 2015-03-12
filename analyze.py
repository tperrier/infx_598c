import numpy as np
import pandas as pd
from sklearn import datasets, linear_model
import matplotlib.pyplot as plt
from statsmodels.formula.api import ols
import collections,os
from code import interact as CI

DATA_DIR = 'data'
COLORS = ['red','grey','blue','green']
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
	quartiles = get_quartiles(df,key)
	for s in range(4):
		yield df.loc[quartiles==s]

def get_quartiles(df,key,labels=False):
	return pd.qcut(df[key],4,labels=labels)

def get_colors(df,key):
	return get_quartiles(df,key,labels=COLORS)

def get_graphs(df,feature='range',key='economic'):
	fig = plt.figure(figsize=(8,6))
	grid_val = 220
	q_i=1
	for i,data in enumerate(split_by(df,key)):
		ax = fig.add_subplot(grid_val+q_i)
		get_graph(ax,q_i,data,feature,key,colors=COLORS[i])
		q_i=q_i+1
	plt.show()

def get_graph_all(df,key='internet'):
	features = ['range','sd','median','sum']
	fig = plt.figure(figsize=(8,6))
	grid_val = 220
	q_i=1
	colors=get_colors(df,key)
	for f in features:
		ax = fig.add_subplot(grid_val+q_i)
		get_graph(ax,q_i,df,f,key,colors=colors)
		q_i=q_i+1
	plt.show()

def get_graph(ax,level,df,feature='range',key='economic',colors='black'):
	model = runModel(df,feature)
	plt.scatter(df['ground'],df[feature],  color=colors,label='Ground Truth')
	dX = pd.DataFrame({feature:np.arange(0,df['ground'].max()+5,0.25)})
	plt.plot(dX, model.predict(dX), color='black',linewidth=3, label='Model')
	ax.set_xlabel('ground truth (%s)'%key)
	ax.set_ylabel(feature)
	title='%s'%key
	if level==1: 
		title='Low '+title
	elif level==2:
		title='Low middle '+title
	elif level==3:
		title='High middle '+title
	elif level==4:
		title='High '+title
	ax.set_title("%s (R Sq: %0.2f)"%(title,model.rsquared))


def run_levels(data,features='median+sd'):
	split_labels = ['economic','internet','mobiles','urban','english']
	table = []
	df = pd.DataFrame(columns=['split','l0','l1','l2','l3','all'])
	print features
	for ix,label in enumerate(split_labels):
		row = [label]
		for split in split_by(data,label):
			model = runModel(split,features,verbose=-1)
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