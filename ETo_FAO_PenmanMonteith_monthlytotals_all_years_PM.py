# -*- coding: utf-8 -*-
import netCDF4 
import numpy as np
import matplotlib.pyplot as plt
#solution to avoid Basemap and PROJ_LIB errors due to environment problems
#at home
import os 
os.environ['PROJ_LIB'] = r'C:/Users/flavi/Anaconda3/pkgs/proj4-5.2.0-ha925a31_1/Library/share/'
from mpl_toolkits.basemap import Basemap
from matplotlib import rcParams
rcParams['mathtext.default'] = 'regular'
import pyeto
from pyeto import fao
from pyeto import fao56_penman_monteith
import math

"script using Daymet data to calculate Penman_Monteith reference ET"
"this script calculates mean monthly ETo from 1980 to 2019"
 
#: Solar constant [ MJ m-2 min-1]
SOLAR_CONSTANT = 0.0820

# Stefan Boltzmann constant [MJ K-4 m-2 day-1]
STEFAN_BOLTZMANN_CONSTANT = 0.000000004903

#calculate yearly, monthly and season climatology by using looping and strings
#define the strings
#years = ['1980', '1981', '1982', '1983', '1984', '1985', '1986', '1987', '1988', '1989', '1990', '1991', '1992', '1993', '1994', '1995', '1996', '1997', '1998', '1999', '2000', '2001', '2002', '2003', '2004', '2005', '2006', '2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019']
years = ['1980', '1981', '1982']

#Create an array filled with zeros that is the same shape as the data in the netCDFs
#This is what we'll add each day's ET to
#import Daymet Data
nc_path1 = ('C:/Users/flavi/OneDrive - University of Georgia/2017_Summer_PR/data/rad/daymet_v3_srad_'+years[0]+'_puertorico.nc4')
ds = netCDF4.Dataset(nc_path1, mode='r')
#create X arrays with the same shape as the data to fill with the new values
sum_ETo = np.zeros((36, ds['srad'][0,:,:].shape[0], ds['srad'][0,:,:].shape[1]))
ETo_times = np.zeros((36))
ds.close()
#i = 0

#order the loop to go through years > month > day
for year in years:
    
