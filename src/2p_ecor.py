import numpy as np

from netCDF4 import Dataset
from datetime import datetime
from datetime import timedelta
import os
import sys

import matplotlib.pyplot as plt
 
from tools_BAIU import get_lonlat, get_arain, get_pw, prep_proj_multi, draw_rec, get_gph, get_prsvar, get_the, get_the_grad, get_rh, get_mslp, get_mf_grad, get_q1, read_etrack, get_olr

quick = True   
quick = False


def main( stime=datetime( 2018, 6, 30, 0), 
          slon=130.0, elon=137.5,
          slat=33.0, elat=36.0,
          adt_h=24,
          vtime_ref=datetime( 2018, 7, 6, 0, 0, 0 ),
          vtime_l=[], rvar="PW", tvar="PW", hpa=500 ):


    thrs = 100.0
    #thrs = 10.0
    thrs = 50.0

    TOP = "/data_ballantine02/miyoshi-t/honda/SCALE-LETKF/BAIU2018_5.3.6"
    
    


    adt = timedelta( hours=adt_h )
    

    INFO = {"TOP": TOP, }


    lon2d, lat2d = get_lonlat( INFO, stime=stime )


    rain_l = np.zeros( 50 )


    # get reference
    for m in range( 50 ):
        rain_ = get_arain( INFO, stime=stime, vtime=vtime_ref, adt=adt, m=m+1 )
        rain_l[m] = np.mean( rain_[ (lon2d >= slon ) & (lon2d <= elon) & (lat2d >= slat) & (lat2d <= elat) ] )


    rain_l -= np.mean( rain_l )


    tclon_l, tclat_l, tcmslp_l, time_l = read_etrack( stime=stime, )
    tclon_l -= np.nanmean( tclon_l, axis=0, keepdims=True )
    tclat_l -= np.nanmean( tclat_l, axis=0, keepdims=True  )
    tcmslp_l -= np.nanmean( tcmslp_l, axis=0, keepdims=True  )

    print( "Reference read: complete" )

    bbox = {'facecolor':'w', 'alpha':1.0, 'pad':2}

    if rvar == "RAIN":
       ref_l = rain_l
    print( ref_l )
    print( "" )

    lons = 116
    lone = 155
    late = 50
    lats = 21

    pnum_l = [ "(a)", "(b)" ]

    ecor = np.zeros( ( lon2d.shape[0], lon2d.shape[1] ) )

    evar = np.zeros( ( 50, lon2d.shape[0], lon2d.shape[1] ) )
    evar2 = np.zeros( ( 50, lon2d.shape[0], lon2d.shape[1] ) )


    fig, ( (ax1,ax2) ) = plt.subplots( 1, 2, figsize=( 10.2, 4.8 ) )
    fig.subplots_adjust( left=0.04, bottom=0.01, right=0.93, top=0.98,
                         wspace=0.1, hspace=0.02)
   
    ax_l = [ ax1, ax2 ]
    m_l = prep_proj_multi('merc', ax_l, ll_lon=lons, ur_lon=lone, 
            ll_lat=lats, ur_lat=late )
    x2d, y2d = m_l[0](lon2d, lat2d)

    for i, vtime in enumerate( vtime_l ):
       ax = ax_l[i]
       delta = (vtime - stime).total_seconds()   

       if delta < 0:
          continue



       for m in range( 50 ):
           gph_ = get_gph( INFO, stime=stime, vtime=vtime, m=m+1, hpa=hpa )
           slp_ = get_mslp( INFO, stime=stime, vtime=vtime, m=m+1, )
           var2_ = gph_

           if tvar == "PW":
              var_ = get_pw( INFO, stime=stime, vtime=vtime, m=m+1, )
              var2_ = slp_

           elif tvar == "MSLP":
              var_ = slp_
              var2_ = var_
           elif tvar == "Z":
              var_ = get_gph( INFO, stime=stime, vtime=vtime, m=m+1, hpa=hpa )
           elif tvar == "RAIN":
              var_ = get_arain( INFO, stime=stime, vtime=vtime, adt=adt, m=m+1 )
              var2_ = slp_
           elif tvar == "THE":
              var_ = get_the( INFO, stime=stime, vtime=vtime, m=m+1, hpa=hpa )
           elif tvar == "THEY" or tvar == "THEX" or tvar == "THEYA":
              var_x, var_y = get_the_grad( INFO, stime=stime, vtime=vtime, m=m+1, hpa=hpa )
              if tvar == "THEY":
                 var_ = var_y
              elif tvar == "THEX":
                 var_ = var_x
              elif tvar == "THEYA":
                 var_ = np.abs( var_y )
           elif tvar == "RH":
              var_ = get_rh( INFO, stime=stime, vtime=vtime, m=m+1, hpa=hpa )
           elif tvar == "MFY" or tvar == "MFX":
              q_ = get_prsvar( INFO, nvar="QVprs", stime=stime, vtime=vtime, m=m+1, hpa=hpa )
              if tvar == "MFY":
                v_ = get_prsvar( INFO, nvar="Vprs", stime=stime, vtime=vtime, m=m+1, hpa=hpa )
              elif tvar == "MFX":
                v_ = get_prsvar( INFO, nvar="Uprs", stime=stime, vtime=vtime, m=m+1, hpa=hpa )
              var_ = q_ * v_

           elif tvar == "MFD":
              var_ = get_mf_grad( INFO, stime=stime, vtime=vtime, m=m+1, hpa=hpa )

           elif tvar == "UDIF" or tvar == "VDIF":
              if tvar == "UDIF":
                 tvar_ = "Uprs"
              var1_ = get_prsvar( INFO, nvar=tvar_, stime=stime, vtime=vtime, m=m+1, hpa=hpa )
              var2_ = get_prsvar( INFO, nvar=tvar_, stime=stime, vtime=vtime, m=m+1, hpa=950 )
              var_ = var1_ - var2_
           elif tvar == "Q1":
              var_ = get_q1( INFO, stime=stime, vtime=vtime, m=m+1, hpa=hpa )
