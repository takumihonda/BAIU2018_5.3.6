import numpy as np

from netCDF4 import Dataset
from datetime import datetime
from datetime import timedelta
import os
import sys

import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
 
from scipy import ndimage

p00 = 100000.00 # hPa
Rd = 287.04
Rv = 461.51
epsilon = Rd / Rv

cp = 1004.0

grav = 9.81

r2DX = 0.5 / (18000.0)
rDX = 1.0 / (18000.0)

t0 = 273.15

def convolve_ave( var2d, kernel):
    return( ndimage.convolve( var2d, kernel, mode='reflect' )  )

def get_lonlat( INFO, stime=datetime(2018,7,1), ):

    mem = str(1).zfill(4)

    fn = os.path.join( INFO["TOP"], stime.strftime('%Y%m%d%H%M%S'), "fcst_sno_np00001",
                mem, "p_history.pe000000.nc" )

    with Dataset( fn, "r", format="NETCDF4") as nc:
       lon = nc.variables["lon"][:]
       lat = nc.variables["lat"][:]
 
    return( lon, lat )

def prep_proj_multi( METHOD, axs, res="c", ll_lon=120, ur_lon=150, ll_lat=20, ur_lat=50,
                     fs=10,zorder=2,contc='burlywood',cont_alp=0.2 ):

#    print("proj")

    ddeg = 0.2 # deg


    lat2 = 40.0
    blon = 138.0
    blat = 36.3


    m_l = []
    cc = "k"
    #contc = 'lightgrey'
    contc = contc

    pdlat = 5.0
    pdlon = 5.0
    #pdlat = 1.0
    #pdlon = 2.0

    lc = 'k'
    fs = fs
    lw = 0.1

    for ax in axs:
      m = Basemap(projection=METHOD,resolution = res,
              llcrnrlon = ll_lon,llcrnrlat = ll_lat,
              urcrnrlon = ur_lon,urcrnrlat = ur_lat,
              lat_0 = blat, lat_1 = lat2,
              lat_2 = lat2, lon_0 = blon,
              ax = ax)
      m_l.append(m)

      m.drawcoastlines(linewidth = 0.5, color = cc, zorder=zorder)
      m.fillcontinents(color=contc,lake_color='w', zorder=0, alpha =cont_alp)
      m.drawparallels(np.arange(0,70,pdlat),labels=[1,0,0,0],fontsize=fs,color=lc,linewidth=lw)
      m.drawmeridians(np.arange(0,180,pdlon),labels=[0,0,0,1],fontsize=fs,color=lc,linewidth=lw)


    return( m_l )

def get_arain_t( INFO, stime=datetime(2018,7,1), 
                adt=timedelta(hours=24), m=1 ):

    mem = str(m).zfill(4)
    if m == 0:
       mem = "mean"

    fn = os.path.join( INFO["TOP"], stime.strftime('%Y%m%d%H%M%S'), "fcst_sno_np00001",
                mem, "p_history.pe000000.nc" )

    adts =  adt.total_seconds()

    with Dataset( fn, "r", format="NETCDF4") as nc:
       fts = nc.variables["time"][:]

       dt = int( adts / ( fts[2] - fts[1] ) )

       rain_ = nc.variables["PREC"][:,:,:]*21600
       rain_[ rain_ < 0.0 ] = 0.0
       tmax = rain_.shape[0] // dt
       rain = np.zeros( (tmax, rain_.shape[1], rain_.shape[2]) )

       vtime_l = [0] * tmax


       tt = 0
       for t, ft in enumerate(fts):
           if ft == 0.0:
              continue         

           tt = (t-1) // dt
           rain[tt, :,:] += rain_[t,:,:]
           vtime_l[tt] = stime + timedelta( seconds=ft ) 
#           print( t, tt, ft )

       return( rain, vtime_l )

def get_arain( INFO, stime=datetime(2018,7,1), vtime=datetime(2018,7,1), 
               adt=timedelta(hours=24), m=1 ):

    mem = str(m).zfill(4)
    if m == 0:
       mem = "mean"

    fn = os.path.join( INFO["TOP"], stime.strftime('%Y%m%d%H%M%S'), "fcst_sno_np00001",
                mem, "p_history.pe000000.nc" )
#    print( fn )

    ft_max = ( vtime - stime ).total_seconds()
    ft_min = ( vtime - adt - stime ).total_seconds()
    

    with Dataset( fn, "r", format="NETCDF4") as nc:
       fts = nc.variables["time"][:]
#       print("time", fts/3600)

       idx_s = np.abs( ( fts - ft_min ) ).argmin()
       idx_e = np.abs( ( fts - ft_max ) ).argmin()

       # 
       rain = np.sum( nc.variables["PREC"][idx_s+1:idx_e+1,:,:], axis=0 )*21600

#    print( rain.shape )
#    print( ft_max, ft_min, idx_s, idx_e )
#    print( stime + timedelta( seconds=fts[idx_s+1]), 
#           stime + timedelta( seconds=fts[idx_e+1]) )
#    print( fts[idx_s:idx_e]/3600)
    return( rain )

def get_mslp( INFO, stime=datetime(2018,7,1), vtime=datetime(2018,7,1), m=1 ):

    mem = str(m).zfill(4)
    if m == 0:
       mem = "mean"

    fn = os.path.join( INFO["TOP"], stime.strftime('%Y%m%d%H%M%S'), "fcst_sno_np00001",
                mem, "p_history.pe000000.nc" )

    ft_max = ( vtime - stime ).total_seconds()

    with Dataset( fn, "r", format="NETCDF4") as nc:
