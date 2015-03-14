import numpy as np
import pandas as pd
from sklearn import datasets, linear_model
import matplotlib.pyplot as plt
from statsmodels.formula.api import ols
import statsmodels.api as sm
import statsmodels.graphics.regressionplots
import collections,os
from code import interact as CI

DATA_DIR = 'data'
COLORS = ['red','grey','blue','green']
DEFAULT_FEATURES = 'median+sd'

def get_csv(key):
	#Return the csv file for key name
	filename = os.path.join(DATA_DIR,'%s.csv'%key)
	return pd.read_csv(filename)
#Get ground truth data
#GROUND KEYS: year	hiv	tb	economic	internet	mobiles	urban	english
GT = get_csv('ground')
GT_LABELS = ['economic','internet','mobiles','urban','english','literacy','population']

def get_data(key,**kwargs):
	if key not in ['hiv','tb']:
		raise ValueError('Data for key %s not found'%s)
	#DATA KEYS: country	year	zeros	1	2	3	4	5	6	7	8	9	10	11	12
	df = get_csv(key)
	df['ground'] = GT[key]
	df = pd.concat([df,GT.loc[:,GT_LABELS]],axis=1)
	df = df.dropna() #Drop all rows with a nan in it

	#filter rows with more than 5 zeros
	df = filter_years(df,year=kwargs.get('year',2011))
	df = filter_zeros(df,count=kwargs.get('count',5))
	return df

def get_dataset_stats(**kwargs):
	for key in ['hiv','tb']:
		df = get_csv(key)
		total_size = df.shape[0]
		df = filter_years(df,year=kwargs.get('year',2011))
		size_years = df.shape[0]
		df['ground'] = GT[key]
		df = pd.concat([df,GT.loc[:,GT_LABELS]],axis=1)
		df = df.dropna()
		size_ground = df.shape[0]
		df = filter_zeros(df,count=kwargs.get('count',5))
		size_zero = df.shape[0]
		print '%s,%s,%s,%s,%s'%(key,total_size,size_years,size_ground,size_zero)

def filter_years(df,year=2011):
	years = df.loc[:,'year']
	return df[years>=year]

def filter_zeros(df,count=5):
	zeros = df.loc[:,'zeros']
	return df[zeros<=count]

def filter_country(df,country):
	return df[df.country == country]

def split_by(df,key,n=4):
	quartiles = get_quartiles(df,key,n=n)
	for s in range(n):
		yield df.loc[quartiles==s]

def get_quartiles(df,key,n=4,labels=False):
	return pd.qcut(df[key],n,labels=labels)

def get_colors(df,key,n=4):
	return get_quartiles(df,key,n,labels=COLORS)

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

def get_scatter_grid_plot(df,features=['internet', 'economic', 'mobiles', 'literacy', 'urban'],colorkey='internet'):
	if colorkey=='':
		pd.tools.plotting.scatter_matrix(df[features],marker='o',color='blue')
	else:
		pd.tools.plotting.scatter_matrix(df[features],marker='o',color=get_colors(df,colorkey))
	plt.draw()

def get_fitted_graph(df,ax,features=['median','sd'],label='HIV'):
	model = sm.OLS(df['ground'], df[features])
	results = model.fit()
	#fig, ax = plt.subplots()
	fig = sm.graphics.plot_fit(results, 0, ax=ax)
	#ax.set_ylabel("%s Ground"%label)
	#ax.set_xlabel("Internet Query Level")
	#ax.set_title("Linear Regression")
	#plt.draw()

def get_residue_graph(df,features=['median','sd'],label='HIV',exog_feature='median'):
	model = sm.OLS(df['ground'], df[features])
	results = model.fit()
	fig, ax = plt.subplots()
	x1 = results.model.exog[:]
	ax.plot(x1, results.resid, 'o')
	ax.axhline(y=0, color='black')
	ax.set_title('Residuals versus %s' % exog_feature, fontsize='large')
	ax.set_xlabel(exog_feature)
	ax.set_ylabel("resid")
	plt.draw()

def get_all_fitted_graphs(df,features=['median','sd'],split='internet',label='HIV'):
	fig = plt.figure(figsize=(8,6))
	grid_val = 220
	q_i=1
	lb=['a','b','c','d']
	for dt in split_by(df,split):
		ax = fig.add_subplot(grid_val+q_i)
		get_fitted_graph(dt,ax,features=features,label=label)
		ax.set_title('( %s )'%lb[q_i-1])
		q_i=q_i+1

def run_levels(data,features=DEFAULT_FEATURES,n=4):
	columns = ['q%i'%i for i in range(n)]+['all']
	table = {c:[] for c in columns}
	print 'Running Levels: %s'%features
	for label in GT_LABELS:
		for ix,split in enumerate(split_by(data,label,n)):
			model = runModel(split,features,verbose=-1)
			table[columns[ix]].append(model.rsquared)
		model = runModel(data,features,verbose=-1)
		table['all'].append(model.rsquared)
	return pd.DataFrame(data=table,index=[l for l in GT_LABELS])

def run_country(df,country,features=DEFAULT_FEATURES):
	df = filter_country(df,country)
	print '%s %s'%(country,df.shape)
	if df.shape[0] > 1:
		model = runModel(df,features)
		return model
	return None

def run_countries(data,features=DEFAULT_FEATURES):
	for country in data.country.unique():
		run_country(data,country,features)

def graph_levels(data,features=DEFAULT_FEATURES,n=4):
	df = run_levels(data,features,n)
	df.T.drop('all').plot()
	return df


def show_stats(df):
	print df.loc[:,['country','year','ground','avg','median','sd','economic','mobiles','internet']]


def runModel(data,features=DEFAULT_FEATURES,reg=0,verbose=0,**kwargs):
	if verbose > -1:
		print 'Making Model: %s Data Shape: %s'%(features,data.shape)
	if reg:
		alpha = kwargs.get('alpha',0.2)
		maxiter = kwargs.get('maxiter',1000)
		wt = kwargs.get('wt',1)
		model = ols("ground ~ "+features, data).fit_regularized(alpha=alpha,maxiter=maxiter,L1_wt=wt)
	else:
		model = ols("ground ~ "+features, data).fit()
	if verbose > 0:
		print model.summary()
	elif verbose == 0:
		print 'R2: %.4f  Std(ys) %.2f Std(res) %.2f'%(model.rsquared,model.model.endog.std(),model.resid.std())
		for name,param in model.params.iteritems():
			pvalue = model.pvalues[name]
			print '  -> %s  %0.4f (%.4f)'%(name,param,pvalue)
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