#              var2_ = get_q1( INFO, stime=stime, vtime=vtime, m=m+1, hpa=850 )
#              var_ -= var2_
           elif tvar == "OLR":
              var_ = get_olr( INFO, stime=stime, vtime=vtime, m=m+1, )
           else:
              tvar_ = tvar + "prs"
              var_ = get_prsvar( INFO, nvar=tvar_, stime=stime, vtime=vtime, m=m+1, hpa=hpa )
           evar[m,:,:] = var_[:]
           evar2[m,:,:] = var2_[:]
   
       evar -= np.mean( evar, axis=0 )
   
       cnt = 0
       ecor[:] = 0.0
       for m in range( 50 ):
           if np.isnan( ref_l[m] ):
              evar[m,:,:] = np.nan
              continue
           cnt += 1
           ecor += evar[m,:,:] * ref_l[m] 
   
       ecor = ecor / np.nanstd( ref_l, ddof=1 ) / np.nanstd( evar, ddof=1, axis=0 ) / cnt
       print("Count:",cnt)
       #ecor = var_ # DEBUG 
  
       print( np.nanmax( var_), np.nanmin(var_) )
       print( "Compute correlation" )

       levs = np.arange( -0.7, 0.8, 0.1 )
       cmap = plt.cm.get_cmap("RdBu_r")
   
       print( np.max(ecor), np.min(ecor) )
       SHADE = ax.contourf( x2d, y2d, ecor, levels=levs,
                         cmap=cmap, extend='both' )
   
       if i == 1:
          pos = ax.get_position()
          cb_width = 0.015
          cb_height = pos.height*0.98
          ax_cb = fig.add_axes( [pos.x1+0.01, pos.y0+0.01, cb_width, cb_height] )
          cb = plt.colorbar( SHADE, cax=ax_cb, orientation = 'vertical', ticks=levs)
          cb.ax.tick_params( labelsize=8 )

       draw_rec( m_l[i], ax, slon, elon, slat, elat, lw=2.0, )

       lc = 'k'
       lw = 1.0
       if tvar == "MSLP" or tvar == "RAIN" or tvar == "PW":
          clevs = np.arange( 900, 1200, 4 )
          fac = 1.e-2
       else:
          clevs = np.arange( 0, 15000, 20 )
          fac = 1.0
          lw = 0.5
       CONT = ax.contour( x2d, y2d, np.mean( evar2, axis=0 )*fac, 
                          colors=lc,
                          linewidths=lw, levels=clevs )
       ax.clabel( CONT, fontsize=6, fmt='%.0f' )
  

       if rvar == "PW" or rvar == "RAIN":
          rrvar = rvar
       else:
          rrvar = rvar + str( hpa )

       if tvar == "PW" or tvar == "RAIN" or tvar == "MSLP" or tvar == "OLR":
          ttvar = tvar
       else:
          ttvar = tvar + str( hpa )





       if rvar == "RAIN":
          dt = ( vtime - ( vtime_ref - adt ) ).total_seconds() / 3600.0
       else:
          dt = ( vtime - ( vtime_ref ) ).total_seconds() / 3600.0
#       note = "Valid: {0:}\nInit: {1:}\nT{2:0=+2}h".format( vtime.strftime('%HUTC %m/%d'), stime.strftime('%H UTC %m/%d'), int( dt ) )
       note = "Valid: {0:}".format( vtime.strftime('%HUTC %m/%d'), )
       ax.text( 0.5, 0.99, note,
                fontsize=12, transform=ax.transAxes,
                ha='center', 
                va='top', 
                zorder=10,
                bbox=bbox, )
   
       ax.text( 0.01, 0.99, pnum_l[i],
                fontsize=11, transform=ax.transAxes,
                ha='left', 
                va='top', 
                bbox=bbox, )

   
       
    tit = "Ensemble-based correlations: {0:} & {1:}".format( rrvar, ttvar )
    fig.suptitle( tit, fontsize=14 )
#    ax.text( 0.5, 1.05, tit,
#             fontsize=14, transform=ax.transAxes,
#             ha='center', 
#             va='center', )

    ofig = "2p_ecor_r{0:}_t{1:}_v{2:}_vr{3:}_adt{4:0=3}".format( rrvar, ttvar, vtime_l[0].strftime('%H%m%d'), vtime_ref.strftime('%H%m%d'), adt_h ) 
    print( ofig )

    if not quick:       
       opath = "png/2p_ecor_s{0:}".format( stime.strftime('%H%m%d'),)
       os.makedirs(opath, exist_ok=True)
        
       ofig = os.path.join(opath, ofig + ".png")
       plt.savefig(ofig,bbox_inches="tight", pad_inches = 0.1)
       plt.clf()
    else:
       plt.show()
   



###################


slon = 130.0
elon = 137.5
slat = 33.0 
elat = 36.0


rvar = "RAIN"

vtime_ref = datetime( 2018, 7, 7, 0, 0 )
adt_h = 48

stime = datetime( 2018, 7, 3, 0)
tvar = "V"
hpa = 850

vtime_l = [
           datetime( 2018, 7, 4, 0),
           datetime( 2018, 7, 5, 0),
          ]

main( stime=stime, vtime_l=vtime_l,   
      slon=slon, elon=elon,
      slat=slat, elat=elat,
      vtime_ref=vtime_ref,
      adt_h=adt_h,
      rvar=rvar, tvar=tvar, hpa=hpa )
