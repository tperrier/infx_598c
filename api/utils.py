import re,math,collections
from private import cookie

"""
Helper functions and data to drive the API
"""

HEADERS = {
	'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/39.0.2171.65 Chrome/39.0.2171.65 Safari/537.36',
	'Cookie':cookie,
}	

FETCH_URL = 'http://www.google.com/trends/fetchComponent'
TRENDS_URL = 'http://www.google.com/trends/trendsReport'

REGEX_DATE = re.compile('new Date\((\d{4}),[ ]?(\d{1,2})(,[ ]?\d{1,2}){1,3}\)')
def sub_date(s):
	#Search for Javascript Dates "new Date(yyyy,mm,dd,hh,mm,ss)" and replace with yyyy-mm
	return REGEX_DATE.sub('"\g<1>-\g<2>"',s)

def make_list(l):
	if isinstance(l,str):
		return [l]
	return l
def base_five_split(n):
	log = int(math.floor(math.log(n,5)))
	power = 5**log
	if power==n: #perfect power of 5
		power = 5**(log-1)
	times = int(math.floor(n/power))
	remainder = n-times*power
	s = [power for i in range(times)]
	if remainder > 0: #perfect power of 5 no remainder
		s += [remainder]
	return s

def find_local(s,p=0,*args):
	#similar to css selectors but for raw text
	p = int(p)
	if len(args) == 0:
		return p
	p = s.index(args[0],p)
	return find_local(s,p,*args[1:])

def fetch_years():
	return ['20%02i'%y for y in range(4,16)]

def fetch_dates():
	dates = []
	for y in range(4,16):
		for m in range(1,13):
			dates.append('%02i-%02i'%(y,m))
	return dates + ['16-1','16-2']

def list_round(l):
	return [round(i,2) if isinstance(i,(int,float,long)) else i for i in l]

def mean(data):
	n = len(data)
	if n<1:
		raise ValueError('mean requires at least one data point')
	return sum(data)/float(n)

def sd(data):
	m = mean(data)
	n = len(data)
	if n<2:
		raise ValueError('variance requires at least two data points')
	ss = sum((i-m)**2 for i in data)
	return (ss/n)**0.5


COUNTRY_CODES = collections.OrderedDict([
('AU','Australia'),('BD','Bangladesh'),('BW','Botswana'),
('CM','Cameroon '),('CA','Canada '),('DK','Denmark'),
('EG','Egypt'),('EE','Estonia'),('FJ','Fiji'),
('DE','Germany'),('GH','Ghana'),('GR','Greece'),
('IN','India'),('IQ','Iraq'),('IE','Ireland'),
('JM','Jamaica'),('JO','Jordan'),('KE','Kenya'),
('LS','Lesotho'),('LR','Liberia'),('MY','Malaysia'),
('MW','Malawi'),('NA','Namibia'),('NL','Netherlands'),
('NZ','New Zealand'),('NG','Nigeria'),('PK','Pakistan'),
('PH','Philippines'),('PR','Puerto Rico'),('RW','Rwanda'),
('SL','Sierra Leone'),('SG','Singapore'),('ZA','South Africa'),
('SR','Suriname'),('SZ','Swaziland'),('TZ','Tanzania'),
('TH','Thailand'),('UG','Uganda'),('GB','United Kingdom'),
('US','United States'),('VU','Vanuatu'),('ZM','Zambia'),
('ZW','Zimbabwe')
])

# /m/01b_21, /m/0c58k, /m/07jwr, /m/0d19y2, /m/0cjf0
TERMS = {
	'diabetes':'/m/0c58k',
	'tb':'/m/07jwr',
	'hiv':'/m/0d19y2',
	'fever':'/m/0cjf0',
	'cough':'/m/01b_21',
}