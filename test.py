def bige2lite(a:int)->str:
    tmp = "%0.16x"%a
    res = ''
    for i in range(0, 16, 2):
        res += tmp[14 - i:16 - i]
    return res

print(bige2lite(123456789))