#       print("time", fts/3600)

       try:
          fts = nc.variables["time"][:]
          idx_e = np.abs( ( fts - ft_max ) ).argmin()
          mslp = nc.variables["MSLP"][idx_e,:,:]
       except:
          print( "No time" )
          mslp = nc.variables["MSLP"][:,:]

    return( mslp )

def get_gph( INFO, stime=datetime(2018,7,1), vtime=datetime(2018,7,1), m=1, hpa=500 ):

    mem = str(m).zfill(4)
    if m == 0:
       mem = "mean"

    fn = os.path.join( INFO["TOP"], stime.strftime('%Y%m%d%H%M%S'), "fcst_sno_np00001",
                mem, "p_history.pe000000.nc" )
    #print(fn)

    ft_max = ( vtime - stime ).total_seconds()

    with Dataset( fn, "r", format="NETCDF4") as nc:
       
       prs = nc.variables["pressure"][:] # hPa
       idx_v = np.abs( ( prs - hpa ) ).argmin()

       try:
          fts = nc.variables["time"][:]
          idx_e = np.abs( ( fts - ft_max ) ).argmin()
          gph = nc.variables["Gprs"][idx_e,idx_v,:,:]

       except:
          print( "No time" )
          gph = nc.variables["Gprs"][idx_v,:,:]

       # 

    return( gph )

def get_prsvar( INFO, nvar="Vprs", stime=datetime(2018,7,1), vtime=datetime(2018,7,1), m=1, hpa=500 ):

    mem = str(m).zfill(4)
    if m == 0:
       mem = "mean"

    fn = os.path.join( INFO["TOP"], stime.strftime('%Y%m%d%H%M%S'), "fcst_sno_np00001",
                mem, "p_history.pe000000.nc" )
    #print(fn)

    ft_max = ( vtime - stime ).total_seconds()

    with Dataset( fn, "r", format="NETCDF4") as nc:
       
       prs = nc.variables["pressure"][:] # hPa
       idx_v = np.abs( ( prs - hpa ) ).argmin()

       try:
          fts = nc.variables["time"][:]
          idx_e = np.abs( ( fts - ft_max ) ).argmin()
          var = nc.variables[nvar][idx_e,idx_v,:,:]

       except:
          print( "No time" )
          var = nc.variables[nvar][idx_v,:,:]

    return( var )

def get_the( INFO, stime=datetime(2018,7,1), vtime=datetime(2018,7,1), m=1, hpa=500 ):

    mem = str(m).zfill(4)
    if m == 0:
       mem = "mean"

    fn = os.path.join( INFO["TOP"], stime.strftime('%Y%m%d%H%M%S'), "fcst_sno_np00001",
                mem, "p_history.pe000000.nc" )
    #print(fn)

    ft_max = ( vtime - stime ).total_seconds()

    with Dataset( fn, "r", format="NETCDF4") as nc:
       
       prs = nc.variables["pressure"][:] # hPa
       idx_v = np.abs( ( prs - hpa ) ).argmin()

       try:
          fts = nc.variables["time"][:]
          idx_e = np.abs( ( fts - ft_max ) ).argmin()
          tk_ = nc.variables["Tprs"][idx_e,idx_v,:,:]
          qv_ = nc.variables["QVprs"][idx_e,idx_v,:,:]


       except:
          print( "No time" )
          tk_ = nc.variables["Tprs"][idx_v,:,:]
          qv_ = nc.variables["QVprs"][idx_v,:,:]

       eprs_ = qv_ * hpa*1.e2 / ( epsilon + qv_ )
       tast_ = 2840.0 / (3.5 * np.log( tk_ ) - np.log(hpa*1.e2 * 0.01) - 4.805) + 55.0
       the = tk_ * np.power(p00 / (hpa*1.e2), 0.2854 * (1.0 - 0.28*qv_)) * np.exp(qv_ * (1.0 + 0.81 * qv_) * (3376.0 / tast_ - 2.54))

    the[ (the > 1000.0) | (the < 0.0 )] = np.nan

    return( the )

def get_the_grad( INFO, stime=datetime(2018,7,1), vtime=datetime(2018,7,1), m=1, hpa=500 ):
   
    the = get_the( INFO, stime=stime, vtime=vtime, m=m, hpa=hpa )

    if the.ndim == 2:
       [ the_y, the_x ] = np.gradient( the, axis=(0,1) ) 
    elif the.ndim == 3:
       [ the_y, the_x ] = np.gradient( the, axis=(1,2) ) 
    else:
       print( "Error" )
       sys.exit()
    
    #return( the_x*r2DX, the_y*r2DX )
    return( the_x*rDX, the_y*rDX )

def get_mf_grad( INFO, stime=datetime(2018,7,1), vtime=datetime(2018,7,1), m=1, hpa=500 ):
    q_ = get_prsvar( INFO, nvar="QVprs", stime=stime, vtime=vtime, m=m, hpa=hpa )
    u_ = get_prsvar( INFO, nvar="QVprs", stime=stime, vtime=vtime, m=m, hpa=hpa )
    v_ = get_prsvar( INFO, nvar="QVprs", stime=stime, vtime=vtime, m=m, hpa=hpa )

    [ dqvdy, _ ] = np.gradient( q_*v_, axis=(0,1) ) 
    [ _, dqudx ] = np.gradient( q_*u_, axis=(0,1) ) 

    return( ( dqvdy+dqudx ) * rDX )

