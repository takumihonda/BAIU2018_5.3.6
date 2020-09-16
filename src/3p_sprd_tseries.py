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
#quick = False

if quick:
   res="c"
else:
   res="l"



def main( slon=130.0, elon=137.5,
          slat=33.0, elat=36.0,
          stime_l=[], dth=24,
          vtime=datetime( 2018, 7, 5, 0 ),
          etime=datetime( 2018, 7, 5, 0 ), nvar="PW", hpa=500 ):

    bbox = {'facecolor':'w', 'alpha':0.95, 'pad':2}

    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots( 2, 2, figsize=( 12, 7.5 ) )
    fig.subplots_adjust( left=0.06, bottom=0.07, right=0.97, top=0.97,
                         wspace=0.15, hspace=0.2)
    ax2.axis("off") 
#    ax4.axis("off") 

    ax_l = [ ax3, ax4 ]

    xmin = datetime( 2018, 6, 30, 0)
    xmax = datetime( 2018, 7, 7, 0) 

    ll_ = 'lower left'
    ul_ = 'upper left'

    loc_l = [ ul_, ul_, ]

    fac = 1.0
    if nvar == "MSLP": 
       ymin1, ymax1  = 995.0, 1019.0
       ymin2, ymax2  = 0.0, 6.0
#       xmax = datetime( 2018, 7, 5, 0) 
       dy1, dy2 = 4.0, 1.0
       yunit = '(hPa)'
       loc_l = [ ll_, ul_, ]

    elif nvar == "RAIN": 
       ymin1, ymax1  = 0.0, 100.0
       ymin2, ymax2  = 0.0, 30.0
       dy1, dy2 = 10, 5
       yunit = '(mm/{0:}h)'.format( dth )

    elif nvar == "Z": 
       if hpa == 300:
          ymin1, ymax1  = 9460.0, 9660.0
       ymin2, ymax2  = 0.0, 35.0
       dy1, dy2 = 40, 5
       yunit = '(m)'

    elif nvar == "T": 
       if hpa == 950:
          ymin1, ymax1  = 286.0, 298.0
       elif hpa == 300:
          ymin1, ymax1  = 236.0, 245.0
       ymin2, ymax2  = 0.0, 2.0
       dy1, dy2 = 2, 0.5
       yunit = '(K)'

    elif nvar == "PW": 
       ymin1, ymax1  = 42.0, 69.0
       ymin2, ymax2  = 0.0, 9.0
       dy1, dy2 = 3, 1.0
       yunit = r'(mm/m$^2$)'

    elif nvar == "MFY": 
       ymin1, ymax1  = 0.0, 0.4
       ymin2, ymax2  = 0.0, 0.1
       dy1, dy2 = 0.1, 0.02
       yunit = r'(kg/kg m s$^{-1}$)'

    elif nvar == "QV": 
       ymin1, ymax1  = 0.0, 6.5
       ymin2, ymax2  = 0.0, 2.0
       dy1, dy2 = 1, 0.5
       yunit = r'(g/kg)'
       fac = 1.e3

    elif nvar == "RH": 
       ymin1, ymax1  = 0.0, 100.0
       ymin2, ymax2  = 0.0, 26.0
       dy1, dy2 = 10, 4
       yunit = r'(%)'
       fac = 1.e2
       loc_l = [ ll_, ul_, ]


    dy_l = [ dy1, dy2 ]
    ymin_l = [ ymin1, ymin2 ]



    ymax_l = [ ymax1, ymax2 ]
    lw = 2.0


    lons = 111
    lone = 159
    late = 46
    lats = 19

    m_l = prep_proj_multi('merc', [ ax1 ], res=res, ll_lon=lons, ur_lon=lone, 
             ll_lat=lats, ur_lat=late, fs=8 )

    TOP = "/data_ballantine02/miyoshi-t/honda/SCALE-LETKF/BAIU2018_5.3.6"
    
    INFO = {"TOP": TOP, }

    lon2d, lat2d = get_lonlat( INFO, stime=datetime( 2018, 7, 1, 0 ) )
    clevs_gph = np.arange(0, 20000, 20 )
    clevs_slp = np.arange(800, 1200, 4 )
    clevs = clevs_gph

    slp_ = get_var( INFO, nvar="MSLP", stime=vtime, vtime=vtime, m=0, )
    gph_ = get_var( INFO, nvar="Z", stime=vtime, vtime=vtime, m=0, hpa=hpa )
    var2 = gph_
    if nvar == "MSLP":
       var2 = slp_
       clevs = clevs_slp
    elif nvar == "Z":
       var2 = gph_
       clevs = clevs_gph
    elif nvar == "PW":
       var2 = slp_
       clevs = clevs_slp
       
    x2d_, y2d_ = m_l[0](lon2d, lat2d) 

    if nvar == "RAIN":
       # JMA
       jvtime = vtime
       jma2d, JMAr_lon, JMAr_lat = get_grads_JMA( jvtime-adt , dth, ACUM=True )
   
       jma2d[jma2d < 0.1] = np.nan
       var_ = jma2d
   
       lon2d_jma, lat2d_jma = np.meshgrid( JMAr_lon, JMAr_lat )
       x2d, y2d = m_l[0](lon2d_jma, lat2d_jma) 
       levs = np.arange( 10, 155, 5 )
       cmap = plt.cm.get_cmap("jet")
   
       cmap.set_under('gray',alpha=1.0)
       extend = 'both'
       var2 = slp_
       clevs = clevs_slp
    else:
       var_ = get_var( INFO, nvar=nvar, stime=vtime, vtime=vtime, m=0, hpa=hpa )
       x2d = x2d_
       y2d = y2d_

    cmap_, levs_, unit_, extend_, nvar_, fac_ = def_cmap( nvar=nvar, hpa=hpa )
    lc = 'k'
    lw = 0.5

    if nvar != "MSLP" and nvar != "Z":

       if nvar == "RAIN":
          cmap_.set_under('lightgray',alpha=0.7 )
          extend_ = 'both'

       SHADE = ax1.contourf( x2d, y2d, var_*fac_, levels=levs_, cmap=cmap_,
                             extend=extend_)

       pos = ax1.get_position()
       cb_width = 0.008
       cb_height = pos.height*0.95
       ax_cb = fig.add_axes( [pos.x1+0.01, pos.y0+0.01, cb_width, cb_height] )
       cb = plt.colorbar( SHADE, cax=ax_cb, orientation = 'vertical', ticks=levs_[::2])
       cb.ax.tick_params( labelsize=8, )
    
       ax1.text( 0.98, 1.01, yunit, 
                 fontsize=8, transform=ax1.transAxes,
                 horizontalalignment='left', 
                 verticalalignment='bottom', )

    x2d = x2d_
    y2d = y2d_
    print( "chk", np.nanmax(var2), np.nanmin(var2))
    if nvar == "PW":
       lc = 'gainsboro'
       lw = 1.0
    CONT = ax1.contour( x2d, y2d, var2, 
                       colors=lc, zorder=2,
                       linewidths=lw, levels=clevs )
    ax1.clabel( CONT, fontsize=6, fmt='%.0f' )

    draw_rec( m_l[0], ax1, slon, elon, slat, elat, c='k', lw=2.0, ls='solid' )

    if var2 is  slp_:
       nvar2 = "MSLP"
    elif var2 is gph_:
       nvar2 = "Z" + str( hpa )
    
    ptit = "Analyzed {0:} & {1:} at {2:}".format( nvar_, nvar2, vtime.strftime('%HUTC %m/%d')) 
    if nvar == "RAIN":  
       ptit = "Obesrved 24-h {0:} & analyzed {1:} at {2:}".format( nvar_, nvar2, vtime.strftime('%HUTC %m/%d')) 
    elif nvar == "MSLP":  
       ptit = "Analyzed {0:} at {1:}".format( nvar_, vtime.strftime('%HUTC %m/%d')) 

    ax1.text( 0.5, 1.01, ptit, 
              fontsize=11, transform=ax1.transAxes,
              horizontalalignment='center', 
              verticalalignment='bottom', )

    ax1.text( -0.1, 1.01, "(a)", 
              fontsize=10, transform=ax1.transAxes,
              horizontalalignment='left', 
              verticalalignment='bottom', )


    ax1_ = ax3
    ax2_ = ax4

    lw = 2.0
    import matplotlib.cm as cm       

    for it, stime in enumerate( stime_l ):
        lc = cm.jet( it / len(stime_l) )
        evar, vtimes = read_tseries( slon=slon, elon=elon, slat=slat, elat=elat,
                                     stime=stime, nvar=nvar, hpa=hpa, etime=etime, dth=dth )

        std = np.std( evar, axis=1, ddof=1 ) *fac
        mean = np.mean( evar, axis=1, ) * fac

        print( '{0:}, Mean:{1:.2f}, {2:.2f}'.format( stime.strftime('%HUTC %m/%d'), np.max(mean), np.max(std) ) )

        ax1_.plot( vtimes, mean, label=stime.strftime('%m/%d'),
                   linewidth=lw, color=lc ) #colors=cc_l[]  )
        ax1_.fill_between( vtimes, mean-std, mean+std, alpha=0.1, 
                          color=lc )

        ax2_.plot( vtimes, std, label=stime.strftime('%m/%d'),
                   linewidth=lw, color=lc ) #colors=cc_l[]  )

    nvar_ = nvar
    if nvar != "MSLP" and nvar != "RAIN" and nvar != "PW":
       nvar_ = nvar + str( hpa )
    tit_l = [ '{0:} forecast mean and spread'.format( nvar_ ),
              '{0:} forecast spread'.format( nvar_ ), ]

 

    ylab_l = [ '{0:} {1:}'.format( nvar_, yunit ),
               '{0:} spread {1:}'.format( nvar_, yunit ), ]

    pnum_l = [ "(b)", "(c)"]

    for i, ax in enumerate( ax_l ):

        ax.vlines( x=vtime, ymin=ymin_l[i], ymax=ymax_l[i], lw=1.0, ls='dashed', 
                   color='gray' )
        print( "chk", ymin_l[i], ymax_l[i] )

        ax.xaxis.set_major_locator(mdates.HourLocator(interval=24) )
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%HUTC\n%m/%d'))  
        
        ax.tick_params( axis='x', labelsize=9 )    

        ax.set_xlim( xmin, xmax )
        ax.set_ylim( ymin_l[i], ymax_l[i] )
        ax.yaxis.set_ticks( np.arange( ymin_l[i], ymax_l[i]+dy_l[i], dy_l[i] ) ) 
        ax.set_ylabel( ylab_l[i], fontsize=10 )   

        ax.legend( loc=loc_l[i], fontsize=10 )

        ax.text( 0.5, 1.01, tit_l[i],
                 fontsize=12, transform=ax.transAxes,
                 horizontalalignment='center', 
                 verticalalignment='bottom', )
                 #bbox=bbox )

        ax.text(  0.0, 1.01, pnum_l[i], 
                  fontsize=10, transform=ax.transAxes,
                  horizontalalignment='left', 
                  verticalalignment='bottom', )


    opath = "png/sprd_ts"
    ofig = "3p_sprd_{0:}_lon{1:}_{2:}_lat{3:}_{4:}_hpa{5:}".format( nvar_, slon, elon, slat, elat, hpa ) 

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
      of = 'dat/aream/{0:}_lon{1:}-{2:}_lat{3:}-{4:}_{5:}.npz'.format( nvar, slon, elon, slat, elat, stime.strftime('s%H%m%d') )
    else:
      of = 'dat/aream/{0:}{1:}_lon{2:}-{3:}_lat{4:}-{5:}_{6:}.npz'.format( nvar,hpa, slon, elon, slat, elat, stime.strftime('s%H%m%d') )

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
#nvar = "PW"
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

hpa_l = [ 700, 850, 950 ]

#hpa_l = [ hpa ]

vtime = datetime( 2018, 7, 5, 0 )
vtime = datetime( 2018, 7, 6, 0 )
#vtime = datetime( 2018, 7, 4, 0 )

for hpa in hpa_l:
    main( slon=slon, elon=elon, slat=slat, elat=elat, vtime=vtime,
          stime_l=stime_l, nvar=nvar, hpa=hpa, etime=etime, )

#while time <= etime:
#      for nvar in nvar_l:
#
#   time += timedelta( days=1 )
#
#
