import pylab as pl
import numpy as np
from sklearn import datasets, linear_model

filename = 'tb_mid.csv'

data = np.genfromtxt(filename,delimiter=',')

dx = data[1:,3:-2]
dy = data[1:,-1]

lin = linear_model.LinearRegression()

lin.fit(dx,dy)

print lin.score(dx,dy)