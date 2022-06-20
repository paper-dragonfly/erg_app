def f(a,b):
    c = a+b
    return c

def g(first=4, second=2):
    c = first + second
    return c 

b = f(2,5)
print(b)

u = g(second=9,first=1)
print(u)

v= f(b=2, a=5)
print(v)

print(90*60)