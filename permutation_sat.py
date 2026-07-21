import subprocess
import numpy as np
import deckcipher as dc

# Generate a permutation SAT file

def get_cnf_permutation(perm_length, offset = 0):
	clauses = []

	code = lambda x, y: x*perm_length + y + 1 + offset # assigns unique number to each entry (x,y) in permutation matrix

	# at least one per row
	for i in range(perm_length):
		clauses += [[code(i, j) for j in range(perm_length)] + [0]]

	# at most one per row
	for i in range(perm_length):
		for j in range(perm_length):
			for k in range(j + 1, perm_length):
				clauses += [[-code(i, j), -code(i, k), 0]]

	# at least one per column
	for i in range(perm_length):
		clauses += [[code(j, i) for j in range(perm_length)] + [0]]

	# at most one per column
	for i in range(perm_length):
		for j in range(perm_length):
			for k in range(j + 1, perm_length):
				clauses += [[-code(j, i), -code(k, i), 0]]

	num_var = perm_length**2
	num_clauses = len(clauses)

	return num_var, num_clauses, clauses

def get_cnf_permutation_product(offset1, offset2, offset3):
	# offset1 and offset2 are for the two factor matrices
	# offset3 is for the new permutation matrix
	# assumes all three already exist

	num_var = 0
	num_clauses = 0
	clauses = []

	code1 = lambda x, y: x*perm_length + y + 1 + offset1
	code2 = lambda x, y: x*perm_length + y + 1 + offset2
	code3 = lambda x, y: x*perm_length + y + 1 + offset3

	for i in range(perm_length):
		for j in range(perm_length):
			for k in range(perm_length):
				clauses += [[-code1(i, k), -code2(k, j), code3(i, j), 0]]
				num_clauses += 1

	return num_var, num_clauses, clauses

def get_cnf_permutation_as_identity(offset):
	# set the permutation matrix at offset as the identity matrix
	num_var = 0
	num_clauses = 0
	clauses = []

	code = lambda x, y: x*perm_length + y + 1 + offset

	for i in range(perm_length):
		clauses += [[code(i, i), 0]]
		num_clauses += 1

	return num_var, num_clauses, clauses

def get_cnf_ct_permutation_equality(index, offset):
	# in the permutation matrix at offset, in row zero, set index to true (corresponds to top card in deck cipher)
	num_var = 0
	num_clauses = 0
	clauses = []

	code = lambda x, y: x*perm_length + y + 1 + offset

	clauses += [[code(0, index), 0]]
	num_clauses += 1

	return num_var, num_clauses, clauses

def get_cnf_unique_top_card(offsets):
	# constrain the permutation matrices at offsets such that the top row is different
	# offsets is list of offsets
	num_var = 0
	num_clauses = 0
	clauses = []

	for i in range(len(offsets)):
		for j in range(i + 1, len(offsets)):
			code1 = lambda x, y: x*perm_length + y + 1 + offsets[i]
			code2 = lambda x, y: x*perm_length + y + 1 + offsets[j]

			for k in range(perm_length):
				clauses += [[-code1(0, k), -code2(0, k), 0]]
				num_clauses += 1

	return num_var, num_clauses, clauses	


# condition for A.A isomorph:
# P1 is permutation 1, P2 is permutation 2
# P1(0, k) = 1 and P2(k, 0) = 1
# --> add clauses [-P1(0,k), P2(k,0), 0] and [P1(0,k), -P2(k,0), 0] for k in range(1, perm_length)
def get_cnf_isomorph_ABA(p1, p2, permutations):
	num_var = 0
	num_clauses = 0
	clauses = []

	code1 = lambda x, y: x*perm_length + y + 1 + permutations[p1]["offset"]
	code2 = lambda x, y: x*perm_length + y + 1 + permutations[p2]["offset"]
	for k in range(1, perm_length):
		clauses += [[-code1(0, k), code2(k, 0), 0], [code1(0, k), -code2(k, 0), 0]]
		num_clauses += 2

	return num_var, num_clauses, clauses