def get_rh( INFO, stime=datetime(2018,7,1), vtime=datetime(2018,7,1), m=1, hpa=500 ):

    mem = str(m).zfill(4)
    if m == 0:
       mem = "mean"

    fn = os.path.join( INFO["TOP"], stime.strftime('%Y%m%d%H%M%S'), "fcst_sno_np00001",
                mem, "p_history.pe000000.nc" )
    #print(fn)

    ft_max = ( vtime - stime ).total_seconds()

    with Dataset( fn, "r", format="NETCDF4") as nc:
       
       prs = nc.variables["pressure"][:] # hPa
       idx_v = np.abs( ( prs - hpa ) ).argmin()

       try:
          fts = nc.variables["time"][:]
          idx_e = np.abs( ( fts - ft_max ) ).argmin()
          tk_ = nc.variables["Tprs"][idx_e,idx_v,:,:]
          qv_ = nc.variables["QVprs"][idx_e,idx_v,:,:]


       except:
          print( "No time" )
          tk_ = nc.variables["Tprs"][idx_v,:,:]
          qv_ = nc.variables["QVprs"][idx_v,:,:]


       # Teten's formula
       rh_ = 611.2 * np.exp( 17.67*( tk_ - t0 ) / ( tk_ - t0 + 243.5 ) )
       rh_ = epsilon * rh_ / ( hpa*1.e2 - rh_ )

       rh_ = qv_ / rh_

       rh_[ rh_ < 0.0 ] = np.nan

    return( rh_ )

def get_ki( INFO, stime=datetime(2018,7,1), vtime=datetime(2018,7,1), m=1 ):

    mem = str(m).zfill(4)
    if m == 0:
       mem = "mean"

    fn = os.path.join( INFO["TOP"], stime.strftime('%Y%m%d%H%M%S'), "fcst_sno_np00001",
                mem, "p_history.pe000000.nc" )
    #print(fn)

    ft_max = ( vtime - stime ).total_seconds()

    with Dataset( fn, "r", format="NETCDF4") as nc:
       
       prs = nc.variables["pressure"][:] # hPa
       idx_v850 = np.abs( ( prs - 850 ) ).argmin()
       idx_v700 = np.abs( ( prs - 700 ) ).argmin()
       idx_v500 = np.abs( ( prs - 500 ) ).argmin()

       try:
          fts = nc.variables["time"][:]
          idx_e = np.abs( ( fts - ft_max ) ).argmin()
          tk850_ = nc.variables["Tprs"][idx_e,idx_v850,:,:]
          tk700_ = nc.variables["Tprs"][idx_e,idx_v700,:,:]
          tk500_ = nc.variables["Tprs"][idx_e,idx_v500,:,:]
          qv850_ = nc.variables["QVprs"][idx_e,idx_v850,:,:]
          qv700_ = nc.variables["QVprs"][idx_e,idx_v700,:,:]

       except:
          print( "No time" )

          tk850_ = nc.variables["Tprs"][idx_v850,:,:]
          tk700_ = nc.variables["Tprs"][idx_v700,:,:]
          tk500_ = nc.variables["Tprs"][idx_v500,:,:]
          qv850_ = nc.variables["QVprs"][idx_v850,:,:]
          qv700_ = nc.variables["QVprs"][idx_v700,:,:]

       # Teten's formula
       e700_ = qv700_ * 700.0 / ( epsilon + qv700_ ) # mb
       td700_ = ( 243.5 * np.log( e700_) - 440.8 ) / ( 19.48 - np.log( e700_ ) ) + t0
       e850_ = qv850_ * 850.0 / ( epsilon + qv850_ ) # mb
       td850_ = ( 243.5 * np.log( e850_ ) - 440.8 ) / ( 19.48 - np.log( e850_ ) ) + t0

       ki = tk850_ - tk500_ + td850_ - ( tk700_ - td700_ ) - t0 # (deg C)
    return( ki )

def get_grads_JMA(itime,FT,ACUM):
    print("get_JMA",itime)

    JMAr_gx = 2560
    JMAr_gy = 3360
    JMAr_top = "/data11/honda/SCALE-LETKF/JMA/radar/grads"

    jetime = itime + timedelta(seconds=3600) * FT

    jstime = itime + timedelta(seconds=600)
    if not ACUM:
      jstime += timedelta(seconds=3600) * (FT - 1)

    print(jstime,jetime)

    JMA_data_npz = os.path.join( JMAr_top, itime.strftime('%Y/%m/%d'),
             "jmaradar_" + jstime.strftime('%Y%m%d%H%M%S') + "-" + jetime.strftime('%Y%m%d%H%M%S') +  ".npz" )
    JMA_data_nc = os.path.join( JMAr_top, itime.strftime('%Y/%m/%d'),
            "jmaradar_" + jstime.strftime('%Y%m%d%H%M%S') + "-" + jetime.strftime('%Y%m%d%H%M%S') +  ".nc" )

    latmax = 20.004167 + 0.008333 * (JMAr_gy-1)
    JMAr_lat = np.arange(20.004167, latmax,0.008333)
    lonmax = 118.006250 + 0.012500 * (JMAr_gx-1)
    JMAr_lon = np.arange(118.006250, lonmax,0.012500)

    # npz is available?
    ISNPZ = os.path.isfile(JMA_data_npz)

    # nc is available?
    ISNC = os.path.isfile(JMA_data_nc)

    if ISNC:
      JMArain2d,JMAr_lon,JMAr_lat =  read_JMA_nc(JMA_data_nc)
      return JMArain2d,JMAr_lon,JMAr_lat

    if ISNPZ and not ISNC:
      JMArain2d = np.load(JMA_data_npz)['arr_0']
      print("read JMA data from: ", JMA_data_npz)

      write_JMA_nc(JMA_data_nc,JMAr_lon,JMAr_lat,jstime,JMArain2d)

    elif not ISNPZ and not ISNC:

      JMArain2d = np.zeros((JMAr_gy,JMAr_gx))

      jtime2 = jstime
      while (jtime2 <= jetime):

        jtime1 = jtime2 - timedelta(seconds=600)
        fn1 = os.path.join( JMAr_top, jtime1.strftime('%Y/%m/%d'),
                  "jmaradar_" + jtime1.strftime('%Y%m%d%H%M%S') + ".grd")
        fn2 = os.path.join( JMAr_top, jtime2.strftime('%Y/%m/%d'),
                  "jmaradar_" + jtime2.strftime('%Y%m%d%H%M%S') + ".grd")

        for fn in fn1,fn2:
           try:
             infile = open(fn)
           except:
             print("Failed to open",fn)
             sys.exit()

           tmp2d = np.fromfile(infile, dtype=np.dtype('<f4'), count=JMAr_gx*JMAr_gy)  # little endian
           input2d = np.reshape(tmp2d, (JMAr_gy,JMAr_gx))
           input2d[input2d < 0.0] = 0.0 #np.nan # undef is negative in JMA radar
           infile.close
           if fn == fn1:
              rain2d = input2d * 0.5
           else:
              rain2d += input2d * 0.5

        JMArain2d += rain2d / 6 # mm/h -> mm/10min
        jtime2 += timedelta(seconds=600)

      write_JMA_nc( JMA_data_nc, JMAr_lon, JMAr_lat, jstime, JMArain2d )
      print("New file stored: ", JMA_data_nc)
      #sys.exit()
    return( JMArain2d, JMAr_lon, JMAr_lat)

