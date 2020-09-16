import numpy as np

from netCDF4 import Dataset
from datetime import datetime
from datetime import timedelta
import os
import sys

import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
 
from tools_BAIU import get_lonlat, prep_proj_multi, get_arain, def_cmap, get_var, get_grads_JMA


quick = True   
quick = False


if quick:
   res="c"
else:
   res="l"

def main( stime_l=[],
          vtime=datetime( 2018, 7, 5, 0 ), nvar="PW", hpa=500 ):

    adt = timedelta( hours=24 )


    TOP = "/data_ballantine02/miyoshi-t/honda/SCALE-LETKF/BAIU2018_5.3.6"
    
    adt = timedelta( hours=24 )
    
    bbox = {'facecolor':'w', 'alpha':0.95, 'pad':2}

    INFO = {"TOP": TOP, }

    lon2d, lat2d = get_lonlat( INFO, stime=datetime( 2018, 7, 1, 0 ) )

    fig, ((ax1,ax2,ax3,ax4),(ax5,ax6,ax7,ax8)) = plt.subplots( 2, 4, figsize=( 14, 6.0 ) )
    fig.subplots_adjust( left=0.03, bottom=0.03, right=0.96, top=0.95,
                         wspace=0.1, hspace=0.02)
        
    #lons = 106
    lons = 111
    #lone = 164
    lone = 159
    late = 49
    lats = 16
        
    ax_l_ = [ ax1, ax2, ax3, ax4, ax5, ax6, ax7, ax8 ]
    ax_l = []
    for i, ax in enumerate( ax_l_ ):
 
       stime = stime_l[i]
       print( i, stime, vtime)

       delta = (vtime - stime).total_seconds()

       if nvar == "RAIN" and i == 7:
          continue

       if delta < 0:
          ax.axis('off')
          continue
       else:
          ax_l.append( ax )


    m_l = prep_proj_multi('merc', ax_l, res=res, fs=6,
                           ll_lon=lons, ur_lon=lone, ll_lat=lats, ur_lat=late )
 
    x2d, y2d = m_l[0](lon2d, lat2d)
        
    extend = 'max'

    lc = 'k'
    lw = 0.5


    cmap, levs, unit, extend, nvar_, fac = def_cmap( nvar=nvar, hpa=hpa )
    if nvar == "RAIN":
       cmap.set_under('lightgray',alpha=0.7 )
       extend = "both"

    if nvar == "PW":
       lc = "gainsboro"
       lw = 1.0

    clevs = np.arange( 900, 1100, 4 )

    mmax = 50 
    if quick:
       mmax = 5
    evar = np.zeros( ( mmax, lon2d.shape[0], lon2d.shape[1] ) )
    eslp = np.zeros( ( mmax, lon2d.shape[0], lon2d.shape[1] ) )
    egph = np.zeros( ( mmax, lon2d.shape[0], lon2d.shape[1] ) )
 
    for i, ax in enumerate( ax_l ):
        
       stime = stime_l[i]
       print( i, stime, vtime)

       for m in range( 0, mmax ):

           slp_ = get_var( INFO, nvar="MSLP", stime=stime, vtime=vtime, m=m+1, )
           gph_ = get_var( INFO, nvar="Z", stime=stime, vtime=vtime, m=m+1, hpa=hpa )
           var_ = get_var( INFO, nvar=nvar, stime=stime, vtime=vtime, m=m+1, adt=timedelta( hours=24 ), hpa=hpa )


           evar[m,:,:] = var_
           eslp[m,:,:] = slp_
           egph[m,:,:] = gph_
           if m % 5 == 0:
              print( m )

       var = np.mean( evar, axis=0) * fac
       print( '{0:}, max:{1:.2f}, min:{2:.2f}'.format( nvar, np.nanmax(var), np.nanmin(var) ) )

       ptit = 'Ini: {0:}'.format( stime.strftime('%HUTC %m/%d') )
       if i == 7:
          ptit = 'Analysis: {0:}'.format( stime.strftime('%HUTC %m/%d') )

       ax.text( 0.5, 0.95, ptit,
                fontsize=9, transform=ax.transAxes,
                ha='center', 
                va='center',
                bbox = bbox, zorder=4 )

       if nvar != "Z" and nvar != "MSLP":
          SHADE = ax.contourf( x2d, y2d, var, 
                                levels=levs, cmap=cmap,
                                extend=extend, zorder=1 )
          var2_ = np.mean( eslp, axis=0 )
          if nvar == "U" or nvar == "V" or nvar == "T":
             var2_ = np.mean( egph, axis=0 )
             clevs = np.arange(0, 15000, 20 )
             
          CONT = ax.contour( x2d, y2d, var2_, 
                              colors=lc, zorder=2,
                              linewidths=lw, levels=clevs )
          ax.clabel( CONT, fontsize=6, fmt='%.0f' )


       else:
          CONT0 = ax.contour( x2d, y2d, var, 
                             levels=levs, colors='k',
                             linewidths=lw, zorder=2 )
          ax.clabel( CONT0, fontsize=6, fmt='%.0f' )