# condition for A..A isomorph:
# P1, P2, P3
# P1(0, k) = 1 and P2(k, j) = 1 and P3(j, 0) = 1
# --> add clauses for each k in range(1, perm_length) and j in range(1, perm_length)
#     [-P1(0,k), P2(k,j), 0], [P1(0,k), -P2(k,j), 0], (P1(0, k) = 1 and P2(k, j) = 1)
#     [-P2(k,j), P3(j,0), 0], [P2(k,j), -P3(j,0), 0]  (P2(k, j) = 1 and P3(j, 0) = 1)

# etc.

###################################

#pt_alphabet_size = 4
#ct_alphabet_size = 6
#pt_array = [0, 1, 2, 3, 0, 1, 2, 3]
#ct_array = [4, 0, 4, 3, 2, 3, 2, 0]

pt = "abcdabcdaabcd"
pt_alphabet = "abcd"
ct_alphabet = "ABCDEF"

#pt = "this a very secret message and this a very secret message"
#pt_alphabet = "abcdefghijklmnopqrstuvwxyz "
#ct_alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

permutation_table = dc.get_permutation_table(len(ct_alphabet), len(pt_alphabet), seed = 0, double_free = True)
print(f"{pt = }")
pt_array = dc.str_to_array(pt, pt_alphabet)
ct_array = dc.encrypt(pt_array, permutation_table)
ct = dc.array_to_str(ct_array, ct_alphabet)
print(f"{ct = }")
roundtrip_array = dc.decrypt(ct_array, permutation_table)
roundtrip = dc.array_to_str(roundtrip_array, pt_alphabet)
assert roundtrip == pt, "Something went horribly wrong and the message couldn't be decrypted correctly!"

pt_alphabet_size = len(pt_alphabet)
ct_alphabet_size = len(ct_alphabet)
pt_length = len(pt)
perm_length = ct_alphabet_size
permutations = []

# explanation about the term offset: the variables count up in order with every new addition, therefore later permutation matrices must be "offset" to account for the already used variables

total_var = lambda: sum([d["num_var"] for d in permutations]) # total number of variables
total_clauses = lambda: sum([d["num_clauses"] for d in permutations]) # total number of clauses
all_clauses = lambda: [x for d in permutations for x in d["clauses"]] # all clauses concatenated together
def perm_matrix_indices(): # get a list with the indices of all permutation matrices in the list "permutations"
	ind = []
	for i, d in enumerate(permutations):
		if d["type"].startswith("perm_matrix"): ind += [i]
	return ind
perm_matrix_offset = lambda n: permutations[perm_matrix_indices()[n]]["offset"] # for the nth permutation matrix in the list "permutations" return the variable offset
perm_matrix_offsets = lambda: [permutations[perm_matrix_indices()[n]]["offset"] for n in range(len(perm_matrix_indices()))] # for all the permutation matrices in the list "permutations" return their variable offset

# create permutation matrices for each plain text letter
for i in range(pt_alphabet_size):
	num_var, num_clauses, clauses = get_cnf_permutation(perm_length, offset = total_var())
	permutations += [{"type": "perm_matrix", "offset": total_var(), "num_var": num_var, "num_clauses": num_clauses, "clauses": clauses}]

# create the deck
num_var, num_clauses, clauses = get_cnf_permutation(perm_length, offset = total_var())
permutations += [{"type": "perm_matrix_deck", "offset": total_var(), "num_var": num_var, "num_clauses": num_clauses, "clauses": clauses}]

# create the states of the shuffled deck
for i in range(pt_length):
	num_var, num_clauses, clauses = get_cnf_permutation(perm_length, offset = total_var())
	permutations += [{"type": "perm_matrix_deck", "offset": total_var(), "num_var": num_var, "num_clauses": num_clauses, "clauses": clauses}]

# set deck in an ordered state
num_var, num_clauses, clauses = get_cnf_permutation_as_identity(offset = perm_matrix_offset(pt_alphabet_size))
permutations += [{"type": "constraint_identity_matrix", "offset": 0, "num_var": num_var, "num_clauses": num_clauses, "clauses": clauses}]

