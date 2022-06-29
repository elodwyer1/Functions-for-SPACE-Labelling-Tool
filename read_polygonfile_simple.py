# -*- coding: utf-8 -*-
"""
Created on Mon Apr 11 09:04:20 2022

@author: eliza
"""

import pandas as pd
import numpy as np
from datetime import datetime
from tfcat import TFCat

def get_data(file):
    co = []
    id_ = []
    feature=[]
    catalogue = TFCat.from_file(file)
    for i in range(len(catalogue)):
        label=catalogue._data.features[i]['properties']['feature_type']
        feature.append(label)
        id_.append(catalogue._data.features[i]['id'])
        coords=np.array(catalogue._data.features[i]['geometry']['coordinates'][0])
        co.append(coords)
        
    return co, id_, feature

def lfe_coordinates(file):
    co, id_, feature = get_data(file)
    timestamps = []
    freqs = []
    for i in range(len(co)):
        time_points=co[i][:,0]
        f_points=co[i][:,1]
        timestamps.append([datetime.utcfromtimestamp(i) for i in time_points])
        freqs.append(f_points)
    return timestamps, freqs, feature, id_

def make_dataframe(file):
    #Timestamps is in the form of pandas timestamp, but you can edit the lfe_coordinates function
    #if you would like it in a different format.
    timestamps, freqs, feature, id_ = lfe_coordinates(file)
    
    
    #Start and end times of each labelled item.
    start = [min(i) for i in timestamps]
    end = [max(i) for i in timestamps]
    
    df = pd.DataFrame({'start': start, 'end':end,'label':feature,'id':id_})
    df=df.sort_values(by='start').reset_index(drop=True)
    

    return df

file="C:/Users/eliza/Desktop/git_folder/ML_For_SKR_Code/selected_polygons/alllfes.json"
df=make_dataframe(file)
