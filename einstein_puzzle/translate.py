import itertools
import sys

output_file = "../input/einstein.cnf" #str(sys.argv)[1]
f = open(output_file, "w")

f.write('p cnf 125 1823\n')

# Impose constraints, eg. at least one man drinks beer
for i in range(25):
    for j in range(5):
        f.write(str(i*5+j+1) + ' ')
    f.write('0\n')

# Impose constraints, eg. at most one man drinks beer
for i in range(25):
    for j in range(1, 6):
        for k in range(j+1, 6):
            f.write(str(-(i*5+j))+ ' ' + str(-(i*5+k)) + ' ')
            f.write('0\n')

# Impose constraints, eg. a man drinks at most one beverage
for i in range(5):
    for j in range(5):
        for r in range(0, 5):
            for k in range(1, 5-j):
                f.write(str(-(i*25+1+j*5+r)) + ' ' + str(-(i*25+1+j*5+r+k*5)) + ' ')
                f.write('0\n')

## nat: Brit, house: red
# DNF: (1 and 26) or (2 and 27) or (3 and 28) or (4 and 29) or (5 and 30)
a = [[1, 26], [2, 27], [3, 28], [4, 29], [5, 30]]
for clause in list(itertools.product(*a)):
    for prop in clause:
        f.write(str(prop) + ' ')
    f.write('0\n')

## nat: Swede, pet: dog
# DNF: (31 and 101) or (32 and 102) or (33 and 103) or (34 and 104) or (35 and 105)
a = [[31, 101], [32, 102], [33, 103], [34, 104], [35, 105]]
for clause in list(itertools.product(*a)):
    for prop in clause:
        f.write(str(prop) + ' ')
    f.write('0\n')

# house: green, pos: left of, house: white
# DNF: (6 and 12) or (7 and 13) or (8 and 14) or (9 and 15)
a = [[6, 12], [7, 13], [8, 14], [9, 15]]
for clause in list(itertools.product(*a)):
    for prop in set(clause):
        f.write(str(prop) + ' ')
    f.write('0\n')

## nat: Dane, bev: tea (not pos1/pos3)
# DNF: (36 and 76) or (37 and 77) or (38 and 78) or (39 and 79) or (40 and 80)
a = [[36, 76], [37, 77], [38, 78], [39, 79], [40, 80]]
for clause in list(itertools.product(*a)):
    for prop in clause:
        f.write(str(prop) + ' ')
    f.write('0\n')

## house: green, bev: coffee
# DNF: (6 and 81) or (7 and 82) or (8 and 83) or (9 and 84) or (10 and 85)
a = [[6, 81], [7, 82], [8, 83], [9, 84], [10, 85]]
for clause in list(itertools.product(*a)):
    for prop in clause:
        f.write(str(prop) + ' ')
    f.write('0\n')

## cig: Pall Mall, pet: birds
# DNF: (51 and 106) or (52 and 107) or (53 and 108) or (54 and 109) or (55 and 110)
a = [[51, 106], [52, 107], [53, 108], [54, 109], [55, 110]]
for clause in list(itertools.product(*a)):
    for prop in clause:
        f.write(str(prop) + ' ')
    f.write('0\n')

## house: yellow, cig: Dunhill
# DNF: (16 and 66) or (17 and 67) or (18 and 68) or (19 and 69) or (20 and 70)
a = [[16, 66], [17, 67], [18, 68], [19, 69], [20, 70]]
for clause in list(itertools.product(*a)):
    for prop in clause:
        f.write(str(prop) + ' ')
    f.write('0\n')

## pos: pos3, bev: milk
# DNF: (88)
f.write("88 0\n")

## nat: Norwegian, pos: pos1
# DNF: (41)
f.write("41 0\n")

## cig: Blends, pos: next to, pet: cats
# DNF: (56 and 112) or (57 and 111) or (57 and 113) or (58 and 112) or (58 and 114) or
# (59 and 113) or (59 and 115) or (60 and 114)
a = [[56, 112], [57, 111], [57, 113], [58, 112], [58, 114], [59, 113], [59, 115], [60, 114]]
for clause in list(itertools.product(*a)):
    for prop in set(clause):
        f.write(str(prop) + ' ')
    f.write('0\n')

## pet: horse, pos: next to, cig: Dunhill
# DNF: (66 and 117) or (67 and 116) or (67 and 118) or (68 and 117) or (68 and 119) or
# (69 and 118) or (69 and 120) or (70 and 119)
a = [[66, 117], [67, 116], [67, 118], [68, 117], [68, 119], [69, 118], [69, 120], [70, 119]]
for clause in list(itertools.product(*a)):
    for prop in set(clause):
        f.write(str(prop) + ' ')
    f.write('0\n')

## cig: Bluemasters, bev: beer
# DNF: (71 and 91) or (72 and 92) or (73 and 93) or (74 and 94) or (75 and 95)
a = [[71, 91], [72, 92], [73, 93], [74, 94], [75, 95]]
for clause in list(itertools.product(*a)):
    for prop in clause:
        f.write(str(prop) + ' ')
    f.write('0\n')

## nat: German, cig: Prince
# DNF: (46 and 61) or (47 and 62) or (48 and 63) or (49 and 64) or (50 and 65)
a = [[46, 61], [47, 62], [48, 63], [49, 64], [50, 65]]
for clause in list(itertools.product(*a)):
    for prop in clause:
        f.write(str(prop) + ' ')
    f.write('0\n')

## nat: Norwegian, pos: next to, house: blue
# DNF: (21 and 42) or (22 and 41) or (22 and 43) or (23 and 42) or (23 and 44) or
# (24 and 43) or (24 and 45) or (25 and 44)
a = [[21, 42], [22, 41], [22, 43], [23, 42], [23, 44], [24, 43], [24, 45], [25, 44]]
for clause in set(itertools.product(*a)):
    for prop in clause:
        f.write(str(prop) + ' ')
    f.write('0\n')

## cig: Blends, pos: next to, bev: water
# DNF: (56 and 97) or (57 and 96) or (57 and 98) or (58 and 97) or (58 and 99) or
# (59 and 98) or (59 and 100) or (60 and 99)
a = [[56, 97], [57, 96], [57, 98], [58, 97], [58, 99], [59, 98], [59, 100], [60, 99]]
for clause in set(itertools.product(*a)):
    for prop in set(clause):
        f.write(str(prop) + ' ')
    f.write('0\n')

f.close()
