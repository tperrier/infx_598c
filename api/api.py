import requests,json,re,csv
import code

import utils
from trendset import TrendSet

def trends_by_query(query,codes):
	data = [['query','country','max']+utils.fetch_years()+utils.fetch_dates()]
	query = utils.make_list(query)
	codes = utils.make_list(codes)
	
	for q in query:
		for d in TrendSet(query=q,cmpt=codes,geo=True).get():
			data.append([q]+d)
	return data

def trends_by_country(query,codes):
	data = [['country','query','max']+utils.fetch_years()+utils.fetch_dates()]
	query = utils.make_list(query)
	codes = utils.make_list(codes)

	for c in codes:
		for d in TrendSet(query=query,codes=c,geo=False).get():
			data.append([c]+d)

	return data

if __name__ == '__main__':

	cf = csv.writer(open('tmp.csv','w'))

	# data = trends_by_country(['seattle','paris','lagos'],['US','FR','NG'])
	data = trends_by_query(['seattle','paris','lagos','cape town'],['NG','FR','US','CA','ZA','EG','DE','KE','IN','TH'])
	# data = trends_by_query(['hiv'],['NG','FR','US','CA'])
	# code.interact(local=locals())
	cf.writerows(data)



