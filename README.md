# Functions-for-SPACE-Labelling-Tool
## Mask_Code_For_Cassini.py
Code that will plot the Cassini RPWS data, with a binary mask showing only the data within the labelled polygons in a .json file.


### Usage instructions:
- call the function **find_mask**
  - The function takes parameters:
      - time_view_start (start of the time duration you'd like to plot in isostring format).
      - time_view_end (end of the time duration you'd like to plot in isostring format).
      - val (parameter you'd like to plot, e.g 's' for flux density and 'v' for degree of normalised degree of circular polarisation).
      - file_data (path to the file containing the Cassini RPWS file, in .hdf5 format with time in julian day, frequency in kHz).
      - polygon_fp (path to .json file with polygons).
      - type_ (type of feature you'd like to plot, e.g the feature name from polygon file.
      
### Example of use.
time_view_start = '2006-01-01' <br />
time_view_end ='2006-01-05' <br />
val='s' <br />
file_data="C:/Users/eliza/Desktop/git_folder/ML_For_SKR_Code/input_data/SKR_2006_CJ.hdf5" <br />
polygon_fp="C:/Users/eliza/Desktop/git_folder/ML_For_SKR_Code/selected_polygons/alllfes.json" <br />
type_=['LFE','LFE_m','LFE_sp','LFE_ext','LFE_sm'] <br />
masked_image=find_mask(tmin, tmax, val, file_data, polygon_fp,type_) <br />

The code above will plot this image:
![example](https://user-images.githubusercontent.com/93202824/176448563-cd9ef588-a812-4e2f-9078-55b9c6305847.png)

## read_polygonfile.py
### Usage instructions:
#### lfe_coordinates
Function to return the time co-ordinates (datetime object in UTC) frequency co-ordinates (in kHz) of features in the polygon file, as well as their feature name and id.
Input is the polygon file in .json format.

#### make_dataframe
Function that returns a dataframe with start and end times of items in the polygon file, as well as their feature type and id.
Input is the polygon file in .json format.

### Example of use.
#### Example of lfe_coordinates
file="C:/Users/eliza/Desktop/git_folder/ML_For_SKR_Code/selected_polygons/alllfes.json" <br />
timestamps, freqs, feature, id_ = lfe_coordinates(file)
    
#### Example of make_dataframe
file="C:/Users/eliza/Desktop/git_folder/ML_For_SKR_Code/selected_polygons/alllfes.json" <br />
df=make_dataframe(file)
