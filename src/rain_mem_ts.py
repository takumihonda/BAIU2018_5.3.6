import numpy as np

from netCDF4 import Dataset
from datetime import datetime
from datetime import timedelta
import os
import sys

import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
 
from tools_BAIU import get_lonlat, prep_proj_multi, get_arain, get_mslp, get_grads_JMA

from scipy.interpolate import griddata

quick = True   
#quick = False

JMA = False

def get_ts_bs( fcst2d, obs2d, thrs=10.0 ):

    fo = np.where( (fcst2d >= thrs) & (obs2d >= thrs), 1, 0 )
    fx = np.where( (fcst2d >= thrs) & (obs2d <  thrs), 1, 0 )
    xo = np.where( (fcst2d <  thrs) & (obs2d >= thrs), 1, 0 )

    return( np.sum(fo) / ( np.sum(fo)+np.sum(fx)+np.sum(xo) ),
            ( np.sum(fo) + np.sum(fx) ) / ( np.sum(fo) + np.sum(xo) ) )

def main():

    thrs = 100.0
    #thrs = 10.0
    thrs = 50.0

    TOP = "/data_ballantine02/miyoshi-t/honda/SCALE-LETKF/BAIU2018_5.3.6"
    
    stime = datetime( 2018, 6, 28, 0, 0, 0 )
    stime = datetime( 2018, 7, 2, 0, 0, 0 )

    vtime = datetime( 2018, 7, 7, 0, 0, 0 )
    vtime = datetime( 2018, 7, 6, 0, 0, 0 )
    
    stime = datetime( 2018, 6, 29, 0, 0, 0 )
    stime = datetime( 2018, 6, 26, 0, 0, 0 )
    stime = datetime( 2018, 6, 27, 0, 0, 0 )
    stime = datetime( 2018, 6, 29, 0, 0, 0 )
    stime = datetime( 2018, 6, 30, 0, 0, 0 )
    stime = datetime( 2018, 7, 1, 0, 0, 0 )
    stime = datetime( 2018, 7, 2, 0, 0, 0 )
    stime = datetime( 2018, 7, 3, 0, 0, 0 )
    stime = datetime( 2018, 6, 28, 0, 0, 0 )

    adt_h = 24
    adt = timedelta( hours=adt_h )
    

    INFO = {"TOP": TOP, }

    lon2d, lat2d = get_lonlat( INFO, stime=stime )

    levs = np.arange( 20, 300, 20)
    clevs = np.arange( 800, 1200, 4 )
    cmap = plt.cm.get_cmap("jet")


    jma2d, JMAr_lon, JMAr_lat = get_grads_JMA( vtime - adt , adt_h, ACUM=True )
    lon2d_jma, lat2d_jma = np.meshgrid( JMAr_lon, JMAr_lat )

    slon = 130.0
    elon = 137.5
    slat = 33.0
    elat = 36.0

    lon2d_jma_ = lon2d_jma[ ( lon2d_jma >= slon )  & ( lon2d_jma <= elon ) & \
                            ( lat2d_jma >= slat )  & ( lat2d_jma <= elat ) ]

    lat2d_jma_ = lat2d_jma[ ( lon2d_jma >= slon )  & ( lon2d_jma <= elon ) & \
                            ( lat2d_jma >= slat )  & ( lat2d_jma <= elat ) ]

    jma2d_ = jma2d[ ( lon2d_jma >= slon )  & ( lon2d_jma <= elon ) & \
                    ( lat2d_jma >= slat )  & ( lat2d_jma <= elat ) ]

    lon2d_ = lon2d[ ( lon2d >= slon )  & ( lon2d <= elon ) & \
                    ( lat2d >= slat )  & ( lat2d <= elat ) ]

    lat2d_ = lat2d[ ( lon2d >= slon )  & ( lon2d <= elon ) & \
                    ( lat2d >= slat )  & ( lat2d <= elat ) ]

    ts_l = np.zeros(50)
    bs_l = np.zeros(50)

    for m in range( 0, 50 ):
        mem = str(m).zfill(4)    
        if m == 0:
           mem = "mean"
        
        rain = get_arain( INFO, stime=stime, vtime=vtime, adt=adt, m=m+1 )
        
        rain_ = rain[ ( lon2d >= slon )  & ( lon2d <= elon ) & \
                      ( lat2d >= slat )  & ( lat2d <= elat ) ]

        if m == 0:
           irain_jma = griddata( (lon2d_jma_.ravel(), lat2d_jma_.ravel() ),
                                  jma2d_.ravel(),
                                  ( lon2d_.ravel(), lat2d_.ravel() ),
                                  method='cubic',
                                  )
#           print(irain_jma.shape, rain_.shape )

#        irain = griddata( ( lon2d.ravel(), lat2d.ravel() ), rain.ravel(), 
#                          ( lon2d_jma_, lat2d_jma_), 
#                           method='cubic',
#                        )
#         
#        print( np.max( rain), rain[ rain > thrs].shape, irain_jma[irain_jma > thrs].shape )
        ts, bs = get_ts_bs( rain_.ravel(), irain_jma, thrs=thrs )
#        print( irain.shape, jma2d_.shape )
#        print("DEBUG", np.max(irain), np.min(irain), np.max(jma2d_), np.min(jma2d_))       
#        print( ts, bs)
#        print( irain[ irain> thrs].shape, jma2d_[ jma2d_ > thrs].shape )

        print( 'Mem: {0:}, TS:{1:}, BS:{2:}, OBS:{3:}, FCST:{4:}'.format( mem, ts, bs, len(irain_jma[irain_jma > thrs]), len( rain_[rain_ > thrs]) ) )

        ts_l[m] = ts
        bs_l[m] = bs

        continue

    print( "" )
    print( 'Init:{0:}, valid:{1:} '.format( stime.strftime('%m/%d %HUTC'),
                       vtime.strftime('%m/%d %HUTC') ) )
    print( np.max(ts_l) )    
    print( np.sort(ts_l)[-1::-1] )    
    print( np.argsort(ts_l)[-1::-1] )    


    opath = "dat/ts_s" + stime.strftime('%H%m%d')
    os.makedirs(opath, exist_ok=True)

    of = 'v{0:}_thrs{1:03}mm_lon{2:04}_{3:04}_lat{4:04}_{5:04}.npz'.format( vtime.strftime('%H%m%d'), thrs , slon, elon, slat, elat )
    print( of )

    np.savez( os.path.join( opath, of), ts=np.sort(ts_l)[-1::-1], mem=np.argsort(ts_l)[-1::-1] )

main()
