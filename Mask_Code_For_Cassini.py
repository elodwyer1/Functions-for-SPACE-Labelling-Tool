# -*- coding: utf-8 -*-
"""
Created on Tue Jun 28 11:05:06 2022

@author: eliza
"""
import numpy
from tfcat import TFCat
from shapely.geometry import MultiPoint, Point, Polygon
from astropy.time import Time
import matplotlib.pyplot as pyplot
import matplotlib.colors as colors
import h5py
import numpy as np
from datetime import datetime
from os import path
import matplotlib.dates as mdates



def extract_data(time_view_start, time_view_end, file_data, val):
    
    time_view_start=datetime.fromisoformat(time_view_start)
    time_view_end=datetime.fromisoformat(time_view_end)
    
    #Read in data from file.
    file = h5py.File(file_data, 'r')
    
    #Convert from julian date to isostring format.
    t=Time(file.get('t'),format='jd').to_value('isot')
    #Convert to numpydatetime64 from isoformat.
    time = np.array(t, dtype=np.datetime64)
    #Restrict data to within time_view_start and time_view_end.
    time_view = time[(time >= time_view_start) & (time < time_view_end)]
    #convert restricted data back to isostring format for later use.
    time_iso = [i.item().strftime('%Y-%m-%dT%H:%M:%S') for i in time_view]
    
    #array for signal data.
    s=np.array(file.get(val))
    

    #Restrict data to within time_view_start and time_view_end. 
    s = s[:, (time >= time_view_start) & (time <= time_view_end)]
    
    #Load frequency data.
    frequency_tmp = np.array(file['f']).copy()

    # frequency_tmp is in log scale from f[0]=3.9548001 to f[24] = 349.6542
    # and then in linear scale above so it's needed to transfrom the frequency
    # table in a full log table and einterpolate the flux table (s --> flux
    frequency = 10**(np.arange(np.log10(frequency_tmp[0]), np.log10(frequency_tmp[-1]), (np.log10(max(frequency_tmp))-np.log10(min(frequency_tmp)))/399, dtype=float))
    flux = np.zeros((frequency.size, len(time_view)), dtype=float)

    for i in range(len(time_view)):
        flux[:, i] = np.interp(frequency, frequency_tmp, s[:, i])
    
    return time_iso, frequency, flux

def get_polygons(polygon_fp,start, end, type_):
    date_time = [start, end]
    #Convert start/stop times to unix from isoformat.
    unix_start, unix_end = Time(date_time,format='isot').to_value('unix')
    
    #array of polygons found within time interval specified.
    polygon_array=[]
    if path.exists(polygon_fp):
        catalogue = TFCat.from_file("C:/Users/eliza/Desktop/git_folder/ML_For_SKR_Code/selected_polygons/alllfes.json")
        for i in range(len(catalogue)):
                
                time_points=np.array(catalogue._data.features[i]['geometry']['coordinates'][0])[:,0]
                label=catalogue._data.features[i]['properties']['feature_type']
                if any(time_points >= unix_start) and any(time_points <= unix_end):
                    if label in type_:
                        polygon_array.append(catalogue._data.features[i]['geometry']['coordinates'][0])
    #polgyon array contains a list of the co-ordinates for each polygon within the time interval           
    return polygon_array
                   
def find_mask(time_view_start, time_view_end, val, file_data,polygon_fp,type_):
    #polgyon array contains a list of the co-ordinates for each polygon within the time interval
    polygon_array=get_polygons(polygon_fp, time_view_start, time_view_end, type_)
    
    #signal data and time frequency values within the time range specified.
    time_iso, frequency, flux=extract_data(time_view_start, time_view_end,file_data, val)
    #convert from isostring format to datetime64.
    times_datetime=np.array(time_iso, dtype=np.datetime64)
    #Also convert to unix.
    time_unix=Time(time_iso,format='isot').to_value('unix')
    #Meshgrid of time/frequency vals.
    times, freqs=np.meshgrid(time_unix, frequency)
    #Total length of 2D signal array.
    data_len = len(flux.flatten())
    #indices of each item in flattened 2D signal array.
    index = numpy.arange(data_len, dtype=int)
    #Co-ordinates of each item in 2D signal array.
    coords = [(t, f) for t,f in zip(times.flatten(), freqs.flatten())]
    data_points = MultiPoint([Point(x, y, z) for (x, y), z in zip(coords, index)])
    #Make mask array.
    mask = numpy.zeros((data_len,))
    
    #Find overlap between polygons and signal array.
    #Set points of overlap to 1.
    for i in polygon_array:
        
        fund_polygon = Polygon(i)
        fund_points = fund_polygon.intersection(data_points)
        mask[[int(geom.z) for geom in fund_points.geoms]] = 1
    mask = (mask == 0)

    #Set non-polygon values to zero in the signal array.
    v = numpy.ma.masked_array(flux, mask=mask)

    vmin = np.quantile(v[v > 0.], 0.05)
    vmax = np.quantile(v[v > 0.], 0.95)
    scaleZ = colors.LogNorm(vmin=vmin, vmax=vmax)
    fig, ax = pyplot.subplots()
    im=ax.pcolormesh(times_datetime,freqs, v,norm=scaleZ,cmap='binary',shading='auto')
    fontsize=10
    ax.set_xlabel('Time (UT)',fontsize=fontsize)
    ax.set_ylabel('Frequency (kHz)', fontsize=fontsize)
    ax.set_title(f'Cassini RPWS Data - {time_view_start} to {time_view_end}', fontsize=fontsize + 2)
    dateFmt = mdates.DateFormatter('%Y-%m-%d\n%H:%M')
    ax.xaxis.set_major_formatter(dateFmt)
    ax.set_yscale('log')
    cb=fig.colorbar(im, ax=ax)
   
    if val=='s':
        cbarlabel=r'Intensity (V$^2$/m$^2$/Hz)'
    elif val=='v':
        cbarlabel='Normalized Degree of'+'\n Circular Polarization'
        
    cb.set_label(cbarlabel, fontsize=fontsize)
    pyplot.show()
    
    return None

tmin = '2010-01-01'
tmax ='2010-01-05'
time_view_start=datetime.fromisoformat(tmin)
year=datetime.strftime(time_view_start,'%Y')
# read the save file and copy variables
file_data="C:/Users/eliza/Desktop/git_folder/ML_For_SKR_Code/input_data/SKR_{}_CJ.hdf5".format(year)
val='s'
polygon_fp="C:/Users/eliza/Desktop/git_folder/ML_For_SKR_Code/selected_polygons/alllfes.json"
type_=['LFE','LFE_m','LFE_sp','LFE_ext','LFE_sm']
masked_image=find_mask(tmin, tmax, val, file_data, polygon_fp,type_)