# NOTE: This step REQUIRES the plain text to be known
# If it is possible to say "it must be one of the perm_matrices that does it, one of them does but idk which one" instead of the one at pt_letter, then it would not depend on the plain text
#
# constrain the deck states sequentially as permutation x old_deck = new_deck
for i in range(pt_length):
	pt_letter = pt_array[i]

	num_var, num_clauses, clauses = get_cnf_permutation_product(offset1 = perm_matrix_offset(pt_letter), offset2 = perm_matrix_offset(pt_alphabet_size + i), offset3 = perm_matrix_offset(pt_alphabet_size + i + 1))
	permutations += [{"type": "constraint_perm_matrix_product", "offset": 0, "num_var": num_var, "num_clauses": num_clauses, "clauses": clauses}]

# constrain the cipher text
for i in range(pt_length):
	ct_letter = ct_array[i]

	num_var, num_clauses, clauses = get_cnf_ct_permutation_equality(ct_letter, offset = perm_matrix_offset(pt_alphabet_size + i + 1))
	permutations += [{"type": "constraint_ct_letter", "offset": 0, "num_var": num_var, "num_clauses": num_clauses, "clauses": clauses}]
	
# constrain the pt permutation matrices to map to unique letters
num_var, num_clauses, clauses = get_cnf_unique_top_card(offsets = perm_matrix_offsets()[:pt_alphabet_size])
permutations += [{"type": "constraint_unique_top_card", "offset": 0, "num_var": num_var, "num_clauses": num_clauses, "clauses": clauses}]



print("Writing CNF...")
with open("permutation_test.cnf", "w") as f:
	f.write(f"p cnf {total_var()} {total_clauses()}\n")
	ac = all_clauses()
	for clause in ac:
		f.write(" ".join(list(map(str, clause))) + "\n")

#print(clauses)

print("Running kissat...")
subprocess.run(["./run_kissat_permutation.sh"])

print("Results:")
with open("permutation_test_result.txt", "r") as f:
	lines = f.readlines()
	result = ""
	expression = ""
	for line in lines:
		if line[0] == "s": result = line[2:].strip()
		if line[0] == "v": expression += line[2:].strip() + " "

print(result)
print(expression)

if result == "SATISFIABLE":
	permutation_table_reconstructed = np.empty((pt_alphabet_size, ct_alphabet_size), dtype = int)

	code_to_pos = lambda v, offset: ((v-1-offset)//perm_length, (v-1-offset)%perm_length)
	for i, p in enumerate(permutations):
		if p["type"].startswith("perm_matrix"):		
			permutation_matrix = np.empty((perm_length, perm_length), dtype = int)
			for n in expression.strip().split(" "):
				if abs(m := int(n)) < sum([d["num_var"] for d in permutations[:i+1]]) + 1 and abs(m) >= p["offset"] and m != 0:				
					permutation_matrix[code_to_pos(abs(m), p["offset"])] = np.sign(m)

			permutation = [np.nonzero(permutation_matrix[k] > 0)[0][0] for k in range(perm_length)]
			print(f"permutation_{i}({p['type']}) = {list(map(int, permutation))}")

			if p["type"] == "perm_matrix":
				permutation_table_reconstructed[i] = permutation

	print("Reconstructed permutation table:")
	print(permutation_table_reconstructed)
	print("Original permutation table:")
	print(permutation_table)

	pt_array_from_reconstructed_permutation_table = dc.decrypt(ct_array, permutation_table_reconstructed)
	pt_from_reconstructed_permutation_table = dc.array_to_str(pt_array_from_reconstructed_permutation_table, pt_alphabet)

	print("Decrypting ct with reconstructed permutation table:")
	print(f"{pt_from_reconstructed_permutation_table = }")

	print(f"Correct decryption: {pt_from_reconstructed_permutation_table == pt}")


	# [[4 0 1 3 2 5]
	#  [1 2 0 3 4 5]
	#  [2 0 5 4 1 3]
	#  [5 4 2 1 3 0]]

	# [4, 5, 3, 2, 1, 0]
	# [5, 4, 3, 0, 2, 1]
	# [3, 5, 4, 2, 1, 0]
	# [2, 4, 1, 5, 3, 0]