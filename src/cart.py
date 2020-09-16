import numpy as np

from netCDF4 import Dataset
from datetime import datetime
from datetime import timedelta
import os
import sys


TOP = "/data_ballantine02/miyoshi-t/honda/SCALE-LETKF/BAIU2018_5.3.6"

stime = datetime( 2018, 6, 30, 0, 0, 0 )
vtime = datetime( 2018, 7, 6, 0, 0, 0 )

adt = timedelta( hours=24 )

m = 1

INFO = {"TOP": TOP, }


def get_lonlat( INFO, stime=datetime(2018,7,1), ):

    mem = str(1).zfill(4)

    fn = os.path.join( INFO["TOP"], stime.strftime('%Y%m%d%H%M%S'), "fcst_sno_np00001",
                mem, "p_history.pe000000.nc" )

    with Dataset( fn, "r", format="NETCDF4") as nc:
       lon = nc.variables["lon"][:]
       lat = nc.variables["lat"][:]
 
    return( lon, lat )

def get_arain( INFO, stime=datetime(2018,7,1), vtime=datetime(2018,7,1), 
               adt=timedelta(hours=24), m=1 ):

    mem = str(m).zfill(4)
    if m == 0:
       mem = "mean"

    fn = os.path.join( INFO["TOP"], stime.strftime('%Y%m%d%H%M%S'), "fcst_sno_np00001",
                mem, "p_history.pe000000.nc" )
    print( fn )

    ft_max = ( vtime - stime ).total_seconds()
    ft_min = ( vtime - adt - stime ).total_seconds()
    

    with Dataset( fn, "r", format="NETCDF4") as nc:
       fts = nc.variables["time"][:]
#       print("time", fts/3600)

       idx_s = np.abs( ( fts - ft_min ) ).argmin()
       idx_e = np.abs( ( fts - ft_max ) ).argmin()

       # 
       rain = np.sum( nc.variables["PREC"][idx_s+1:idx_e+1,:,:], axis=0 )*21600

    print( rain.shape )
#    print( ft_max, ft_min, idx_s, idx_e )
#    print( stime + timedelta( seconds=fts[idx_s+1]), 
#           stime + timedelta( seconds=fts[idx_e+1]) )
#    print( fts[idx_s:idx_e]/3600)
    return( rain )

rain = get_arain( INFO, stime=stime, vtime=vtime, adt=adt, m=1 )

lon2d, lat2d = get_lonlat( INFO, stime=stime )


import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import matplotlib.ticker as mticker
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
import cartopy.feature as cfeature

fig = plt.figure(figsize=(10, 10))

lons = 110
lone = 160
lats = 10
late = 55

#central_longitude = 135.0
#central_latitude = 35.0

#ax1 = fig.add_subplot(1,1,1, projection=ccrs.LambertConformal( central_longitude=central_longitude,
#                                                       central_latitude=central_latitude,
#                                                     ))
#ax1 = fig.add_subplot(1,1,1, projection=ccrs.Mercator( central_longitude=central_longitude,
#                                                        min_latitude=min_latitude,
#                                                       max_latitude=max_latitude,
#                                                       latitude_true_scale=latitude_true_scale,
#ax1 = plt.subplot(2, 2, 1, projection=ccrs.Mercator( central_longitude=180.0, ))
#ax1 = fig.add_subplot(1,1,1, projection=ccrs.PlateCarree(central_longitude=180))

ax1 = fig.add_subplot(1,1,1, projection=ccrs.PlateCarree(central_longitude=180))

ax1.set_extent( [lons, lone, lats, late ])

#ax1.coastlines() 
ax1.add_feature(cfeature.COASTLINE, linewidth=0.8)

dlon, dlat = 5, 5
#gl = ax1.gridlines(crs=ccrs.PlateCarree())
#gl.xlocator = mticker.FixedLocator(np.arange( lons, lone+dlon, dlon))
#gl.ylocator = mticker.FixedLocator(np.arange( lats, late+dlat, dlat))

xticks_lab = np.arange( lons, lone+dlon, dlon) 
yticks_lab = np.arange( lats, late+dlat, dlat) 

ax1.set_xticks(xticks_lab, crs=ccrs.PlateCarree()) 
ax1.set_yticks(yticks_lab, crs=ccrs.PlateCarree())

gl = ax1.gridlines( crs=ccrs.PlateCarree(), \
                    linewidth=0.5, linestyle='--', color='k', alpha=0.8)

ax1.xaxis.set_major_formatter(LongitudeFormatter(zero_direction_label=True))
ax1.yaxis.set_major_formatter(LatitudeFormatter())

SHADE = ax1.contourf( lon2d, lat2d, rain, 
                      transform=ccrs.PlateCarree(), )

#ax1.set_xlimit( lons, lone )
#ax1.set_ylimit( lats, late )

plt.show()

sys.exit()

fig, ((ax1)) = plt.subplots(1, 1, figsize=( 8,7.))
fig.subplots_adjust( left=0.04, bottom=0.04, right=0.92, top=0.91,
                     wspace=0.15, hspace=0.3)


plt.show()