#Using the incoming shortwave radiation to estimate the daily net radiation
    nc_path1 = ('C:/Users/flavi/OneDrive - University of Georgia/2017_Summer_PR/data/rad/daymet_v3_srad_'+year+'_puertorico.nc4')
    ds = netCDF4.Dataset(nc_path1, mode='r')
    srad='srad'
    srad_units = ds.variables['srad'].units
    
    #Using tmax to estimate net outgoing longwave radiation
    nc_path = ('C:/Users/flavi/OneDrive - University of Georgia/2017_Summer_PR/data/tmax/daymet_v3_tmax_'+year+'_puertorico.nc4')
    ds1 = netCDF4.Dataset(nc_path, mode='r')
    tmx='tmax'
    tmax_units = ds1.variables['tmax'].units
    
    #Using tmin to estimate net outgoing longwave radiation
    nc_path2 = ('C:/Users/flavi/OneDrive - University of Georgia/2017_Summer_PR/data/tmin/daymet_v3_tmin_'+year+'_puertorico.nc4')
    ds2 = netCDF4.Dataset(nc_path2, mode='r')
    tmn='tmin'
    tmin_units = ds2.variables['tmin'].units
    
    #Using daily average vapor pressure to represent the Actual vapour pressure in the eq of 'no_lw_rad'
    nc_path3 = ('C:/Users/flavi/OneDrive - University of Georgia/2017_Summer_PR/data/vap/daymet_v3_vp_'+year+'_puertorico.nc4')
    ds3 = netCDF4.Dataset(nc_path3, mode='r')
    lons = ds3.variables['lon'][:]
    lats = ds3.variables['lat'][:]
    vap='vp'
    #Save list of times in file so that we can loop through them
    time = ds3.variables['time'][:]
    vap_units = ds3.variables['vp'].units

    #define the starting month
    start_mt = 1 

    #FAO Method to calculate ET
    #Loop through a list from 0-365 based on the times we saved earlier
    for t in range(len(time)):
        #Convert the integer in the time list to the day of the year
        dt = netCDF4.num2date(time[t],'days since 1980-01-01 00:00:00','standard')
        yr = dt.year
        mt = dt.month
        dy = dt.day 
        
        #monthly loop
        for m in range(1,13): 
            if m == mt:
                ETo_times[(yr-1980)*12+mt-1] = time[t]
                # t_ind_new = np.where(time == (t+0.5))
                t_ind_new = np.where(time == time[t])
                t_ind_new = np.max(t_ind_new)

        
                print (mt, t)                                 
            
            #For each timestep in the file, pull out Tmax and Tmin from that position
                tmax_data = ds1.variables['tmax'][t][:,:] 
                tmin_data = ds2.variables['tmin'][t][:,:]
                srad_data = ds.variables['srad'][t][:][:]
                vap_data = ds3.variables['vp'][t][:][:]
            
                #Calculate mean temp in Celsius
                daily_mean_t= (tmax_data + tmin_data)/2
            
            #to estimate et_rad
            #estimating clear sky radiation for the eq of logwave rad = 'no_lw_rad' (altitude and et_rad)
                altitude = 1065 #in meters from the peak of El Younque 
                import datetime
                lat = pyeto.deg2rad(18.2813432)  # Convert latitude to radians   
                day_of_year = datetime.date(yr, mt, dy).timetuple().tm_yday #convert day in julian days
                sol_dec = pyeto.sol_dec(day_of_year)            # Solar declination
                sha = pyeto.sunset_hour_angle(lat, sol_dec)
                ird = pyeto.inv_rel_dist_earth_sun(day_of_year)
                et_rad = pyeto.et_rad(lat, sol_dec, sha, ird)   # Extraterrestrial radiation (top of the atmosphere radiation)
            #clear sky radiation
                cs_rad = fao.cs_rad(altitude, et_rad)
            
            #Using daily average vapor pressure to represent the Actual vapour pressure in the eq of 'no_lw_rad'
                avp = vap_data * 0.0010 #converting vapor pressure from Pa to KPa
        
            #Calculating varible 'net_rad' = daily net radiation
            #First = shortwave rad
                sol_rad = (srad_data * 3.6)/(10**3) #converting the shortwave rad from W m-2 to MJ m-2
        
            #Using tmin and tmax to estimate net outgoing longwave radiation
            #converting C in Kelvin
                tmax = tmax_data + 273.15
                tmin = tmin_data + 273.15
        
             #Copying the equation from the package = fao.net_out_lw_rad(tmin_data, tmax_data, sol_rad, cs_rad, avp)  = estimating net outgoing longwave radiation
                tmp1 = (STEFAN_BOLTZMANN_CONSTANT*((np.power(tmax, 4) + np.power(tmin, 4)) / 2.))
                tmp2 = (0.34 - (0.14 * avp**0.5))
                tmp3 = 1.35 * (sol_rad / cs_rad) - 0.35
                no_lw_rad = tmp1 * tmp2 * tmp3
             
            #finally calculating the daily net radiation at the crop surface, assuming a grass reference crop
                ni_sw_rad = sol_rad
                net_rad = fao.net_rad(ni_sw_rad, no_lw_rad)
        
            #calculating variable 't' = Air temperature at 2 m height in Kelvin
                daily_mean_tk= (tmax + tmin)/2
                t = daily_mean_tk
        
            #estimating variable 'ws' = Wind speed at 2 m height [m s-1]
                ws = 3.7
        
            # estimating variable 'svp' = Saturation vapour pressure [kPa] from temp
                t2 = daily_mean_t #mean daily temp in Celsius
        
                svp = 0.6108 * np.exp((17.27 * t2) / (t2 + 237.3))
        
            #estimating 'delta_svp' = Slope of saturation vapour pressure curve [kPa degC-1]
                tmp = 4098 * (0.6108 * np.exp((17.27 * t2) / (t2 + 237.3)))
                delta_svp = tmp / np.power((t2 + 237.3), 2)
        
            #calculating variable 'psy' = Psychrometric constant [kPa deg C]
                atmos_pres = fao.atm_pressure(altitude) #Estimate atmospheric pressure from the altitude of El Younque
                psy = fao.psy_const(atmos_pres)
        
            # estimating variable shf = Soil heat flux (G) [MJ m-2 day-1] 
            #shf: Soil heat flux (G) [MJ m-2 day-1] (default is 0.0, which is reasonable for a daily or 10-day time steps). 
            #For monthly time steps *shf* can be estimated using ``monthly_soil_heat_flux()`` or ``monthly_soil_heat_flux2()``.
            #Estimate monthly soil heat flux (Gmonth) from the mean air temperature of the previous and next month, assuming a grass crop.
            #shf = fao.monthly_soil_heat_flux(t_month_prev, t_month_next) #Mean air temperature of the previous and next month in Celsius
                shf = 0.0
        
            #FAO_Penman Method to calculate ET
                ETo = pyeto.fao56_penman_monteith(net_rad, t, ws, svp, avp, delta_svp, psy, shf) 
                #Eto_avg = ETo/37
        
            #Add the daily ETo to our running total for the month
                sum_ETo[(yr-1980)*12+mt-1,:,:] = sum_ETo[(yr-1980)*12+mt-1,:,:] + ETo
                #sum_ETo = sum_ETo + ETo
                

print ('Writing to netCDF...')
wrfgdi_out = netCDF4.Dataset('C:/Users/flavi/OneDrive - University of Georgia/20-21_NOAA_RA/NOAA_RA/ET_'+str(yr)+'-{0:0>2d}'.format(mt)+'.nc', mode='w', format='NETCDF4_CLASSIC')

lat = wrfgdi_out.createDimension('lat', lats.shape[0])
lon = wrfgdi_out.createDimension('lon', lons.shape[0])
time_dim = wrfgdi_out.createDimension('time', None)

# Create coordinate variables for 4-dimensions
times_var = wrfgdi_out.createVariable('time', np.float64, ('time',))
latitudes = wrfgdi_out.createVariable('latitude', np.float32, ('lat',))
longitudes = wrfgdi_out.createVariable('longitude', np.float32, ('lon',))
# Create the actual 3-d variable
tot_ET_var = wrfgdi_out.createVariable('TOT_ET', np.float32, ('time','lat','lon'))

# Variable Attributes
latitudes.units = 'degree_north'
longitudes.units = 'degree_east'
tot_ET_var.units = 'mm'
times_var.units = 'days since 1980-01-01 00:00:00'
times_var.calendar = 'standard'

latitudes[:] = lats
longitudes[:] = lons
times_var[:] = ETo_times
tot_ET_var[:,:,:] = sum_ETo[:,:,:]


wrfgdi_out.close()


ds.close()
ds2.close()
