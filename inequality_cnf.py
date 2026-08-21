# compare two lists and force them to be unequal

length = 4
list1 = [i+1 for i in range(length)]
list2 = [i+length+1 for i in range(length)]

aux_var = [i+length*2+1 for i in range(length)]

print(list1)
print(list2)
print(aux_var)

clauses = []
for (a, b, c) in zip(aux_var, list1, list2):
	clauses += [[-a,  b, -c,  0],
				[-a, -b,  c,  0],
				[ a,  b,  c,  0],
				[ a, -b, -c,  0]]