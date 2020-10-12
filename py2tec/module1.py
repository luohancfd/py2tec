#!/usr/bin/env python3
import numpy as np

__all__ = ['py2tec']

FEM_TYPE = [['FELINESEG'],
            ['FETRIANGLE', 'FEQUADRILATERAL', 'FEPOLYGON'],
            ['FETETRAHEDRON', 'FEBRICK', 'FEPOLYHEDRAL']]

FEM_FACE_TYPE = ['FEPOLYGON', 'FEPOLYHEDRAL']

def nparray2string(val):
    '''
    convert a numpy array to string
    '''
    m = val.shape
    if len(m) > 3:
        raise ValueError('Output limits to 3D matrix')
    if len(m) == 1:
        return ' '.join(['{:e}'.format(x) for x in val]) + '\n'
    if len(m) == 2:
        s = []
        for row in val:
            s.append(' '.join(['{:e}'.format(x) for x in row]))
        return '\n'.join(s) + '\n'
    if len(m) == 4:
        sp = []
        for p in val:
            s = []
            for row in val:
                s.append(' '.join(['{:e}'.format(x) for x in row]))
            sp.append('\n'.join(s))
        return '\n'.join(sp) + '\n'


def formatnp(data):
    '''
    Generate appropriate format string for numpy array

    Argument:
        - data: a list of numpy array
    '''

    dataForm = []
    for i, idata in enumerate(data):
        if np.issubsctype(idata, np.integer):
            dataForm.append('{:d}')
        else:
            dataForm.append('{:e}')

    return ' '.join(dataForm)


def writeZoneHeader(fid, header, size, izone=0):
    '''
    Write zone header
    Arguments:
        - fid: file stream)
        - header: zone header information
        - size: a list for size of the zone
    '''
    # zonename
    if 'zonename' in header:
        zonename = header['zonename']
    else:
        zonename = 'ZONE {:d}'.format(izone)
    fid.write('ZONE T="{:s}"'.format(zonename))

    # zonetype and size
    if 'zonetype' in header.keys():
        zonetype = header['zonetype']
    else:
        zonetype = 'ORDERED'
    fid.write(' ZONETYPE={:s}'.format(zonetype))
    if zonetype == 'ORDERED':
        if len(size) == 3:
            fid.write(' I={2:d} J={1:d} K={0:d}'.format(*size))
        elif len(size) == 2:
            fid.write(' I={1:d} J={0:d}'.format(*size))
        elif len(size) == 1:
            fid.write(' I={:d}'.format(*size))
    else:
        # FEM zone
        fid.write(' NODES={:d} ELEMENTS={:d}'.format(size[0], size[1]))
        if len(size) == 3:
            fid.write(' FACES={:d}'.format(size[3]))

    # passivevar
    if 'passivevarlist' in header:
        fid.write(' PASSIVEVARLIST = [{:s}]'.format(','.join([ii+1 for ii in header['passivevarlist']])))

    # reformat boolean type
    boolean_param = {
        'datapacking': {0: 'POINT', 1: 'BLOCK'},
    }
    for k in boolean_param.keys():
        if k in header.keys() and header[k] in boolean_param[k].keys():
            header[k] = boolean_param[k][header[k]]

    other_param = {
        'datapacking': ['BLOCK', '{:s}'],
        'solutiontime': [None, '{:e}'],
        'strandid': [None, '{:d}'],
        'varloc': [None, '{:s}']
    }

    for key, val in other_param.items():
        formatStr = ' {:s}'.format(key.upper()) + '=' + val[1]
        if key in header.keys():
            fid.write(formatStr.format(header[key]))
        elif val[0]:
            fid.write(formatStr.format(val[0]))

    fid.write('\n')
    return True


def py2tec(tdata, fname):
    '''
    Argument list:

    - tdata: A dictionary of data, it can have the following keys:
        + title (optional): title of the file
        + varnames: a list of variable names
        + lines (optional): a list of data for line plot
            + lines.data: the data for the line data, it should be a list of numpy arraies, which should have the same length.
            + lines.zonename(optional): name of the zone
            + lines.passivevarlist (optional): exclude some variables from the data
            # TODO
            + lines.datapacking
        + surfaces (optional): TODO
    '''
    if not isinstance(tdata, dict):
        raise TypeError('tdata should be a dict')
    with open(fname, 'w', encoding='utf-8') as fid:
        # title
        if 'title' in tdata:
            fid.write('TITLE = "{:s}"\n'.format(title))

        # variables
        fid.write('VARIABLES = {:s}\n'.format(','.join(['"{:s}"'.format(i) for i in tdata['varnames']])))

        nzone = {'lines': 0, 'surfaces': 0}
        for key in nzone.keys():
            if key in tdata:
                nzone[key] = len(tdata[key])

        izone = 0
        # ========================== write lines ======================================
        if nzone['lines'] > 0:
            for i, line in enumerate(tdata['lines']):
                izone += 1

                # get number of rows
                nx = len(line['data'][0])

                # modify header
                line['datapacking'] = 'POINT'
                line['zonetype'] = 'ORDERED'
                writeZoneHeader(fid, line, [nx], izone)

                # write data
                dataFormat = formatnp(line['data']) + '\n'
                # nvar = len(tdata['varnames']) - len(passivevarlist)
                for ix in range(nx):
                    d = [j[ix] for j in line['data']]
                    fid.write(dataFormat.format(*d))

                fid.write('\n')
        # =========================== Write 2D surface ================================
        if nzone['surfaces'] > 0:
            for isurf, surf in enumerate(tdata['surfaces']):
                izone += 1
                if 'datapacking' not in surf.keys():
                    surf['datapacking'] = 'BLOCK'

                # 0 for nodal, 1 for center
                if 'varloc' in surf.keys():
                    ivarloc = surf['varloc']
                    if isinstance(ivarloc, list):
                        surf['datapacking'] = 'BLOCK'
                        icen = []
                        inodal = []
                        for i, ii in enumerate(ivarloc):
                            if ii == 1:
                                icen.append(i+1)
                            else:
                                inodal.append(i+1)
                else:
                    ivarloc = 0

                x = surf['x']
                # x should be store in the following way
                # x -----> i
                # |
                # |
                # ^ j
                y = surf['y']
                if 'z' in surf.keys():
                    z = surf['z']
                if 'v' in surf.keys():
                    v = surf['v']

                m, n = x.shape
                if isinstance(ivarloc, list):
                    surf['varloc'] = 'VARLOCATION=({:s}=CELLCENTERED, {:s}=NODAL)\n'.format(str(icen), str(inodal))
                elif ivarloc == 1:
                    surf['varloc'] = 'VARLOCATION=([{:d}-{:d}]=CELLCENTERED)\n'.format(1, len(tdata['varnames']))

                writeZoneHeader(fid, surf, [m, n], izone)

                if surf['datapacking'] == 'BLOCK':
                    fid.write(nparray2string(x))
                    fid.write(nparray2string(y))
                    if 'z' in surf.keys():
                        fid.write(nparray2string(z))
                    if 'v' in surf.keys():
                        for vv in v:
                            fid.write(nparray2string(vv))
                else:
                    data = x
                    data = np.vstack((data, y))
                    if 'z' in surf.keys():
                        data = np.vstack((data, z))
                    if 'v' in line.keys():
                        for vv in v:
                            data = np.vstack((data, vv))
                    fid.write(nparray2string(data.T))
                fid.write('\n\n')
