#!/usr/bin/env python3
#%%
import py2tec
import numpy as np

#%%
tdata = {'varnames': ['x', 'y'],
         'lines': [
             {'zonename': 'line1',
              'data': [np.array([1,2,3],np.int32), np.array([-1,-2,-3], np.float64)]}
         ]}
py2tec.py2tec(tdata,'test.tec')

#%%
tdata =py2tec.tec2py('test.tec')

#%%
