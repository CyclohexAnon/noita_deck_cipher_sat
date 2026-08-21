import numpy as np

# given some value k, encode it as binary and add restrictions such that it can only be 0-k
# NOTE: This means that there are k+1 possible values allowed!!
# i.e. if we want a 26 card deck, we need to set it to 25

value = 26

bits = int(np.ceil(np.log2(value+1)))

array = [i+1 for i in range(bits)]

# we want to only allow numbers 0-k, so k+1 until 2^bits-1 is forbidden
# we can be more efficient by excluding the prefixes

binary_exclusion_str_rev = bin(2**bits - 1 - value)[2:][::-1]

clauses = []
for i, c in enumerate(binary_exclusion_str_rev):
	if c == "1":
		#print(f"disallow ({bits - i = }) of value ({value + 2**i = })")
		disallowed_bits_str = bin(value + 2**i)[2:2+bits-i]
		temp = []
		for j, v in enumerate(disallowed_bits_str):
			temp += [-(int(v)*2-1) * array[j]]
		clauses += [temp + [0]]

print(clauses)

# checking function, remove later
for i in range(2**bits):
	binary_reprensation = bin(i)[2:].rjust(bits, "0")
	temp = []
	for j, c in enumerate(binary_reprensation):
		temp += [(int(c)*2-1)*(j+1)]
	#print(temp)
	passes_all = True
	for clause in clauses:
		passes = False
		for (a, b) in zip(clause[:-1], temp):
			#print(a, b)
			if a == b: passes = True; break
		if not passes: passes_all = False
	#print(passes_all)
	#print("---")

	print(f"{i}: {passes_all}")