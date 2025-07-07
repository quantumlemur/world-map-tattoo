import dataclasses
import datetime
import pathlib
import tempfile
from typing import List, Optional

import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.feature import ShapelyFeature
import cartopy.io.shapereader as shpreader
from matplotlib import gridspec
import matplotlib.pyplot as plt
from mpl_toolkits import basemap
import numpy as np
import pandas
import shapely.geometry as sgeom


@dataclasses.dataclass
class Inset:
    countries: List[str]
    map_extent: List[float]  # lon_min, lon_max, lat_min, lat_max
    placement_x_extent: List[float]  # x_min, x_max
    placement_y_extent: List[float]  # y_min, y_max


insets = [
    Inset(
        countries=['Greenland', 'Iceland'],
        map_extent=[-75, -5, 55, 85],  # lon_min, lon_max, lat_min, lat_max
        placement_x_extent=[0.33, 0.45],  # x_min, x_max
        placement_y_extent=[0.85, 1.05],  # y_min, y_max
    ),
    Inset(
        countries=['Antarctica'],
        map_extent=[-180, 180, -90, -65],  # lon_min, lon_max, lat_min, lat_max
        placement_x_extent=[0.35, 0.7],  # x_min, x_max
        placement_y_extent=[0, 0.2],  # y_min, y_max
    ),
    Inset(
        countries=['New Zealand'],
        map_extent=[163, 180, -49, -32],  # lon_min, lon_max, lat_min, lat_max
        placement_x_extent=[0.93, 1],  # x_min, x_max
        placement_y_extent=[0.13, 0.3],  # y_min, y_max
    ),
]

# fig, ax = plt.subplots(figsize=(10, 10))  # main map

fig = plt.figure(figsize=(10, 6))

ax = fig.add_subplot(
    1, 1, 1, projection=ccrs.InterruptedGoodeHomolosine(emphasis='land')
)

# Load Natural Earth shapefile for countries
shapename = 'admin_0_countries'
countries_shp = shpreader.natural_earth(
    resolution='110m', category='cultural', name=shapename
)
reader = shpreader.Reader(countries_shp)

# Filter features
inset_countries = []
for inset in insets:
    inset_countries.extend(inset.countries)
print(inset_countries)
filtered_geoms = [
    country.geometry
    for country in reader.records()
    if country.attributes['NAME'] not in inset_countries
]
# Create and add the feature for selected countries
selected_feature = ShapelyFeature(
    filtered_geoms,
    ccrs.PlateCarree(),
    edgecolor='black',
    facecolor='none',
    # linewidth=1.5,
)
print(selected_feature)
ax.add_feature(selected_feature)

# Set the extent of the map (optional, but can be useful for specific regions)
# ax.set_extent([-180, 180, -65, 75], crs=ccrs.PlateCarree())
ax.spines['geo'].set_visible(False)


for inset in insets:
    dimensions = [
        inset.placement_x_extent[0],
        inset.placement_y_extent[0],
        inset.placement_x_extent[1] - inset.placement_x_extent[0],
        inset.placement_y_extent[1] - inset.placement_y_extent[0],
    ]
    central_longitude = (inset.map_extent[1] + inset.map_extent[0]) / 3
    print(central_longitude)
    ax_inset = ax.inset_axes(
        dimensions, projection=ccrs.Aitoff(central_longitude=central_longitude)
    )  # type:ignore
    ax_inset.set_extent(
        inset.map_extent, crs=ccrs.PlateCarree()
    )  # lon_min, lon_max, lat_min, lat_max

    # Filter features
    filtered_geoms = [
        country.geometry
        for country in reader.records()
        if country.attributes['NAME'] in inset.countries
    ]

    # Create and add the feature for selected countries
    selected_feature = ShapelyFeature(
        filtered_geoms,
        ccrs.PlateCarree(),
        edgecolor='black',
        facecolor='none',
        # linewidth=1.5,
    )
    ax_inset.add_feature(selected_feature)

    # Transparent background
    ax_inset.set_facecolor('none')

    # Remove inset borders
    for key in ax_inset.spines.keys():
        ax_inset.spines[key].set_visible(False)


plt.tight_layout()
plt.savefig('plot.png')
