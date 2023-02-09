# Vessel_Proximity_Analysis
 Vessel proximity/interactions for port and coastal scales.

 - Initial commit 06FEB2023.

    Vessel proximity analysis for coastal and port scales, with attributes enumerating vessel interactions (meeting, crossing, overtaking).

    ## Coastal

    The coastal analysis determines vessel proximities at 20 min. intervals, at 0-.5nm, .5-1nm, 1-2nm, 2-3nm, 3-12nm.

    Three scales of data are available as an output: the maximum number of vessels seen in a single day, the highest monthly average, and the annual average.

    (The monthly average does not compute within a single month for the entire output. Instead, it computes the highest monthly average at each point and logs what month it was observed. Monthly output does not include interaction breakdowns.)

    ## Port

    The port analysis is very similar to the coastal. The port analysis is at a higher resolution, only caputres w/i 250meters, and enumerates interactions based on vessel types (or exclusions of vessel types).