def write_JMA_nc(JMA_data_nc,JMA_lon,JMA_lat,jstime,JMArain2d):

    nc = Dataset(JMA_data_nc, "w", format="NETCDF4")

    nc.createDimension("latitude", len(JMA_lat))
    nc.createDimension("longitude", len(JMA_lon))
    nc.createDimension("level", 1)
    nc.createDimension("time", 1)

    XX = nc.createVariable("longitude","f4",("longitude",))
    XX.units = "degrees_east"

    YY = nc.createVariable("latitude","f4",("latitude",))
    YY.units = "degrees_north"

    ZZ = nc.createVariable("level","i4",("level",))
    ZZ.units = "km"

    times = nc.createVariable("time","f4",("time",))
    nc.description = "Superobs of Himawari-8 IR"

    times.units = "hours since " + str(jstime)
    times.calendar = "gregorian"
    times[0] = 0

    XVAR = nc.createVariable("RAIN","f4",("time","level","latitude","longitude"))
    XVAR.units = "mm"

    XVAR[:,:,:,:] = JMArain2d
    XX[:] = JMA_lon
    YY[:] = JMA_lat
    ZZ[:] = 0

def read_JMA_nc(JMA_data_nc):

    print(JMA_data_nc)
    nc = Dataset(JMA_data_nc, "r", format="NETCDF4")
    JMArain2d = nc.variables['RAIN'][0,0,:,:]
    JMA_lon = nc.variables['longitude'][:]
    JMA_lat = nc.variables['latitude'][:]

    nc.close()

    return( JMArain2d, JMA_lon, JMA_lat )

def draw_rec( m, ax, slon, elon, slat, elat, c='k', lw=5.0, ls='solid' ):

    slat_l = np.linspace( slat, slat )
    elat_l = np.linspace( elat, elat )

    slon_l = np.linspace( slon, slon )
    elon_l = np.linspace( elon, elon )

    lon_l = np.linspace( slon, elon )
    lat_l = np.linspace( slat, elat )

    x_, y_ = m( lon_l, slat_l )
    ax.plot( x_, y_, linewidth=lw, linestyle=ls, color=c )
       
    x_, y_ = m( lon_l, elat_l )
    ax.plot( x_, y_, linewidth=lw, linestyle=ls, color=c )

    x_, y_ = m( slon_l, lat_l )
    ax.plot( x_, y_, linewidth=lw, linestyle=ls, color=c )

    x_, y_ = m( elon_l, lat_l )
    ax.plot( x_, y_, linewidth=lw, linestyle=ls, color=c )

