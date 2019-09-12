#!/usr/bin/env python3
#%%
import re
import numpy as np
#%%
__all__ = ['tec2py']
def tec2py(datfile):
#%%
   # datfile = 'test.tec'
    IVARlist = False
    lines = []

    # read data once first
    flines = []
    IVARlist = False
    with open(datfile, 'r') as fid:
        for l in fid:
            l = l.strip()
            if len(l) > 0:
                if l[0] != '#':
                    if 'VARIABLES' in l:
                        VARlist = re.findall('[''"](.*?)[''"]', l)
                        NVAR = len(VARlist)
                        IVARlist = True
                    elif IVARlist:
                        # only keep content below VARIABLES=****
                        flines.append(l)

    flines = iter(flines)
#%%
    if not IVARlist:
        raise Exception("No variables found")
    else:
        nzone = 0
        while True:
            try:
#%%
                l = next(flines)
                if 'ZONE' in l:
                    nzone = nzone + 1
                    # ===========load zone information===================
                    inum = re.findall('I\s*=\s*(\d+)', l)
                    inum = int(inum[0])
                    jnum = re.findall('J\s*=\s*(\d+)', l)
                    if jnum:
                        jnum = int(jnum[0])
                    else:
                        jnum = 1
                    ndata = inum*jnum
                    zonename = re.findall('T\s*=\s*["''](.*)[''"]', l)
                    if not zonename:
                        zonename = re.findall('T\s*=\s*(.*)', l)
                    if zonename:
                        zonename = zonename[0]
                    else:
                        zonename = 'data %d' % (nzone,)
#%%
                    # ============== load passivelist ==================
                    mcolum = NVAR
                    passive_list = []
                    i_passive = False
                    if "PASSIVEVARLIST" in l:
                        i_passive = True
                        passive_str = re.findall('PASSIVEVARLIST=\[(.*)\]', l)[0]
                        passive_list = [int(i)-1 for i in passive_str.split(',')]
                        mcolum -= len(passive_list)
#%%
                    #  ============== load data ===========================
                    zone_data = []
                    nelement = 0
                    for nelement in range(ndata):
                        l = next(flines).strip()
                        l2append = [float(i) for i in l.split()]
                        zone_data += [l2append]
#%%
                    zone_data = np.array(zone_data).T
                    if i_passive:
                        zd = np.zeros((ndata, NVAR))
                        j = 0
                        for i in range(NVAR):
                            if i not in passive_list:
                                zd[i] = zone_data[j]
                                j += 1
                        zone_data = zd

                        # add zero if there is passive_list
                        if jnum == 1:
                            zone_data2 = np.zeros((ndata, NVAR))
                            for i, j in enumerate(npassive_list):
                                zone_data2[:, j] = zone_data[:, i]
                        else:
                            zone_data2 = np.zeros((mcolum, jnum, inum))
                            for i, j in enumerate(npassive_list):
                                zone_data2[j] = zone_data[i]

                        zone_data = zone_data2

                    lines.append({'zonename': zonename, 'data': [i for i in zone_data]})
            except StopIteration:
                break
    return {'varnames': VARlist, 'lines': lines}
