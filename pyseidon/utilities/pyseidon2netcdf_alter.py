#!/usr/bin/python2.7
# encoding: utf-8

#Libs import
from __future__ import division
import numpy as np
import sys
#TR comment: 2 alternatives
import netCDF4 as nc
#from scipy.io import netcdf

def pyseidon_to_netcdf(fvcom, filename, debug):
    """
    Saves fvcom object in a pickle file

    inputs:
      - fvcom = fvcom pyseidon object
      - filename = file name, string
    """
    #Define bounding box
    if debug: print "Computing bounding box..."
    if fvcom.Grid._ax == []:
        lon = fvcom.Grid.lon[:]
        lat = fvcom.Grid.lat[:]
        fvcom.Grid._ax = [lon.min(), lon.max(),
                         lat.min(), lat.max()]
    filename = filename + ".nc"
    f = nc.Dataset(filename, 'w', format='NETCDF4_CLASSIC')
    #history attribut
    f.history = fvcom.History[:]

    #create dimensions
    if not fvcom.Variables._3D:
        ##2D dimensions
        dims = {'three':3, 'four':4,
                'nele': fvcom.Grid.nele, 'node': fvcom.Grid.nnode,
                'siglay': 2, 'siglev': 3,
                'time': fvcom.Variables.julianTime.shape[0]}
    else:
        ##3D dimensions
        dims = {'three':3, 'four':4,
                'nele': fvcom.Grid.nele, 'node': fvcom.Grid.nnode,
                'siglay': fvcom.Grid.nlevel, 'siglev': fvcom.Grid.nlevel+1,
                'vertshear':fvcom.Grid.nlevel-1,
                'time': fvcom.Variables.julianTime.shape[0]}
    for key in dims.keys():
        f.createDimension(key, dims[key])

    #list of potential 2D var
    varname = ['el', 'ua', 'va', 'julianTime', 'matlabTime',
               'depth_av_flow_dir', 'hori_velo_norm',
               'depth_av_vorticity', 'depth_av_power_density',
               'depth_av_power_assessment', 'tauc']
    #list of potential 2D grid var
    gridname = ['a1u', 'a2u','trinodes', 'triele',
                'xc', 'x', 'yc', 'y', 
                'lonc', 'lon', 'latc', 'lat',
                'aw0', 'awy', 'awx',
                'h','hc', 'depth2D',
                'siglay','siglev', 'depth']
    #list of potential 3D var * grid var
    if fvcom.Variables._3D:
        varname = varname + ['u', 'v', 'w', 'flow_dir', 'velo_norm', 'verti_shear',
                             'vorticity', 'power_density']

    #load in netcdf file
    if debug: print "Loading variables' matrices in nc file..."
    for var in varname:
        if debug: print "...loading "+var+"..."
        if var in ['ua', 'va','depth_av_flow_dir','depth_av_vorticity',
                   'depth_av_power_density','depth_av_power_assessment',
                   'hori_velo_norm', 'tauc']:
            try:
                if hasattr(fvcom.Variables, var):
                    tmp_var = f.createVariable(var, 'float', ('time','nele'))
                    tmp_var[:] = getattr(fvcom.Variables, var)[:]
            except (AttributeError, IndexError) as e:
                pass
        if var in ['julianTime', 'matlabTime']:
            try:
                if hasattr(fvcom.Variables, var):
                    tmp_var = f.createVariable(var, 'float', ('time',))
                    tmp_var[:] = getattr(fvcom.Variables, var)[:]
            except AttributeError:
                pass
        if var == 'el':
            try:
                if hasattr(fvcom.Variables, var):
                    tmp_var = f.createVariable('zeta', 'float', ('time','node'))
                    tmp_var[:] = getattr(fvcom.Variables, var)[:]
            except (AttributeError, IndexError) as e:
                pass
        if fvcom.Variables._3D:
            if var in ['u', 'v', 'flow_dir', 'velo_norm',
                       'vorticity', 'power_density']:
                try:
                    if hasattr(fvcom.Variables, var):
                        tmp_var = f.createVariable(var,'float',('time','siglay','nele'))
                        tmp_var[:] = getattr(fvcom.Variables, var)[:]
                except (AttributeError, IndexError) as e:
                    pass
            if var in ['verti_shear']:
                try:
                    if hasattr(fvcom.Variables, var):
                        tmp_var = f.createVariable(var,'float',
                                                      ('time','vertshear','nele'))
                        tmp_var[:] = getattr(fvcom.Variables, var)[:]
                except (AttributeError, IndexError) as e:
                    pass
            if var in ['w']:
                try:
                    if hasattr(fvcom.Variables, var):
                        tmp_var = f.createVariable('ww','float',
                                                      ('time','siglay','nele'))
                        tmp_var[:] = getattr(fvcom.Variables, var)[:]
                except (AttributeError, IndexError) as e:
                    pass

    if debug: print "Loading grid' matrices in nc file..."
    for grd in gridname:
        if debug: print "...loading "+grd+"..."
        if grd in ['xc', 'yc', 'lonc', 'latc', 'hc']:
            try:
                if hasattr(fvcom.Grid, grd):
                    tmp_var = f.createVariable(grd, 'float', ('nele',))
                    tmp_var[:] = getattr(fvcom.Grid, grd)[:]
            except (AttributeError, IndexError) as e:
                pass
        if grd == 'depth2D':
            try:
                if hasattr(fvcom.Grid, grd):
                    tmp_var = f.createVariable(grd, 'float', ('time','nele'))
                    tmp_var[:] = getattr(fvcom.Grid, grd)[:]
            except (AttributeError, IndexError) as e:
                pass
        if grd in ['x', 'y', 'lon', 'lat', 'h']:
            try:
                if hasattr(fvcom.Grid, grd):
                    tmp_var = f.createVariable(grd, 'float', ('node',)) 
                    tmp_var[:] = getattr(fvcom.Grid, grd)[:]
            except (AttributeError, IndexError) as e:
                pass
        if grd in ['triele','trinodes']:
            try:
                if hasattr(fvcom.Grid, grd):
                    tmp_var = f.createVariable(grd, 'i', ('nele','three'))
                    tmp_var[:] = getattr(fvcom.Grid, grd)[:]
            except (AttributeError, IndexError) as e:
                pass
        if grd in ['a1u', 'a2u']:
            try:
                if hasattr(fvcom.Grid, grd):
                    tmp_var = f.createVariable(grd, 'float', ('four','nele'))
                    tmp_var[:] = getattr(fvcom.Grid, grd)[:]
            except (AttributeError, IndexError) as e:
                pass
        if grd in ['aw0', 'awy', 'awx']:
            try:
                if hasattr(fvcom.Grid, grd):
                    tmp_var = f.createVariable(grd, 'float', ('three','nele'))
                    tmp_var[:] = getattr(fvcom.Grid, grd)[:]
            except (AttributeError, IndexError) as e:
                pass
        if grd == 'siglay':
            try:
                if hasattr(fvcom.Grid, grd):
                    tmp_var = f.createVariable(grd,'float', ('siglay','node'))
                    tmp_var[:] = getattr(fvcom.Grid, grd)[:]
            except (AttributeError, IndexError) as e:
                pass
        if grd == 'siglev':
            try:
                if hasattr(fvcom.Grid, grd):
                    tmp_var = f.createVariable(grd,'float', ('siglev','node'))
                    tmp_var[:] = getattr(fvcom.Grid, grd)[:]
            except (AttributeError, IndexError) as e:
                pass
        if grd == 'depth':
            try:
                if hasattr(fvcom.Grid, grd):
                    tmp_var = f.createVariable(grd,'float', ('time','siglay','nele'))
                    tmp_var[:] = getattr(fvcom.Grid, grd)[:]
            except (AttributeError, IndexError) as e:
                pass
    f.close()
    if debug: print "...done"    






