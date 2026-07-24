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

def get_cnf_pt_selector(pt_alphabet_size, offset = 0):
	code = lambda x: x + 1 + offset

	num_var = 0
	num_clauses = 0
	clauses = []

	# at least one selector is true
	clauses += [[code(i) for i in range(pt_alphabet_size)] + [0]]
	num_clauses += 1

	# between every pair, at most one selector is true
	for i in range(pt_alphabet_size):
		for j in range(i + 1, pt_alphabet_size):
			clauses += [[-code(i), -code(j), 0]]
			num_clauses += 1

	num_var = pt_alphabet_size

	return num_var, num_clauses, clauses


def get_cnf_permutation_product(perm_length, offset1, offset2, offset3):
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

def get_cnf_selector_permutation_product(perm_length, selectors, offsets1, offset2, offset3):
	# selectors is a list of codes for the selecting variables
	# offsets1 is a list of offsets for the first factor
	# offset2 is for the second factor matrix
	# offset3 is for the new permutation matrix
	# assumes all three already exist

	num_var = 0
	num_clauses = 0
	clauses = []

	code2 = lambda x, y: x*perm_length + y + 1 + offset2
	code3 = lambda x, y: x*perm_length + y + 1 + offset3

	# TODO
	for n, offset1 in enumerate(offsets1):
		code1 = lambda x, y: x*perm_length + y + 1 + offset1  
		for i in range(perm_length):
			for j in range(perm_length):
				for k in range(perm_length):
					clauses += [[-(selectors[n] + 1), -code1(i, k), -code2(k, j), code3(i, j), 0]]
					num_clauses += 1

	return num_var, num_clauses, clauses

def get_cnf_permutation_as_identity(perm_length, offset):
	# set the permutation matrix at offset as the identity matrix
	num_var = 0
	num_clauses = 0
	clauses = []

	code = lambda x, y: x*perm_length + y + 1 + offset

	for i in range(perm_length):
		clauses += [[code(i, i), 0]]
		num_clauses += 1

	return num_var, num_clauses, clauses

def get_cnf_ct_permutation_equality(perm_length, index, offset):
	# in the permutation matrix at offset, in row zero, set index to true (corresponds to top card in deck cipher)
	num_var = 0
	num_clauses = 0
	clauses = []

	code = lambda x, y: x*perm_length + y + 1 + offset

	clauses += [[code(0, index), 0]]
	num_clauses += 1

	return num_var, num_clauses, clauses

def get_cnf_equality(index, val = True):
	# set the variable at index to val
	num_var = 0
	num_clauses = 0
	clauses = []

	clauses += [[index * int((int(val)-0.5)*2), 0]]
	num_clauses += 1

	return num_var, num_clauses, clauses

def get_cnf_unique_top_card(perm_length, offsets):
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