def draw_prapiroon( m, ax, time=datetime( 2018, 7, 1, 0 ), 
                    c='k', ms=5.0, marker='o', lw=10.0,
                    c_track='b', ms_track=2.0, 
                    marker_track='o', label=None ):
 
    lats = [ 19.8, 19.8, 19.8, 19.8, 19.8,
             19.8, 19.8, 19.9, 20.4, 21.0,
             21.8, 22.9, 23.6, 23.9, 24.5,
             25.0, 25.4, 25.8, 26.1, 26.7,
             27.2, 27.7, 28.2, 28.8, 29.5,
             30.1, 30.7, 31.4, 32.0, 32.7,
             33.2, 33.9, 34.4, 35.0, 35.6,
             37.3, 39.6, 40.6, 40.9, 41.3,
             41.7 ]
    lons = [ 132.8, 132.2, 131.4, 130.8, 130.3,
             129.9, 129.8, 129.7, 129.6, 129.4,
             128.8, 128.2, 127.7, 127.3, 127.2,
             127.0, 126.9, 126.8, 126.8, 126.8,
             127.0, 127.1, 127.4, 127.7, 128.1,
             127.9, 127.8, 127.9, 128.2, 128.6,
             128.9, 129.3, 129.6, 130.2, 130.8,
             132.5, 134.8, 136.6, 138.3, 139.5, 
             140.2, ]

    dates = [ datetime( 2018, 6, 28,  0), 
              datetime( 2018, 6, 28,  6),
              datetime( 2018, 6, 28, 12),
              datetime( 2018, 6, 28, 18),
              datetime( 2018, 6, 29,  0),
              datetime( 2018, 6, 29,  6),
              datetime( 2018, 6, 29, 12),
              datetime( 2018, 6, 29, 18),
              datetime( 2018, 6, 30,  0),
              datetime( 2018, 6, 30,  6),
              datetime( 2018, 6, 30, 12),
              datetime( 2018, 6, 30, 18),
              datetime( 2018, 7,  1,  0),
              datetime( 2018, 7,  1,  3),
              datetime( 2018, 7,  1,  6),
              datetime( 2018, 7,  1,  9),
              datetime( 2018, 7,  1, 12),
              datetime( 2018, 7,  1, 15),
              datetime( 2018, 7,  1, 18),
              datetime( 2018, 7,  1, 21),
              datetime( 2018, 7,  2,  0),
              datetime( 2018, 7,  2,  3),
              datetime( 2018, 7,  2,  6),
              datetime( 2018, 7,  2,  9),
              datetime( 2018, 7,  2, 12),
              datetime( 2018, 7,  2, 15),
              datetime( 2018, 7,  2, 18),
              datetime( 2018, 7,  2, 21),
              datetime( 2018, 7,  3,  0),
              datetime( 2018, 7,  3,  3),
              datetime( 2018, 7,  3,  6),
              datetime( 2018, 7,  3,  9),
              datetime( 2018, 7,  3, 12),
              datetime( 2018, 7,  3, 15),
              datetime( 2018, 7,  3, 18),
              datetime( 2018, 7,  4,  0),
              datetime( 2018, 7,  4,  6),
              datetime( 2018, 7,  4, 12),
              datetime( 2018, 7,  4, 18),
              datetime( 2018, 7,  5,  0),
              datetime( 2018, 7,  5,  6),
            ]

    xs_, ys_ = m( lons, lats )
    if lw > 0.0:
       m.plot( xs_, ys_, color=c_track, markersize=ms_track,
                marker=marker_track, linewidth=lw,  )

    if time == datetime( 2018, 6, 28, 0 ):
       lat, lon, hpa = 19.8, 132.8, 1006.0
    elif time == datetime( 2018, 6, 29, 0 ):
       lat, lon, hpa = 19.8, 130.3, 998.0
    elif time == datetime( 2018, 6, 30, 0 ):
       lat, lon, hpa = 20.4, 129.6, 992.0
    elif time == datetime( 2018, 7, 1, 0 ):
       lat, lon, hpa = 23.6, 127.7, 985.0
    elif time == datetime( 2018, 7, 2, 0 ):
       lat, lon, hpa = 27.2, 127.0, 965.0
    elif time == datetime( 2018, 7, 3, 0 ):
       lat, lon, hpa = 32.0, 128.2, 965.0
    elif time == datetime( 2018, 7, 4, 0 ):
       lat, lon, hpa = 37.3, 132.5, 985.0
    elif time == datetime( 2018, 7, 5, 0 ):
       lat, lon, hpa = 41.3, 139.5, 992.0
#    elif time == datetime( 2018, 7, 4, 18 ):
#       lat, lon, hpa = 37.3, 132.5, 985.0
    else:
       print("No TC data")
       return( np.nan, np.nan, np.nan)
    x_, y_ = m( lon, lat )
    if ms > 0.0:
       m.plot( x_, y_, color=c, markersize=ms,
                marker=marker, linewidth=lw, label=label )
 
    return( lon, lat, hpa )

def get_dlm( INFO, stime=datetime(2018,7,1), vtime=datetime(2018,7,1), m=1, dist=np.array([]) ):
    #
    # Get Deep Layer Mean (DLM) wind

    hpa_l = [ 850, 700, 500, 300, 200 ]

    mem = str(m).zfill(4)
    if m == 0:
       mem = "mean"

    fn = os.path.join( INFO["TOP"], stime.strftime('%Y%m%d%H%M%S'), "fcst_sno_np00001",
                mem, "p_history.pe000000.nc" )
    #print(fn)

    ft_max = ( vtime - stime ).total_seconds()

    with Dataset( fn, "r", format="NETCDF4") as nc:
 

       fts = nc.variables["time"][:]
       idx_e = np.abs( ( fts - ft_max ) ).argmin()
      
       prs = nc.variables["pressure"][:] # hPa

       idx_v = np.abs( ( prs - hpa_l[0] ) ).argmin()
       # dist = 1: within an avaraging area
       #      = NaN: outside 
       v = np.nanmean( nc.variables["Vprs"][idx_e,idx_v,:,:] * dist * prs[idx_v] )
       u = np.nanmean( nc.variables["Vprs"][idx_e,idx_v,:,:] * dist * prs[idx_v] )

       for hpa in hpa_l[1:]:
          idx_v = np.abs( ( prs - hpa ) ).argmin()
          v += np.nanmean( nc.variables["Vprs"][idx_e,idx_v,:,:] * dist * prs[idx_v] )
          u += np.nanmean( nc.variables["Uprs"][idx_e,idx_v,:,:] * dist * prs[idx_v] )


       u = u / np.sum( hpa_l )
       v = v / np.sum( hpa_l )

    return( u, v )

