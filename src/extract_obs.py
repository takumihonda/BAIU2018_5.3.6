import numpy as np

from datetime import datetime
from datetime import timedelta
import os
import sys

import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap



def read_and_extrect_obs( time=datetime( 2018, 7, 2, 0 ), note="NOVADWND" ):
    otop = "/data_ballantine02/miyoshi-t/honda/SCALE-LETKF/BAIU2018_5.3.6/ncepobs_letkf"

    fn = os.path.join( otop, "obs_" + time.strftime('%Y%m%d%H%M%S.dat') )
    print(fn)

    infile = open( fn )
    data = np.fromfile( infile, dtype=np.dtype('>f4') )
    infile.close

    nobs = int( data.shape[0]/(8+2) ) # wk(8) + header + footer in one record
    #obs_all = np.zeros((8,nobs))
    #obs_all = data.reshape(10,nobs)
    obs_all = data.reshape(nobs,10)

    print( obs_all.shape )

    VADWND = 6 # Fortran array ID   

    ids = obs_all[:,1]
    types = obs_all[:,7]
    lons = obs_all[:,2]
    lats = obs_all[:,3]

    # VADWND
    lat_min = 25
    lat_max = 27
    lon_min = 125
    lon_max = 130

    # SFCSHP
    lat_min = 19
    lat_max = 21
    lon_min = 125
    lon_max = 131

    # Daito island
    lat_min = 25
    lat_max = 27
    lon_min = 130
    lon_max = 132

    id_ps = 14593

    #idxs = ( types == VADWND ) * ( lats > lat_min ) * ( lats < lat_max ) * ( lons > lon_min ) * ( lons < lon_max )
    #idxs = ( lats > lat_min ) * ( lats < lat_max ) * ( lons > lon_min ) * ( lons < lon_max )
    idxs = ( ids == id_ps ) * ( lats > lat_min ) * ( lats < lat_max ) * ( lons > lon_min ) * ( lons < lon_max )
    obs_new = obs_all[ ~idxs,: ] 
    obs_rej = obs_all[ idxs,: ] 
    print( "Resulting obs:", obs_new.shape, "Reject:", obs_rej.shape )

    print_obs( obs_rej )
#    sys.exit()

    data_new = obs_new.reshape( len( obs_new[:,0] )*10 )
    


    # write new file
    fn = os.path.join( otop, "obs_{0:}_{1:}.dat".format( time.strftime('%Y%m%d%H%M%S'), note ) )
    print( fn )
    data_new.tofile( fn,  )
    sys.exit()

def print_obs( obs_l ):
    for l in range( len( obs_l[:,0] ) ):
        print( "typ: {0:}, id:{1:}, lon: {2:.2f}, lat:{3:.2f}, lev:{4:.2f}".format( int( obs_l[l,7] ), int( obs_l[l,1] ), obs_l[l,2], obs_l[l,3], obs_l[l,4] ) )

#    infile = open( fn )
#    data = np.fromfile( infile, dtype=np.dtype('>f4') )
#    infile.close
#
#    nobs = int( data.shape[0]/(8+2) ) # wk(8) + header + footer in one record
#    obs_all = data.reshape(nobs,10)
#    print( nobs )
#    print( obs_all[0,:] )
#
#    sys.exit()
#
#    c = 0
#    typ = VADWND
#    for l in range( len( obs_new[:,0] ) ):
##        if obs_all[l,7] == typ:
#        print( "lon: {0:.2f}, lat:{1:.2f}, lev:{2:.2f}".format( obs_new[l,2], obs_new[l,3], obs_all[l,4] ) )
#        c += 1
#
#    print( c )
#    sys.exit()

def main( time, note="" ):

    read_and_extrect_obs( time=time, note=note )
    sys.exit()


####################




stime = datetime( 2018, 7, 2, 18 )
#etime = datetime( 2018, 7, 3, 0 )
etime = stime

note = "NOVADWND"
note = "NOADPSFC"

time = stime
while( time <= etime):
  main( time, note=note )
  time += timedelta(hours=6)
