import random
winNum = [2, 4, 6, 8, 11, 13, 19, 20]
initState = [0, 0, 0, 2, 4, 7, 8, 0, 13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
minlost = 10
maxlost = 50

is_checked = 0

betnumber = random.randint(30, 40)
for i in range(maxlost, minlost - 1, -1):
   
    if is_checked == 1:
        break
    for j in range(20):
        if i == initState[j]:
            betnumber = j + 1
            is_checked = 1

print (betnumber)

