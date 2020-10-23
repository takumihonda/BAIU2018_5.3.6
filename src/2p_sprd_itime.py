import numpy as np

from netCDF4 import Dataset
from datetime import datetime
from datetime import timedelta
import os
import sys

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
 
from tools_BAIU import get_lonlat, get_var, prep_proj_multi, get_grads_JMA, def_cmap, draw_rec


quick = True   
quick = False



def main( slon=130.0, elon=137.5,
          slat=33.0, elat=36.0,
          stime_l=[], dth=24,
          vtime=datetime( 2018, 7, 5, 0 ),
          vtime_ref=datetime( 2018, 7, 5, 0 ),
          etime=datetime( 2018, 7, 5, 0 ), nvar="PW", hpa=500 ):

    bbox = {'facecolor':'w', 'alpha':0.95, 'pad':2}

    fig, ( (ax1, ax2) ) = plt.subplots( 1, 2, figsize=( 10, 4.5 ) )
    fig.subplots_adjust( left=0.08, bottom=0.12, right=0.97, top=0.92,
                         wspace=0.15, hspace=0.2)


    xmin = datetime( 2018, 6, 27, 0)
    xmax = datetime( 2018, 7, 5, 0) 

    fac = 1.0

    TOP = "/data_ballantine02/miyoshi-t/honda/SCALE-LETKF/BAIU2018_5.3.6"
    
    INFO = {"TOP": TOP, }

    lon2d, lat2d = get_lonlat( INFO, stime=datetime( 2018, 7, 1, 0 ) )

    cmap_, levs_, unit_, extend_, nvar_, fac_ = def_cmap( nvar=nvar, hpa=hpa )

    std_l = []
    mean_l = []

    for it, stime in enumerate( stime_l ):
        evar, vtimes = read_tseries( slon=slon, elon=elon, slat=slat, elat=elat,
                                     stime=stime, nvar=nvar, hpa=hpa, etime=etime, dth=dth )

        std = np.std( evar, axis=1, ddof=1 ) *fac
        mean = np.mean( evar, axis=1, ) * fac

        for it2 in range( len(vtimes) ):
            dt = ( vtimes[it2] - vtime_ref ).total_seconds()
            if dt == 0.0:
               break
            
        std_l.append( std[it2] )
        mean_l.append( mean[it2] )

        print( '{0:}, Mean:{1:.2f}, {2:.2f}'.format( stime.strftime('%HUTC %m/%d'), np.max(mean), np.max(std) ) )


    std_l = np.array( std_l )
    mean_l = np.array( mean_l )
    stime_l = np.array( stime_l )

    lw = 2.0
    var_l = [ mean_l, std_l ]
 
    ylab_l = [ "Forecast mean (mm)", "Forecast spread (mm)" ]

    ptit_l = [ "Ensemble mean", "Ensemble spread" ]

    ymin_l = [ 10.0, 10.0 ]
    ymax_l = [ 150.0, 45.0 ]
    ax_l = [ ax1, ax2 ]
    for i, ax in enumerate( ax_l ):

        ax.plot( stime_l, var_l[i], linewidth=lw, color='k' )
    
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=24) )
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))  
    
        ax.set_xlim( xmin, xmax )
    
        xlab = "Initial time (UTC)"
        ax.set_xlabel( xlab, fontsize=12 )
    
        ax.set_ylabel( ylab_l[i], fontsize=12 )
    
        ax.set_ylim( ymin_l[i], ymax_l[i] )
    
        ax.vlines( x=stime_l, ymin=ymin_l[i], ymax=ymax_l[i], linestyle='dashed',
                   lw=0.5, color='gray' )

        ax.text( 0.5, 0.99, ptit_l[i],
                  fontsize=12, transform=ax.transAxes,
                  ha='center', va='top', )

    opath = "png/sprd_ts"
    ofig = "2p_sprd_{0:}_lon{1:}_{2:}_lat{3:}_{4:}_hpa{5:}_adt{6:0=3}".format( nvar_, slon, elon, slat, elat, hpa, dth ) 

    if nvar_ == "RAIN":
       tit = "Forecast ensemble mean and spread of {0:}-h accumulated precipitation amount".format( dth ) #"{0:} forecast spread at {1:}".format( nvar_, vtime_ref.strftime('%HUTC %m/%d') ) 

       note = "Period: {0:}\n-{1:}".format( ( vtime_ref - timedelta(hours=dth) ).strftime('%HUTC %m/%d'),
                 vtime_ref.strftime('%HUTC %m/%d'), )
       ax.text( 0.99, 0.8, note,
                 fontsize=10, transform=ax.transAxes,
                 ha='right', va='top',
                 )


    else:
       tit = "{0:} forecast spread at {1:}".format( nvar_, vtime_ref.strftime('%HUTC %m/%d') ) 
    fig.suptitle( tit, fontsize=13 )

    if not quick:

       os.makedirs(opath, exist_ok=True)
     
       ofig = os.path.join(opath, ofig + ".png")
       plt.savefig(ofig,bbox_inches="tight", pad_inches = 0.1)
       print(ofig)
       plt.clf()
    else:
       print(ofig)
       plt.show()








