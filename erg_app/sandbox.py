d = {'a':"" , 'b': 2}
print(d)
d2 = {}
for key in d:
    if d[key] != "":
        d2[key] = d[key]

print(d2)

print(len(d))