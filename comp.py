with open('c:/foraconveni2018.txt') as f:
    lines2018 = f.readlines()
with open('c:/foraconveni2019.txt') as g:
    lines2019 = g.readlines()

baixes=[]
altes=[]
for a in lines2018:
    if not a in lines2019:
        baixes.append(a)
for b in lines2019:
    if not b in lines2018:
        altes.append(b)

with open('baixesfora.txt', 'w') as f:
    for item in baixes:
        f.write("%s\n" % item)
with open('altesfora.txt', 'w') as f:
    for item in altes:
        f.write("%s\n" % item)