def get_var( INFO, nvar="PW", stime=datetime(2018,7,1), vtime=datetime(2018,7,1), m=1, adt=timedelta(hours=24), hpa=500 ):
    if nvar == "PW":
       var_ = get_pw( INFO, stime=stime, vtime=vtime, m=m ) * 0.001 # kg/m2
    elif nvar == "OLR":
       var_ = get_olr( INFO, stime=stime, vtime=vtime, m=m )
    elif nvar == "Q1":
       var_ = get_q1( INFO, stime=stime, vtime=vtime, m=m, hpa=hpa ) 
    elif nvar == "Q1_vg":
       hpa1 = 700
       hpa2 = 850
       var1_ = get_q1( INFO, stime=stime, vtime=vtime, m=m, hpa=hpa1 ) 
       var2_ = get_q1( INFO, stime=stime, vtime=vtime, m=m, hpa=hpa2 )
       var_ = ( var1_ - var2_ ) / ( ( hpa1 - hpa2 ) * 1.e2 )
    elif nvar == "Z":
       var_ = get_gph( INFO, stime=stime, vtime=vtime, m=m, hpa=hpa ) 
    elif nvar == "RH":
       var_ = get_rh( INFO, stime=stime, vtime=vtime, m=m, hpa=hpa ) 
    elif nvar == "THE" or nvar == "EPT":
       var_ = get_the( INFO, stime=stime, vtime=vtime, m=m, hpa=hpa ) 
    elif nvar == "THEG":
       v1_, v2_ = get_the_grad( INFO, stime=stime, vtime=vtime, m=m, hpa=hpa ) 
       var_ = np.sqrt( np.square( v1_ ) + np.square( v2_ ) )
    elif nvar == "RAIN":
       var_ = get_arain( INFO, stime=stime, vtime=vtime, 
               adt=adt, m=m )
    elif nvar == "MFY" or nvar == "MFX":
        q_ = get_prsvar( INFO, nvar="QVprs", stime=stime, vtime=vtime, m=m, hpa=hpa )
        if nvar == "MFY":
           v_ = get_prsvar( INFO, nvar="Vprs", stime=stime, vtime=vtime, m=m, hpa=hpa )
        elif nvar == "MFX":
           v_ = get_prsvar( INFO, nvar="Uprs", stime=stime, vtime=vtime, m=m, hpa=hpa )
        var_ = q_ * v_
    
    elif nvar == "MSLP":
       var_ = get_mslp( INFO, stime=stime, vtime=vtime, m=m ) * 0.01 # hPa
    else:
       var_ =  get_prsvar( INFO, nvar=nvar+"prs", stime=stime, vtime=vtime, m=m, hpa=hpa )

    return( var_ )

def get_pw( INFO, stime=datetime(2018,7,1), vtime=datetime(2018,7,1), m=1 ):

    mem = str(m).zfill(4)
    if m == 0:
       mem = "mean"

    fn = os.path.join( INFO["TOP"], stime.strftime('%Y%m%d%H%M%S'), "fcst_sno_np00001",
                mem, "p_history.pe000000.nc" )

    ft_max = ( vtime - stime ).total_seconds()

    with Dataset( fn, "r", format="NETCDF4") as nc:
#       print("time", fts/3600)

       try:
          fts = nc.variables["time"][:]
          idx_e = np.abs( ( fts - ft_max ) ).argmin()
          pw = nc.variables["PW"][idx_e,:,:]
       except:
          print( "No time" )
          pw = nc.variables["PW"][:,:]

    return( pw )

def get_hdiv_curl( INFO, stime=datetime(2018,7,1), vtime=datetime(2018,7,1), m=1, hpa=500 ):
   
    u_ =  get_prsvar( INFO, nvar="Uprs", stime=stime, vtime=vtime, m=m, hpa=hpa )
    v_ =  get_prsvar( INFO, nvar="Vprs", stime=stime, vtime=vtime, m=m, hpa=hpa )

    u_[ u_ < -200 ] = np.nan
    v_[ v_ < -200 ] = np.nan
 
    [ dudy, dudx ] = np.gradient( u_, axis=(0,1) ) 
    [ dvdy, dvdx ] = np.gradient( v_, axis=(0,1) ) 

    div = ( dudx + dvdy ) * rDX
    curl = ( dvdx - dudy ) * rDX

    return( div, curl )