def read_tseries( slon=130.0, elon=137.5,
          slat=33.0, elat=36.0, dth=24,
          stime=datetime( 2018, 7, 1, 0 ),
          etime=datetime( 2018, 7, 5, 0 ), nvar="PW", hpa=500 ):


    TOP = "/data_ballantine02/miyoshi-t/honda/SCALE-LETKF/BAIU2018_5.3.6"
    
    
    INFO = {"TOP": TOP, }

    lon2d, lat2d = get_lonlat( INFO, stime=datetime( 2018, 7, 1, 0 ) )

    flag2d = np.where( ( lon2d >= slon ) & ( lon2d <= elon) & 
                       ( lat2d >= slat ) & ( lat2d <= elat ), 
                       1.0, np.nan )


    if nvar == "RAIN" or nvar == "MSLP" or nvar == "PW":
      of = 'dat/aream/{0:}_lon{1:}-{2:}_lat{3:}-{4:}_{5:}_dth{6:0=3}.npz'.format( nvar, slon, elon, slat, elat, stime.strftime('s%H%m%d'), dth )
    else:
      of = 'dat/aream/{0:}{1:}_lon{2:}-{3:}_lat{4:}-{5:}_{6:}_dth{7:0=3}.npz'.format( nvar,hpa, slon, elon, slat, elat, stime.strftime('s%H%m%d'), dth )

    print( of )

    try: 
       data = np.load( of, allow_pickle=True )
       return( data['evar'], data['vtimes'] )
    except:
       print( "No file, read now" )
       os.makedirs( 'dat/aream', exist_ok=True )

    if nvar != "RAIN":
       dth = 6

    vtimes = []

    cnt = 0
    time = stime
    while time <= etime:
        vtimes.append( time )

        cnt += 1
        time += timedelta( hours=dth )

    mmax = 50
    evar = np.zeros( ( cnt, mmax ) )


    t = 0
    time = stime
    while time <= etime:
       print( time )
       for m in range( mmax ): 
          evar[t,m] = np.nanmean( get_var( INFO, nvar=nvar, stime=stime, vtime=time, m=m+1, adt=timedelta( hours=dth ), hpa=hpa ) * flag2d )
       t += 1

       time += timedelta( hours=dth )

    if nvar == "RAIN":
       evar[0,:] = np.nan

    print( np.mean( evar, axis=1 ))
    print( np.std( evar, axis=1, ddof=1 ))


    np.savez( of, evar=evar, vtimes=vtimes )

    return( evar, vtimes )



    sys.exit()



# forecast loop

stime_l = [ 
#            datetime( 2018, 6, 26, 0),
            datetime( 2018, 6, 27, 0),
            datetime( 2018, 6, 28, 0),
            datetime( 2018, 6, 29, 0),
            datetime( 2018, 6, 30, 0),
            datetime( 2018, 7,  1, 0),
            datetime( 2018, 7,  2, 0),
            datetime( 2018, 7,  3, 0),
            datetime( 2018, 7,  4, 0),
            datetime( 2018, 7,  5, 0),
          ]


hpa = 950
hpa = 500

nvar = "QV"
nvar = "RH"
nvar = "PW"
#nvar = "T"
nvar = "RAIN"
slon = 130.0
elon = 137.5
slat = 33.0
elat = 36.0

#slon = 130.0
#elon = 134.5
#slat = 28.0
#elat = 35.0

# East China Sea
#nvar = "QV"
#slon = 120.0
#elon = 135.0
#slat = 30.0
#elat = 36.0


# Sea of Japan
##elon = 150.0
#slon = 130.0
#elon = 140.0
#slat = 35.0
#elat = 43.0
#nvar = "THE"
#nvar = "THEG"
#nvar = "T"
#nvar = "QV"
#hpa = 950
#hpa = 300
#nvar = "MSLP"

#nvar = "PW"
#slon = 125.0
#elon = 135.0
#slat = 20.0
#elat = 35.0
#
# Trough
#hpa = 300
##nvar = "Z"
#nvar = "T"
#slat = 35.0
#elat = 45.0
#slon = 120.0
#elon = 140.0

# South
#nvar = "MFY"
#slon = 130.0
#elon = 135.0
#slat = 25.0
#elat = 33.0

etime = datetime( 2018, 7, 7, 0 )
#nvar = "RAIN"
adt = timedelta( hours=24 )

hpa_l = [ 500, 700, 850, 950 ]

#hpa_l = [ hpa ]

vtime = datetime( 2018, 7, 5, 0 )
vtime = datetime( 2018, 7, 6, 0 )
vtime_ref = datetime( 2018, 7, 6, 0 )
#vtime_ref = datetime( 2018, 7, 5, 0 )
#vtime = datetime( 2018, 7, 4, 0 )

vtime_ref = datetime( 2018, 7, 7, 0 )
#vtime_ref = datetime( 2018, 7, 6, 0 )
dth = 24
dth = 48

for hpa in hpa_l:
    main( slon=slon, elon=elon, slat=slat, elat=elat, vtime=vtime,
          vtime_ref=vtime_ref, dth=dth,
          stime_l=stime_l, nvar=nvar, hpa=hpa, etime=etime, )
    
    if nvar == "PW" or nvar == "RAIN":
       break

#while time <= etime:
#      for nvar in nvar_l:
#
#   time += timedelta( days=1 )
#
#
