# translate boundary files encoded in topojson objects

import json
import csv
import sys
from math import sqrt
from subprocess import call

# input
in_topojson = '1991/1991_ct_dbf_topo.json'
# output
out_topojson = '1991/1991_ct_dbf_translate_tooo.json'


# function for doing the translate stuff
# inputs the row to be moved, the ref points, and a beta for defining the moving window
def translater(in_point_row,ref_point_list,beta):
    # lets say beta = b
    b = beta
    # input point initial coordinates xi and yi
    xi = float(in_point_row[0])
    yi = float(in_point_row[1])

    # finding the distance to each ref point
    d_list = []
    for pt in ref_point_list:
        # compute euclidean distance from xi yi to coords
        d = sqrt((xi - float(pt[2]))**2 + (yi - float(pt[3]))**2)
        # append back to ref point list at i[6]
        d_list.append(pt + [d])


    # compute probabilities via distance decay
    probs = []
    p_total = 0
    db_sum = 0
    for d in d_list:
        db_sum += d[6] ** b
    for d in d_list:
        p = (d[6] ** b) / db_sum
        p_total = p_total + p
        probs.append(d + [p])

    dx = 0
    dy = 0
    for p in probs:
        dx = dx + p[7] * p[4]
        dy = dy + p[7] * p[5]

    xg = xi + dx
    yg = yi + dy

    return xg, yg, p_total
    # sum of all probs should = 1


# grab list of all the ref points
ref_points = []
with open("control_points.csv") as csvfile:
    reader = csv.DictReader(csvfile)
    tid = 0
    for row in reader:
        tid += 1 # unique ID
        xi = float(row["xi"])
        yi = float(row["yi"])
        dx = float(row["xg"]) - float(row["xi"])
        dy = float(row["yg"]) - float(row["yi"])
        cma = row['cma']
        # append [id,cma, xi, yi, dx, dy]
        ref_points.append([tid,cma,xi,yi,dx,dy])




# loading the topojson file
with open(in_topojson) as json_data:
    d = json.load(json_data)


# d['arcs'] is a big dirty lists of line strings
arc_array = d["arcs"]
print len(d["arcs"])

# so ill have to run through each line string, translating each point in the string via my translate function

new_arc_array = []
c = 0
for arc in arc_array:
    new_arc = []
    for point in arc:


        # translate
        print point
        np = translater(point,ref_points,-2)
        if np[2] < 0.999 or np[2] > 1.001:
            sys.exit("FAIL")

        c += 1


        new_arc.append([np[0],np[1]])


    new_arc_array.append(new_arc)


print len(arc_array)
print len(new_arc_array)
if len(new_arc_array) != len(arc_array):
    sys.exit("FAIL")


new_topojson = {
    "type": "Topology",
    "bbox": d['bbox'],
    "objects": d['objects'],
    "arcs": new_arc_array
}

with open(out_topojson, 'w') as outfile:
    json.dump(new_topojson, outfile)



# call(["topo2geo", "96_vancity=96_vancity_translate.geojson", "<", "96_vancity_topo_translate.json"])

print c
