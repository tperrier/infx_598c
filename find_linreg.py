import numpy as np
from sklearn import datasets, linear_model
import collections,code



filename = 'data/hiv.csv'
ground_index = -2

data = np.genfromtxt(filename,delimiter=',',skip_header=1)
ground = np.genfromtxt('data/ground.csv',delimiter=',',skip_header=1)

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