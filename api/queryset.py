import requests,json,pickle,operator,csv,time,sys,itertools
import code

import utils

class QueryGroup(object):

	def __init__(self,query,code,geo=True):
		'''
		group_by: q for query, c for country
		'''
		self.query = utils.make_list(query)
		self.cmpt = utils.make_list(code)
		self.geo = geo
		self.queries = []

		if self.geo is False:
			_query = query
			self.query = cmpt
			self.cmpt = _query

	def get(self,timeout=1,normalize=True):
		for q in self.query:
			query = QuerySet(query=q,cmpt=self.cmpt,geo=self.geo).get()
			if normalize:
				query.normalize()
			self.queries.append(query)
			time.sleep(timeout)
		return self

	def normalize(self):
		#get the max for all queries
		counts = [[] for i in self.cmpt]
		for q in self:
			for i,l in enumerate(q.leaves()):
				counts[i].append(l[1])

		#find the cmpt item with the smallest standard deviation across quires
		sd_list = map(utils.sd,counts)
		imin = min(xrange(len(sd_list)),key=sd_list.__getitem__)

		#For now assume len(self) < 6
		max_list = [j[1] for j in QuerySet(query=self.cmpt[imin],cmpt=[q.query for q in self],geo= not self.geo).get()]

		print self
		for i,q in enumerate(self):
			print max_list[i]
			q.rescale(max_list[i]/100.0)
		print self

		code.interact(local=locals())

	def csv_rows(self,**kwargs):
		for q in self.queries:
			for r in q.csv_rows(**kwargs):
				yield r

	def csv_all(self,filename,**kwargs):
		print 'Making CSV File: %s'%filename
		with open(filename,'w') as fp:
			csvfp = csv.writer(fp)
			#write header
			header = ['query','country','year'] + [str(i) for i in range(1,13)]
			if kwargs.get('avg',False):
				header.append('avg')
			csvfp.writerow(header)
			#write csv_rows
			for r in self.csv_rows(**kwargs):
				csvfp.writerow(r)

	def csv_query(self,query,**kwargs):
		try:
			qindex = self.query.index(query)
		except ValueError as e:
			print 'Query: %s not found in %s'%(query,self.query)
		#make file name and make header
		filename = '%s.csv'%query
		print 'Making CSV File: %s'%filename
		header = ['country','year','zeros']+[str(i) for i in range(1,13)]
		if kwargs.get('avg',False):
			header.append('avg')
		#write csv file
		kwargs['query'] = False
		kwargs['zeros'] = True
		with open(filename,'w') as fp:
			csvfp = csv.writer(fp)
			csvfp.writerow(header)
			#write csv rows
			for r in self.queries[qindex].csv_rows(**kwargs):
				csvfp.writerow(r)





	def make_json(self,filename):
		print 'Making JSON File: %s'%filename
		with open(filename,'w') as fp:
			json.dump(self.toJSON(),fp)


	def toJSON(self):
		_o = {'query':self.query,'cmpt':self.cmpt,'geo':self.geo,'queries':[q.toJSON() for q in self.queries]}
		return _o

	def __repr__(self):
		_s = ['%s [%s] geo=%s'%(self.query,self.cmpt,self.geo)]
		for q in self.queries:
			_s.append(q.query[0])
			_s.append(str(q))
		return '\n'.join(_s)

	@classmethod
	def fromJSON(cls,data):
		_o = cls(data['query'],data['cmpt'],data['geo'])
		_o.queries = [QuerySet.fromJSON(d) for d in data['queries']]
		return _o


