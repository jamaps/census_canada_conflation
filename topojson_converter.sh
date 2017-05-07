# converting between geojson and topojson

# more info:

# the translater scripts require topojson
# in order for faster computation and
# preserving topology of boundaries

# converts geojson to topojson
geo2topo 1991_ct_dbf.geojson > 1991_ct_dbf_topo.json

# converts topojson to geojson
topo2geo ct_96_og=ct_96_t.geojson < ct_96_og_topo_translatae.json