def get_prapiroon( time=datetime( 2018, 7, 1, 0 ) ):
 
    lats = [ 19.8, 19.8, 19.8, 19.8, 19.8,
             19.8, 19.8, 19.9, 20.4, 21.0,
             21.8, 22.9, 23.6, 23.9, 24.5,
             25.0, 25.4, 25.8, 26.1, 26.7,
             27.2, 27.7, 28.2, 28.8, 29.5,
             30.1, 30.7, 31.4, 32.0, 32.7,
             33.2, 33.9, 34.4, 35.0, 35.6,
             37.3, 39.6, 40.6, 40.9, 41.3,
             41.7 ]
    lons = [ 132.8, 132.2, 131.4, 130.8, 130.3,
             129.9, 129.8, 129.7, 129.6, 129.4,
             128.8, 128.2, 127.7, 127.3, 127.2,
             127.0, 126.9, 126.8, 126.8, 126.8,
             127.0, 127.1, 127.4, 127.7, 128.1,
             127.9, 127.8, 127.9, 128.2, 128.6,
             128.9, 129.3, 129.6, 130.2, 130.8,
             132.5, 134.8, 136.6, 138.3, 139.5, 
             140.2, ]

    dates = np.array(
            [ datetime( 2018, 6, 28,  0), 
              datetime( 2018, 6, 28,  6),
              datetime( 2018, 6, 28, 12),
              datetime( 2018, 6, 28, 18),
              datetime( 2018, 6, 29,  0),
              datetime( 2018, 6, 29,  6),
              datetime( 2018, 6, 29, 12),
              datetime( 2018, 6, 29, 18),
              datetime( 2018, 6, 30,  0),
              datetime( 2018, 6, 30,  6),
              datetime( 2018, 6, 30, 12),
              datetime( 2018, 6, 30, 18),
              datetime( 2018, 7,  1,  0),
              datetime( 2018, 7,  1,  3),
              datetime( 2018, 7,  1,  6),
              datetime( 2018, 7,  1,  9),
              datetime( 2018, 7,  1, 12),
              datetime( 2018, 7,  1, 15),
              datetime( 2018, 7,  1, 18),
              datetime( 2018, 7,  1, 21),
              datetime( 2018, 7,  2,  0),
              datetime( 2018, 7,  2,  3),
              datetime( 2018, 7,  2,  6),
              datetime( 2018, 7,  2,  9),
              datetime( 2018, 7,  2, 12),
              datetime( 2018, 7,  2, 15),
              datetime( 2018, 7,  2, 18),
              datetime( 2018, 7,  2, 21),
              datetime( 2018, 7,  3,  0),
              datetime( 2018, 7,  3,  3),
              datetime( 2018, 7,  3,  6),
              datetime( 2018, 7,  3,  9),
              datetime( 2018, 7,  3, 12),
              datetime( 2018, 7,  3, 15),
              datetime( 2018, 7,  3, 18),
              datetime( 2018, 7,  4,  0),
              datetime( 2018, 7,  4,  6),
              datetime( 2018, 7,  4, 12),
              datetime( 2018, 7,  4, 18),
              datetime( 2018, 7,  5,  0),
              datetime( 2018, 7,  5,  6),
            ] )

    dif = 999999999
    for i in range( len(dates) ):
       sec = np.abs( (dates[i] - time).total_seconds() )
       if sec < dif:
          dif = sec
       elif sec >= dif:
          break

    return( lons[i-1], lats[i-1], dates[i-1] )

def get_q1( INFO, stime=datetime(2018,7,1), vtime=datetime(2018,7,1), m=1, hpa=500 ):

    mem = str(m).zfill(4)
    if m == 0:
       mem = "mean"

    fn = os.path.join( INFO["TOP"], stime.strftime('%Y%m%d%H%M%S'), "fcst_sno_np00001",
                mem, "p_history.pe000000.nc" )

    ft_max = ( vtime - stime ).total_seconds()

    with Dataset( fn, "r", format="NETCDF4") as nc:
       
       prs = nc.variables["pressure"][:] # hPa
       idx_v = np.abs( ( prs - hpa ) ).argmin()

       fts = nc.variables["time"][:]
       idx_e = np.abs( ( fts - ft_max ) ).argmin()


       rho_ = nc.variables["DENSprs"][idx_e,idx_v,:,:]
       omega_ = -nc.variables["Wprs"][idx_e,idx_v,:,:] * rho_ * grav
       tk_ = nc.variables["Tprs"][idx_e,idx_v,:,:]
       u_ = nc.variables["Uprs"][idx_e,idx_v,:,:]
       v_ = nc.variables["Vprs"][idx_e,idx_v,:,:]

       [ dTdy_, dTdx_ ] = np.gradient( tk_, axis=(0,1) ) 

       dTdt_ = ( nc.variables["Tprs"][idx_e+1,idx_v,:,:] - nc.variables["Tprs"][idx_e-1,idx_v,:,:] ) / ( 12*3600.0 )
       sigma_ = Rd * tk_ /  ( cp*hpa*1.e2 ) - \
                ( nc.variables["Tprs"][idx_e,idx_v+1,:,:] - \
                  nc.variables["Tprs"][idx_e,idx_v-1,:,:] ) / \
                ( ( prs[idx_v+1] - prs[idx_v-1] )*1.e2 )

       q1 = cp * dTdt_ - cp * ( omega_ * sigma_ - u_ * dTdx_ * rDX - v_ * dTdy_ * rDX )
    return( q1 )

def def_cmap( nvar="RAIN", hpa=950 ):

    fac = 1.0
    extend = "max"
    cmap = plt.cm.get_cmap("jet")
    tvar = nvar
    if nvar == "RAIN":
       levs = np.arange( 10, 155, 5 )
       unit = "(mm/24h)"

    elif nvar == "Q1_vg":
       levs = np.arange( -100, 105, 5 )
       unit = "()"
       fac = 1.e6
       extend = "both"
       cmap = plt.cm.get_cmap("RdBu_r")

    elif nvar == "Q1":
       levs = np.arange( 10, 155, 5 )
       unit = "()"
       fac = 1.e2

    elif nvar == "OLR":
       cmap.set_under('gray',alpha=1.0)
       levs = np.arange( 80, 305, 5 )