class QuerySet(object):

	def __init__(self,query,cmpt,geo=False,parent=None):
		self.cmpt = utils.make_list(cmpt)
		self.query = utils.make_list(query)
		self.geo = geo
		self.parent = parent
		self.children = []
		self.rows = []
		self.imax = None

	def get(self,query=None,cmpt=None,geo=None):
		if query is not None:
			self.query = query
		if cmpt is not None:
			self.cmpt = cmpt
		if geo is not None:
			self.geo = geo

		#Split into lists of 5 or less if needed
		if len(self.cmpt) > 5:
			self._make_children()

		data = self._get_data()
		self._load_json(data)
		
		return self #make chainable

	def normalize(self,r=1.0):
		#normalze all data to max cmpt in query
		if len(self.children) > 0:
			for i,d in enumerate(self.children):
				d.normalize(self.rows[i].max()/100.0 * r) #ratio of this row to max row (100)
		else:
			self.rescale(r)
		return self #make chainable

	def rescale(self,r=1.0):
		if len(self.children) > 0:
			for d in self.children:
				d.rescale(r)
		else:
			for i in self.rows:
				i.rescale(r)
		return self #make chainable


	def leaves(self):
		if len(self.children) > 0:
			for c in self.children:
				for l in c.leaves():
					yield l
		else:
			for d in self.rows:
				yield d

	def csv_rows(self,**kwargs):
		for l in self.leaves():
			for r in l.csv_rows(**kwargs):
				yield r

	def toJSON(self):
		_o = {'cmpt':self.cmpt,'query':self.query,'geo':self.geo,'imax':self.imax}
		_o['rows'] = [r.toJSON() for r in self.rows]
		if self.children:
			_o['children'] = [c.toJSON() for c in self.children]
		else:
			_o['children'] = []
		return _o

	@classmethod
	def fromJSON(cls,data,parent=None):
		_o = cls(data['query'],data['cmpt'],data['geo'])
		if parent:
			_o.parent = parent
		_o.rows = [Query.fromJSON(d) for d in data['rows']]
		if data['children']:
			_o.children = [cls.fromJSON(d,_o) for d in data['children']]
		return _o

	def _get_data(self):
		#Make params
		params = {'hl':'en-US'}
		if len(self.children) > 0:
			self.original_cmpt = self.cmpt
			self.cmpt = [c.get_max() for c in self.children]
		
		compare = ','.join(self.cmpt)
		if self.geo:
			params['cmpt'] = 'geo'
			params['q'] = self.query
			params['geo'] = compare
		else:
			params['cmpt'] = 'q'
			params['q'] = compare
			params['geo'] = self.query

		#GET request
		r = requests.get(utils.TRENDS_URL,params=params,headers=utils.HEADERS)
		print r.url
		data = r.text	

		#parse request by looking for the chartData array
		try:
			start = utils.find_local(data,0,'time-chart-container','chartData','{')
			end = data.index('};',start)
		except ValueError as e:
			try:
				nf = data.index('Not enough search volume to show results.')
				print 'Not enough search volume'
				return 'NO_DATA'
			except ValueError as e:
				# print 'Find Error: ',e
				code.interact(local=locals())
				raise e
		try:
			data = json.loads(utils.sub_date(data[start:end+1]))
		except Exception as e:
			print 'JSON Decode Error Line 75',e
			code.interact(local=locals())
			raise e
		return data

	def _load_json(self,data):
		if data == 'NO_DATA':
			self._load_zeros()
			return
		#Transpose data rows to columns
		indexs = []
		#Get valid columns and labels 
		query = self.query[0] if self.geo else self.cmpt[0]
		for i,v in enumerate(data['columns']):
			if 'id' in v and v['id'].startswith('q'):
				indexs.append(i)
				self.rows.append(Query(query=query,label=v['label']))

		#Get row data
		for r in data['rows']:
			for i,t in zip(indexs,self.rows):
				t.append(r[i] if r[i] is not None else 0)

		#get max and year averages
		max_max = (0,0)
		for i,t in enumerate(self.rows):
			if t.max() > max_max[0]:
				max_max = (t.max(),i)

		self.imax = max_max[1]

	def _load_zeros(self):
		query = self.query[0] if self.geo else self.cmpt[0]
		for c in self.cmpt:
			self.rows.append(QueryZero(query=query,label=c))
		self.imax = 0

	def _make_children(self):
		#Make base 5 tree for children
		isplit = 0
		for s in utils.base_five_split(len(self.cmpt)):
			child = self.__class__(self.query,self.cmpt[isplit:isplit+s],self.geo,self)
			child.get() #recursive call
			self.children.append(child)
			isplit+=s

	def get_max(self):
		return self.cmpt[self.imax] #this should be the max query from this TrendSet

	def depth(self):
		if self.parent:
			return self.parent.depth()+1
		return 0

	def __repr__(self):
		_s = []
		for s,c in itertools.izip_longest(self.rows,self.children):
			_s.append('*'*self.depth()+str(s))
			if c:
				_s.append(str(c))
		return '\n'.join(_s)

class Query(object):
	
	def __init__(self,query,label):
		self.query = query
		self.label = label
		self.data =[]
		self.max_sum = None

	def max(self,recalculate=False):
		if recalculate or self.max_sum is None:
			self.max_sum = max(self.data)
		return self.max_sum

	def append(self,d):
		self.data.append(d)

	def rescale(self,r):
		self.data = [d*r for d in self.data]
		self.max(recalculate=True)


	def csv_rows(self,**kwargs):
		start = kwargs.get('start',2004)
		end = kwargs.get('end',2013)
		if kwargs.get('query',True):
			front = [self.query,self.label]
		else:
			front = [self.label]
		for y in range(start,end+1):
			i = (y - 2004)*12
			#Get Mid
			mid = ['%i'%y] #year
			end = self.data[i:i+12]
			if kwargs.get('zeros',False): #append count of zeros. Default: False
				mid.append(len([d for d in end if d==0]))
			#Get End
			if kwargs.get('round',True):
				end = utils.list_round(end)
			if kwargs.get('avg',False):
				end.append(utils.mean(self.data[i:i+12]))
			yield front+mid+end

	def toJSON(self):
		return self.__dict__

	@classmethod
	def fromJSON(cls,data):
		_o = cls(data['query'],data['label'])
		_o.max_sum = data['max_sum']
		_o.data = data['data']
		return _o

	def __repr__(self):
		_s = '%s (%s - %i) %s'%(self.query,self.label,self.max(),utils.list_round(self.data[:5]))
		return _s

class QueryZero(Query):

	def __init__(self,query,label):
		super(QueryZero,self).__init__(query,label)
		self.max_sum = 0
		self.data = [0 for i in xrange(144)]

def get_all():
	# query = ['diabetes','hiv','tuberculosis','fever','cough']
	query = utils.TERMS.values()
	codes = utils.COUNTRY_CODES.keys()
	return QueryGroup(query,codes,geo=True).get(timeout=20)

if __name__ == '__main__':


	# query = ['tuberculosis']
	# codes = ['NG','FR','US','CA','ZA']
	# query = QueryGroup(query,utils.COUNTRY_CODES.keys(),geo=True).get()
	# query.make_json('tb.json')
	query = QueryGroup.fromJSON(json.load(open('all.json')))
	
	# query = get_all()
	# query.make_csv('terms.csv')
	# query.make_json('terms.json')


	code.interact(local=locals())