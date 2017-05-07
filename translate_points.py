# translates points in census block-face files based on a set of control points

import csv
import sys
from math import sqrt

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


# grab array of all points that need to be translated
in_points = []
with open("my_91_points.csv") as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        if row != ['x', 'y', 'ctuid', 'pop', 'pt_type']:
            # if row[2][:3] == '933':
            in_points.append(row)


# loop through translating
# will probably have to call the function by cma eventually!
out_points = [["xi","yi","ctuid","pop","pt_type","xg","yg"]]

# go through each and translate!
for row in in_points:
    out_row = translater(row,ref_points,-2)
    xg = out_row[0]
    yg = out_row[1]
    p_total = out_row[2]
    # fail if probability is lower or higher than these thresholds
    if p_total < 0.999 or p_total > 1.001:
        sys.exit("FAIL")

    # append it!
    out_points.append(row + [xg,yg])

    # maybe do some printing?
    # print "===================================="

# output to a file
with open("my_points_91_moved.csv", 'w') as csvfile:
    writer = csv.writer(csvfile)
    for row in out_points:
        writer.writerow(row)