#       cmap = plt.cm.get_cmap("Greys")
       unit = r'(W/m$^2$)'
       extend = "both"

    elif nvar == "MSLP":
       levs = np.arange( 0, 1400, 4)
       unit = "(hPa)"

    elif nvar == "Z":
       levs = np.arange( 0, 13000, 20 )
       unit = "(m)"
       tvar = nvar + str( hpa )

    elif nvar == "QV":
       cmap = plt.cm.get_cmap("BrBG")
       levs = np.arange( 0, 19.0, 1 )
       if hpa < 850:
          levs = np.arange( 0, 8.0, 0.5 )
       if hpa < 700:
          levs = np.arange( 0, 4.25, 0.25 )
          levs = np.arange( 0, 6.25, 0.25 )
       unit = r'(g/m$^3$)'
       fac = 1.e3
       tvar = nvar + str( hpa )

    elif nvar == "PW":
       levs = np.arange( 0, 72.5, 2.5)
       #cmap = plt.cm.get_cmap("Blues")
       cmap = plt.cm.get_cmap("hot_r")
       unit = r'(mm/m$^{2}$)'

    elif nvar == "THE" or nvar == "EPT":
       levs = np.arange( 280, 340, 2)
       unit = "(K)"
       cmap = plt.cm.get_cmap("jet")
       tvar = r'$\theta_e$' + str( hpa )

    elif nvar == "T":
       cmap = plt.cm.get_cmap("RdBu_r")
       levs = np.arange( 284, 297, 1 )
       unit = '(K)'
       extend = 'both'
       if hpa < 400:
          levs = np.arange( 238, 251, 1 )
       elif hpa < 600:
          levs = np.arange( 264, 275, 1 )
       tvar = nvar + str( hpa )

    elif nvar == "U":
       levs = np.arange( -36, 39, 3 )
       cmap = plt.cm.get_cmap("RdBu_r")
       extend = 'both'
       unit = '(m/s)'
       tvar = nvar + str( hpa )

    elif nvar == "V":
       levs = np.arange( -20, 22, 2 )
       cmap = plt.cm.get_cmap("RdBu_r")
       extend = 'both'
       unit = '(m/s)'
       tvar = nvar + str( hpa )

    elif nvar == "RH":
       cmap = plt.cm.get_cmap("BrBG")
       levs = np.arange( 10, 95, 5 )
       fac = 1.e2
       extend = 'both'
       unit = '(%)'
       tvar = nvar + str( hpa )

    return( cmap, levs, unit, extend, tvar, fac )

def read_etrack( stime=datetime(2018, 7, 1, 0),
                 ng=3,
                 dlon=2.0 ):
    opath = "dat/track"
    of = "track_s{0:}_ng{1:0=3}_dlon{2:}.npz".format( stime.strftime('%m%d'), int( ng ), dlon )

    print( of )
    data = np.load( os.path.join( opath, of ), allow_pickle=True )
    tclat_l = data['tclat_l']
    tclon_l = data['tclon_l']
    tcmslp_l = data['tcmslp_l']
    time_l = data['time_l']

    return( np.array( tclon_l ), np.array( tclat_l ), np.array( tcmslp_l ), 
            np.array( time_l ) )

def get_steering_flow( INFO, tclon=130.0, tclat=30.0, m=1, 
                       lon2d=np.zeros(1), lat2d=np.zeros(1), 
                       stime=datetime( 2018, 7, 5, 0 ),
                       vtime=datetime( 2018, 7, 5, 0 ), 
                       hpa_l = [ 850, 700, 500, ], # Velden and Leslie 1991WAF for weak TCs
                       tc_rad=5.0 ):

    dist = np.sqrt( np.square( lon2d - tclon ) + np.square( lat2d - tclat ) )

    j,i = np.unravel_index( np.argmin( dist ),  dist.shape  ) 


    u = 0.0
    v = 0.0

    for p, hpa in enumerate( hpa_l ):
        u_ = get_var( INFO, nvar="U", stime=stime, vtime=vtime, m=m+1, hpa=hpa )
        v_ = get_var( INFO, nvar="V", stime=stime, vtime=vtime, m=m+1, hpa=hpa )

        u_[ dist > tc_rad ] = np.nan
        v_[ dist > tc_rad ] = np.nan
        u += np.nanmean( u_ ) * hpa
        v += np.nanmean( v_ ) * hpa

    return( u/sum(hpa_l), v/sum(hpa_l) )

def get_rain_idx( INFO, slon=130.0, elon=137.5, slat=33.0, elat=36.0, 
                  adt_h=24, mmax=50, vtime_ref=datetime( 2018, 7, 6, 0 ),
                  stime=datetime( 2018, 7, 2, 0 ) ):

    lon2d, lat2d = get_lonlat( INFO, stime=datetime( 2018, 7, 1, 0 ) )

    adt = timedelta( hours=adt_h )
    
    rain_l = np.zeros( mmax )


    # get reference
    for m in range( mmax ):
        rain_ = get_var( INFO, nvar="RAIN", stime=stime, vtime=vtime_ref, m=m+1, adt=adt )
        rain_l[m] = np.mean( rain_[ (lon2d >= slon ) & (lon2d <= elon) & (lat2d >= slat) & (lat2d <= elat) ] )

    mem_l = np.argsort( rain_l )[::-1]
    rain_l = np.sort( rain_l )[::-1]

    return( rain_l, mem_l )

def get_olr( INFO, stime=datetime(2018,7,1), vtime=datetime(2018,7,1), m=1 ):

    mem = str(m).zfill(4)
    if m == 0:
       mem = "mean"

    fn = os.path.join( INFO["TOP"], stime.strftime('%Y%m%d%H%M%S'), "fcst_sno_np00001",
                mem, "p_history.pe000000.nc" )

    ft_max = ( vtime - stime ).total_seconds()

    with Dataset( fn, "r", format="NETCDF4") as nc:
#       print("time", fts/3600)

       try:
          fts = nc.variables["time"][:]
          idx_e = np.abs( ( fts - ft_max ) ).argmin()
          olr = nc.variables["OLR"][idx_e,:,:]
       except:
          print( "No time" )
          olr = nc.variables["OLR"][:,:]

    return( olr )