#       if nvar == "PW":
#          CONT0 = ax.contour( x2d, y2d, var, 
#                              colors='aqua', linestyles='solid',
#                              linewidths=1.0, levels=[60,] )
#          ax.clabel( CONT0, fontsize=8, fmt='%.0f' )
   
    if nvar == "RAIN":
       # JMA
       adth = 24
       adt = timedelta( hours=adth )
       jma2d, JMAr_lon, JMAr_lat = get_grads_JMA( vtime-adt , adth, ACUM=True )
   
       jma2d[jma2d < 0.1] = np.nan
       rain = jma2d
   
       lon2d_jma, lat2d_jma = np.meshgrid( JMAr_lon, JMAr_lat )

       m_l = prep_proj_multi('merc', [ ax8 ], res=res, fs=6,
                              ll_lon=lons, ur_lon=lone, ll_lat=lats, ur_lat=late )

       x2d, y2d = m_l[0](lon2d_jma, lat2d_jma) 

       SHADE = ax8.contourf( x2d, y2d, rain, 
                            levels=levs, cmap=cmap,
                            extend='both') #,extend )

       ptit = "JMA radar & analyzed MSLP"
       ax8.text( 0.5, 0.95, ptit,
                fontsize=9, transform=ax8.transAxes,
                ha='center', 
                va='center',
                bbox = bbox)

       slp_ = get_var( INFO, nvar="MSLP", stime=vtime, vtime=vtime, m=0, )
       x2d, y2d = m_l[0](lon2d, lat2d)
       CONT = ax8.contour( x2d, y2d, slp_, 
                           colors=lc,
                           linewidths=lw, levels=clevs )
       ax8.clabel( CONT, fontsize=6, fmt='%.0f' )



#       if nvar == "PW":

    if nvar != "Z" and nvar != "MSLP":
       pos = ax8.get_position()
       cb_width = 0.006
       cb_height = pos.height*1.5
       ax_cb = fig.add_axes( [pos.x1+0.005, pos.y0+0.01, cb_width, cb_height] )
       cb = plt.colorbar( SHADE, cax=ax_cb, orientation = 'vertical', ticks=levs[::2])
       cb.ax.tick_params( labelsize=8 )
    ax4.text( 0.9, 1.01, unit,
             fontsize=9, transform=ax4.transAxes,
             ha='left', 
             va='bottom', )

    ax4.text( 0.7, 1.01, "Valid: {0:}".format( vtime.strftime('%HUTC %m/%d') ),
             fontsize=11, transform=ax4.transAxes,
             ha='right', 
             va='bottom', )

 
    ax_l = [ ax1, ax2, ax3, ax4, ax5, ax6, ax7, ax8 ]
    pnum_l = [ "(a)", "(b)", "(c)", "(d)", "(e)", "(f)", "(g)", "(h)" ]
    for i, ax in enumerate( ax_l ):
       ax.text( 0.01, 0.99, pnum_l[i],
                fontsize=9, transform=ax.transAxes,
                ha='left', va='top', 
                bbox = bbox )

    

    tnvar = nvar_
    tnvar_ = nvar_
    if nvar == "RAIN":
       tnvar_ = nvar
       tnvar2 = "MSLP"
       tnvar = "24-h precipitation amount"
       tit = 'Forecast/observed {0:} & {1:}'.format( tnvar, tnvar2 ) 
    else:
       tnvar2 = "Z" + str(hpa)
       tnvar_ = nvar + str(hpa)
       tnvar = nvar + str(hpa)
       if nvar == "PW":
          tnvar_ = nvar
          tnvar2 = "MSLP"
 
       tit = 'Forecast/analyzed {0:} & {1:}'.format( tnvar, tnvar2 ) 

    fig.suptitle( tit, fontsize=14 )
        
    opath = "png/fig0808"
    ofig = "mean_{0:}_v{1:}".format( tnvar_, vtime.strftime('%H%m%d') ) 

    if not quick:

      os.makedirs(opath, exist_ok=True)
    
      ofig = os.path.join(opath, ofig + ".png")
      plt.savefig(ofig,bbox_inches="tight", pad_inches = 0.1)
      print(ofig)
      plt.clf()
    else:
      print(ofig)
      plt.show()



# forecast loop




hpa = 950


nvar = "RAIN"
vtime = datetime( 2018, 7, 6, 0 )
nvar = "PW"
nvar = "RH"
hpa = 500
nvar = "T"
hpa = 300
nvar = "EPT"
hpa = 950
vtime = datetime( 2018, 7, 5, 0 )


stime_l = [ 
            datetime( 2018, 6, 27, 0),
            datetime( 2018, 6, 28, 0),
            datetime( 2018, 6, 29, 0),
            datetime( 2018, 6, 30, 0),
            datetime( 2018, 7,  1, 0),
            datetime( 2018, 7,  2, 0),
            datetime( 2018, 7,  3, 0),
            vtime, 
          ]


main( stime_l=stime_l, vtime=vtime, nvar=nvar, hpa=hpa )