def solve(use_known_pt, ct_alphabet, ct, pt_alphabet, pt = None, permutation_table = None, cribs = [], debug = True):

	# #pt_alphabet_size = 4
	# #ct_alphabet_size = 6
	# #pt_array = [0, 1, 2, 3, 0, 1, 2, 3]
	# #ct_array = [4, 0, 4, 3, 2, 3, 2, 0]

	# pt = "aaaaaaaaa"
	# pt_alphabet = "ab"
	# ct_alphabet = "ABCD"

	# #pt = "this a very secret message and this a very secret message"
	# #pt_alphabet = "abcdefghijklmnopqrstuvwxyz "
	# #ct_alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

	# # if set to true, this will intentionally corrupt the plain text, probably resulting in UNSAT
	# corrupt_pt = (False, "b" + pt[1:])

	# # if True:  Use the ct and pt to attempt to reconstruct a permutation table
	# #           Then check if permutation table reproduces the ct from the pt
	# # if False: Use the ct to attempt to reconstruct a pt - permutation table pair
	# #           Then check if the reconstructed pt and the reconstructed permutation table reproduce the ct
	# #           Then compare reconstructed pt and original pt
	# use_known_pt = False

	# # If use_known_pt is false, this will be used to input cribs
	# # can be empty list
	# cribs = [{"pos" : 4, "val" : "abcd"}]
	# cribs = []

	# permutation_table = dc.get_permutation_table(len(ct_alphabet), len(pt_alphabet), seed = 0, double_free = True)
	# print(f"{pt = }")
	# pt_array = dc.str_to_array(pt, pt_alphabet)
	# ct_array = dc.encrypt(pt_array, permutation_table)
	# ct = dc.array_to_str(ct_array, ct_alphabet)
	# print(f"{ct = }")
	# roundtrip_array = dc.decrypt(ct_array, permutation_table)
	# roundtrip = dc.array_to_str(roundtrip_array, pt_alphabet)
	# assert roundtrip == pt, "Something went horribly wrong and the message couldn't be decrypted correctly!"

	# #ct = "BCBDBCDAC" # orphan ciphertext for "ab" and "ABCD"
	# #ct = "BABDBADCB" # also an orphan
	# #ct = "BABDBADCA" # however, this is apparently not an orphan, even though it is a just a substitution of the first string (A <--> C), why? --> I think this is because A is kind of a special letter because it starts the unshuffled deck and repeating doubles is not allowed, so substitutions involving A might behave unexpectantly. Swapping for example (B <--> C) behaves in the expected way.
	# ct = "BCBDBCDAC" 
	# ct_array = dc.str_to_array(ct, ct_alphabet)

	# # corrupt plain text, if desired, probably resulting in UNSAT
	# if corrupt_pt[0]:
	# 	pt = corrupt_pt[1]
	# 	pt_array = dc.str_to_array(pt, pt_alphabet)

	if pt is not None: pt_array = dc.str_to_array(pt, pt_alphabet)
	ct_array = dc.str_to_array(ct, ct_alphabet)

	pt_alphabet_size = len(pt_alphabet)
	ct_alphabet_size = len(ct_alphabet)
	pt_length = len(ct) # using ct here to get the length because pt and ct have the same length anyways and ct is always given

	perm_length = ct_alphabet_size
	permutations = []

	# -1 implies unknown
	crib_array = [-1 for i in range(pt_length)]
	for d in cribs:
		for i in range(len(d["val"])):
			crib_array[d["pos"] + i] = pt_alphabet.index(d["val"][i])

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

	pt_letter_permutation_matrix_offsets = perm_matrix_offsets()

	# create the deck
	num_var, num_clauses, clauses = get_cnf_permutation(perm_length, offset = total_var())
	permutations += [{"type": "perm_matrix_deck", "offset": total_var(), "num_var": num_var, "num_clauses": num_clauses, "clauses": clauses}]

	# create the states of the shuffled deck
	for i in range(pt_length):
		num_var, num_clauses, clauses = get_cnf_permutation(perm_length, offset = total_var())
		permutations += [{"type": "perm_matrix_deck", "offset": total_var(), "num_var": num_var, "num_clauses": num_clauses, "clauses": clauses}]

	# set deck in an ordered state
	num_var, num_clauses, clauses = get_cnf_permutation_as_identity(perm_length, offset = perm_matrix_offset(pt_alphabet_size))
	permutations += [{"type": "constraint_identity_matrix", "offset": 0, "num_var": num_var, "num_clauses": num_clauses, "clauses": clauses}]

	if use_known_pt:
		# NOTE: This step REQUIRES the plain text to be known
		# If it is possible to say "it must be one of the perm_matrices that does it, one of them does but idk which one" instead of the one at pt_letter, then it would not depend on the plain text
		#
		# constrain the deck states sequentially as permutation x old_deck = new_deck
		for i in range(pt_length):
			pt_letter = pt_array[i]

			num_var, num_clauses, clauses = get_cnf_permutation_product(perm_length, offset1 = perm_matrix_offset(pt_letter), offset2 = perm_matrix_offset(pt_alphabet_size + i), offset3 = perm_matrix_offset(pt_alphabet_size + i + 1))
			permutations += [{"type": "constraint_perm_matrix_product", "offset": 0, "num_var": num_var, "num_clauses": num_clauses, "clauses": clauses}]
	else:
		# If we do not wish to use the plain text, we need to create an array to hold the reconstructed pt
		selector_offsets = []
		for i in range(pt_length):
			num_var, num_clauses, clauses = get_cnf_pt_selector(pt_alphabet_size, offset = total_var())
			selector_offsets += [total_var()]
			permutations += [{"type": "pt_selector", "offset": total_var(), "num_var": num_var, "num_clauses": num_clauses, "clauses": clauses}]

		# constrain the deck states sequentially as selector x permutation x old_deck = new_deck
		for i in range(pt_length):
			num_var, num_clauses, clauses = get_cnf_selector_permutation_product(perm_length, selectors = [selector_offsets[i] + j for j in range(pt_alphabet_size)], offsets1 = pt_letter_permutation_matrix_offsets, offset2 = perm_matrix_offset(pt_alphabet_size + i), offset3 = perm_matrix_offset(pt_alphabet_size + i + 1))
			permutations += [{"type": "constraint_perm_matrix_product", "offset": 0, "num_var": num_var, "num_clauses": num_clauses, "clauses": clauses}]

		# process cribs
		for i, crib in enumerate(crib_array):
			if crib == -1: continue
			num_var, num_clauses, clauses = get_cnf_equality(selector_offsets[i] + crib + 1)
			permutations += [{"type": "constraint_crib", "offset": 0, "num_var": num_var, "num_clauses": num_clauses, "clauses": clauses}]

		# If we want to disallow some plaintext, we would just set the specific variables in the selector matrix to false, or rather say not first letter or not second letter etc. such that as soon as at least one letter deviates, the condition is trivially satisfied and thus allowed.
		# If we want to disallow some plaintext UP TO MONOALPHABETIC SUBSTITUTION (i.e. disallow that particular isomorph code), then introduce a permutation matrix (pt_alphabet_size x pt_alphabet_size) and then disallow -position x permutation matrix etc.? Maybe that works? Need to calculate it on paper.



	# constrain the cipher text
	for i in range(pt_length):
		ct_letter = ct_array[i]

		num_var, num_clauses, clauses = get_cnf_ct_permutation_equality(perm_length, ct_letter, offset = perm_matrix_offset(pt_alphabet_size + i + 1))
		permutations += [{"type": "constraint_ct_letter", "offset": 0, "num_var": num_var, "num_clauses": num_clauses, "clauses": clauses}]
		
	# constrain the pt permutation matrices to map to unique letters
	num_var, num_clauses, clauses = get_cnf_unique_top_card(perm_length, offsets = perm_matrix_offsets()[:pt_alphabet_size])
	permutations += [{"type": "constraint_unique_top_card", "offset": 0, "num_var": num_var, "num_clauses": num_clauses, "clauses": clauses}]



	if debug: print("Writing CNF...")
	with open("permutation_test.cnf", "w") as f:
		f.write(f"p cnf {total_var()} {total_clauses()}\n")
		ac = all_clauses()
		for clause in ac:
			f.write(" ".join(list(map(str, clause))) + "\n")

	#print(clauses)

	if debug: print("Running kissat...")
	subprocess.run(["./run_kissat_permutation.sh"])

	if debug: print("Results:")
	with open("permutation_test_result.txt", "r") as f:
		lines = f.readlines()
		result = ""
		expression = ""
		for line in lines:
			if line[0] == "s": result = line[2:].strip()
			if line[0] == "v": expression += line[2:].strip() + " "

	if debug: print(result)
	if debug: print(expression)

	if result == "SATISFIABLE":
		permutation_table_reconstructed = np.empty((pt_alphabet_size, ct_alphabet_size), dtype = int)
		selection_matrix = np.empty((pt_length, pt_alphabet_size), dtype = int)

		code_to_pos = lambda v, offset: ((v-1-offset)//perm_length, (v-1-offset)%perm_length)
		selector_code_to_pos = lambda v, offset: ((v-1-offset)//pt_alphabet_size, (v-1-offset)%pt_alphabet_size)

		for i, p in enumerate(permutations):
			if p["type"].startswith("perm_matrix"):		
				permutation_matrix = np.empty((perm_length, perm_length), dtype = int)
				for n in expression.strip().split(" "):
					if abs(m := int(n)) < sum([d["num_var"] for d in permutations[:i+1]]) + 1 and abs(m) >= p["offset"] and m != 0:				
						permutation_matrix[code_to_pos(abs(m), p["offset"])] = np.sign(m)

				permutation = [np.nonzero(permutation_matrix[k] > 0)[0][0] for k in range(perm_length)]
				if debug: print(f"permutation_{i}({p['type']}) = {list(map(int, permutation))}")

				if p["type"] == "perm_matrix":
					permutation_table_reconstructed[i] = permutation

			#elif p["type"] == "pt_selector":		
			#	#selector_offsets
			#	for n in expression.strip().split(" "):
			#		#if (m := int(n)) != 0 and abs(m) >= selector_offsets[0] and abs(m) < (selector_offsets[-1] + pt_alphabet_size):
			#		if (m := int(n)) != 0 and abs(m) >= p["offset"] and abs(m) < (p["offset"] + pt_alphabet_size):
			#			selection_matrix[selector_code_to_pos(abs(m), selector_offsets[0])] = np.sign(m)

		if not use_known_pt:
			for n in expression.strip().split(" "):
				if (m := int(n)) != 0 and abs(m) >= selector_offsets[0] and abs(m) <= (selector_offsets[-1] + pt_alphabet_size):	
					selection_matrix[selector_code_to_pos(abs(m), selector_offsets[0])] = np.sign(m)

		if use_known_pt:
			return {"satisfiable" : True, "permutation_table_reconstructed": permutation_table_reconstructed}

		else:
			# we need to use the reconstructed pt and the reconstructed permutation table to check
			reconstructed_pt = ""
			for row in selection_matrix:
				reconstructed_pt += pt_alphabet[np.nonzero(row == 1)[0][0]]

			return {"satisfiable" : True, "permutation_table_reconstructed": permutation_table_reconstructed, "reconstructed_pt" : reconstructed_pt}
		
	else:
		# UNSATISFIABLE
		return {"satisfiable" : False}

def analyse_result(use_known_pt, ct_alphabet, ct, pt_alphabet, pt = None, permutation_table = None, permutation_table_reconstructed = None, reconstructed_pt = None, satisfiable = None):
	print("Reconstructed permutation table:")
	print(permutation_table_reconstructed)
	print("Original permutation table (if given):")
	print(permutation_table)

	if use_known_pt:
		pt_array_from_reconstructed_permutation_table = dc.decrypt(ct_array, permutation_table_reconstructed)
		pt_from_reconstructed_permutation_table = dc.array_to_str(pt_array_from_reconstructed_permutation_table, pt_alphabet)

		# we need to use the original pt to check the permutation table
		print("Decrypting ct with reconstructed permutation table:")
		print(f"{pt_from_reconstructed_permutation_table = }")
		print(f"Correct decryption: {pt_from_reconstructed_permutation_table == pt}")

	else:
		# we need to use the reconstructed pt and the reconstructed permutation table to check
		reconstructed_pt_array = dc.str_to_array(reconstructed_pt, pt_alphabet)
		reconstructed_ct_array = dc.encrypt(reconstructed_pt_array, permutation_table_reconstructed)
		reconstructed_ct = dc.array_to_str(reconstructed_ct_array, ct_alphabet)

		print(f"{pt               = }")
		print(f"{reconstructed_pt = }")
		print(f"{ct               = }")
		print(f"{reconstructed_ct = }")

		print(f"Correct ct reproduction: {ct == reconstructed_ct}")
		print("-"*10)

		print(f"pt isomorph code               = '{dc.get_isomorph_code(pt)}'")
		print(f"reconstructed pt isomorph code = '{dc.get_isomorph_code(reconstructed_pt)}'")
		print(f"reconstructed pt is monoalphabetic substitution of pt: {dc.get_isomorph_code(pt) == dc.get_isomorph_code(reconstructed_pt)}")

def generate_some_ct(pt, pt_alphabet, ct_alphabet, seed = 0, double_free = True, debug = True):
	permutation_table = dc.get_permutation_table(len(ct_alphabet), len(pt_alphabet), seed = 0, double_free = True)
	if debug: print(f"{pt = }")
	pt_array = dc.str_to_array(pt, pt_alphabet)
	ct_array = dc.encrypt(pt_array, permutation_table)
	ct = dc.array_to_str(ct_array, ct_alphabet)
	if debug: print(f"{ct = }")
	roundtrip_array = dc.decrypt(ct_array, permutation_table)
	roundtrip = dc.array_to_str(roundtrip_array, pt_alphabet)
	assert roundtrip == pt, "Something went horribly wrong and the message couldn't be decrypted correctly!"

	return ct, permutation_table

if __name__ == "__main__":

	#pt = "aaaaaaaaa"
	#pt_alphabet = "ab"
	#ct_alphabet = "ABCD"
	#ct, permutation_table = generate_some_ct(pt, pt_alphabet, ct_alphabet, seed = 0, double_free = True, debug = True)
	#result = solve(use_known_pt = False, ct = ct, ct_alphabet = ct_alphabet, pt = pt, pt_alphabet = pt_alphabet, permutation_table = permutation_table, cribs = [], debug = True)
	#analyse_result(use_known_pt = False, ct = ct, ct_alphabet = ct_alphabet, pt = pt, pt_alphabet = pt_alphabet, permutation_table = permutation_table, **result)
	
	result_dict = {}
	l_stats = {}

	pt_alphabet = "abc"
	ct_alphabet = "ABCD"

	unsat_prefixes = []

	for max_ct_len in range(1, 13):
		l_stats[max_ct_len] = {True: 0, False: 0}
		m = len(ct_alphabet)**max_ct_len
		for i in range(m):
			ct = ""
			k = i
			for j in range(max_ct_len):
				r = k%len(ct_alphabet)
				ct = ct_alphabet[r] + ct
				k = k//len(ct_alphabet)
			if max_ct_len > 2 and i%(m>>3) == 0: print(ct)

			#contains_doubles = False
			#for j, c in enumerate(ct):
			#	if j == 0: continue
			#	if c == ct[j-1]: contains_doubles = True; break
			#if contains_doubles: continue # we want to look for things without doubles
			#if ct[0] == ct_alphabet[0]: continue # if the first letter is the special letter, that implies a permutation starting with 0, which would allow doubles

			found = False
			isocode = dc.get_firstfree_isomorph_code(ct, special_letter = ct_alphabet[0])
			for c in unsat_prefixes:
				if isocode.startswith(c):
					# if the ct starts with an unsat prefix, everything we append will not make it sat again
					# so we dont need to calculate it
					result_dict[ct] = False
					l_stats[max_ct_len][False] += 1
					found = True
					break
			if found: continue
			if isocode in result_dict:
				l_stats[max_ct_len][result_dict[isocode]] += 1
				continue

			result = solve(use_known_pt = False, ct = ct, ct_alphabet = ct_alphabet, pt = None, pt_alphabet = pt_alphabet, permutation_table = None, cribs = [], debug = False)
			result_dict[isocode] = result["satisfiable"]
			l_stats[max_ct_len][result["satisfiable"]] += 1

			if not result["satisfiable"]:
				unsat_prefixes += [isocode]
		print(l_stats)

	print("Finish")
	#print(result_dict)
	print(l_stats)



	# for pt_alphabet = "ab", ct_alphabet = "ABCD"
	# double-free
	# {1: {True: 3, False: 0}, 2: {True: 9, False: 0}, 3: {True: 27, False: 0}, 4: {True: 81, False: 0}, 5: {True: 243, False: 0}, 6: {True: 729, False: 0}, 7: {True: 2187, False: 0}, 8: {True: 6273, False: 288}, 9: {True: 16707, False: 2976}, 10: {True: 41175, False: 17874}, 11: {True: 96027, False: 81120}}


	# for pt_alphabet = "ab", ct_alphabet = "ABC"
	# not double-free
	# {1: {True: 3, False: 0}, 2: {True: 9, False: 0}, 3: {True: 27, False: 0}, 4: {True: 73, False: 8}, 5: {True: 171, False: 72}, 6: {True: 393, False: 336}, 7: {True: 855, False: 1332}, 8: {True: 1841, False: 4720}, 9: {True: 3863, False: 15820}, 10: {True: 8053, False: 50996}, 11: {True: 16567, False: 160580}, 12: {True: 33941, False: 497500}}

	# for pt_alphabet = "ab", ct_alphabet = "ABCD"
	# not double-free
	# {1: {True: 4, False: 0}, 2: {True: 16, False: 0}, 3: {True: 64, False: 0}, 4: {True: 232, False: 24}, 5: {True: 736, False: 288}, 6: {True: 2200, False: 1896}, 7: {True: 6220, False: 10164}, 8: {True: 16594, False: 48942}, 9: {True: 41638, False: 220506}, 10: {True: 98998, False: 949578}}

	# for pt_alphabet = "ab", ct_alphabet = "ABCDE"
	# not double-free
	# {1: {True: 5, False: 0}, 2: {True: 25, False: 0}, 3: {True: 125, False: 0}, 4: {True: 577, False: 48}, 5: {True: 2357, False: 768}, 6: {True: 9145, False: 6480}, 7: {True: 33701, False: 44424}, 8: {True: 121729, False: 268896}, 9: {True: 413717, False: 1539408}}

	# for pt_alphabet = "ab", ct_alphabet = "ABCDEF"
	# not double-free
	# {1: {True: 6, False: 0}, 2: {True: 36, False: 0}, 3: {True: 216, False: 0}, 4: {True: 1216, False: 80}, 5: {True: 6176, False: 1600}, 6: {True: 29956, False: 16700}, 7: {True: 137996, False: 141940}, 8: {True: 628616, False: 1051000}}

	# pt_alphabet = "ab", ct_alphabet = "ABCDEFG"
	# not double-free
	# {1: {True: 7, False: 0}, 2: {True: 49, False: 0}, 3: {True: 343, False: 0}, 4: {True: 2281, False: 120}, 5: {True: 13927, False: 2880}, 6: {True: 81709, False: 35940}, 7: {True: 456403, False: 367140}, 8: {True: 2523661, False: 3241140}}

	# for pt_alphabet = "abc", ct_alphabet = "ABCD"
	# not double-free
	# {1: {True: 4, False: 0}, 2: {True: 16, False: 0}, 3: {True: 64, False: 0}, 4: {True: 256, False: 0}, 5: {True: 1024, False: 0}, 6: {True: 4096, False: 0}, 7: {True: 16384, False: 0}, 8: {True: 65536, False: 0}, 9: {True: 261568, False: 576}}

	# for pt_alphabet = "abc", ct_alphabet = "ABCDE"
	# not double-free
	# {1: {True: 5, False: 0}, 2: {True: 25, False: 0}, 3: {True: 125, False: 0}, 4: {True: 625, False: 0}, 5: {True: 3125, False: 0}, 6: {True: 15625, False: 0}, 7: {True: 78125, False: 0}, 8: {True: 390625, False: 0}, 9: {True: 1951829, False: 1296}}

	# for pt_alphabet = "abc", ct_alphabet = "ABCDEF"
	# not double-free
	# {1: {True: 6, False: 0}, 2: {True: 36, False: 0}, 3: {True: 216, False: 0}, 4: {True: 1296, False: 0}, 5: {True: 7776, False: 0}, 6: {True: 46656, False: 0}, 7: {True: 279936, False: 0}, 8: {True: 1679616, False: 0}}