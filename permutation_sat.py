import subprocess
import numpy as np
import deckcipher as dc
import lzma_mt
import lzma

# Generate a permutation SAT file

def get_cnf_permutation(perm_length, offset = 0, return_no_clauses = False):
	clauses = []

	if return_no_clauses:
		# Just return the number of vars and clauses, but do not return clauses themselves
		num_var = perm_length**2
		num_clauses = 2 * perm_length + perm_length ** 2 * (perm_length - 1)
		return num_var, num_clauses, []

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

def get_cnf_permutation_optimized(perm_length, offset = 0, return_no_clauses = False):
	if return_no_clauses:
		# Just return the number of vars and clauses, but do not return clauses themselves
		num_var = perm_length**2
		num_clauses = 2 * perm_length + perm_length ** 2 * (perm_length - 1)
		return num_var, num_clauses, []

	#code = lambda x, y: x*perm_length + y + 1 + offset # assigns unique number to each entry (x,y) in permutation matrix

	clauses = ""

	# at least one per row
	for i in range(perm_length):
		clauses += " ".join([str(i*perm_length + j + 1 + offset) for j in range(perm_length)]) + " 0\n"

	# at most one per row
	for i in range(perm_length):
		for j in range(perm_length):
			temp = str(i*perm_length + j + 1 + offset)
			for k in range(j + 1, perm_length):
				clauses += "-" + temp + " -" + str(i*perm_length + k + 1 + offset) + " 0\n"

	# at least one per column
	for i in range(perm_length):
		clauses += " ".join([str(j*perm_length + i + 1 + offset) for j in range(perm_length)]) + " 0\n"

	# at most one per column
	for i in range(perm_length):
		for j in range(perm_length):
			temp = str(j*perm_length + i + 1 + offset)
			for k in range(j + 1, perm_length):
				clauses += "-" + temp + " -" + str(k*perm_length + i + 1 + offset) + " 0\n"

	num_var = perm_length**2
	num_clauses = len(clauses)

	return num_var, num_clauses, clauses

def get_cnf_permutation_vector(perm_length, offset = 0, return_no_clauses = False):
	num_var = 0
	num_clauses = 0
	clauses = []

	if return_no_clauses:
		# Just return the number of vars and clauses, but do not return clauses themselves
		num_var = perm_length
		num_clauses = 1 + ((perm_length - 1) * perm_length / 2)
		return num_var, num_clauses, []

	code = lambda x: x + 1 + offset

	# at least one entry is true
	clauses += [[code(i) for i in range(perm_length)] + [0]]
	num_clauses += 1

	# between every pair, at most one selector is true
	for i in range(perm_length):
		for j in range(i + 1, perm_length):
			clauses += [[-code(i), -code(j), 0]]
			num_clauses += 1

	num_var = perm_length

	return num_var, num_clauses, clauses

def get_cnf_permutation_vector_constraints(perm_length, offsets = [], return_no_clauses = False):
	# no two rows can be the same
	num_var = 0
	num_clauses = 0
	clauses = []

	if return_no_clauses:
		num_var = 0
		num_clauses = perm_length * (len(offsets) * (len(offsets) - 1)/2)
		return num_var, num_clauses, []

	code = lambda x, y: offsets[y] + 1 + x

	for i in range(perm_length):
		for j in range(len(offsets)):
			for k in range(j + 1, len(offsets)):
				clauses += [[-code(i, j), -code(i, k), 0]]
				num_clauses += 1

	return num_var, num_clauses, clauses


def get_cnf_pt_selector(pt_alphabet_size, offset = 0, return_no_clauses = False):
	code = lambda x: x + 1 + offset

	num_var = 0
	num_clauses = 0
	clauses = []

	if return_no_clauses:
		num_var = pt_alphabet_size
		num_clauses = 1 + (pt_alphabet_size * (pt_alphabet_size - 1) / 2)
		return num_var, num_clauses, []

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


def get_cnf_permutation_product(perm_length, offset1, offset2, offset3, return_no_clauses = False):
	# offset1 and offset2 are for the two factor matrices
	# offset3 is for the new permutation matrix
	# assumes all three already exist

	num_var = 0
	num_clauses = 0
	clauses = []

	if return_no_clauses:
		num_var = 0
		num_clauses = perm_length**3
		return num_var, num_clauses, []

	code1 = lambda x, y: x*perm_length + y + 1 + offset1
	code2 = lambda x, y: x*perm_length + y + 1 + offset2
	code3 = lambda x, y: x*perm_length + y + 1 + offset3

	for i in range(perm_length):
		for j in range(perm_length):
			for k in range(perm_length):
				clauses += [[-code1(i, k), -code2(k, j), code3(i, j), 0]]
				num_clauses += 1

	return num_var, num_clauses, clauses

def get_cnf_permutation_product_with_vector(perm_length, offset1, offset2, offset3, return_no_clauses = False):
	# offset1 is for the first factor matrix
	# offset2 is for the row vector (also length perm_length)
	# offset3 is for the result vector (also length perm_length)
	# assumes all three already exist

	num_var = 0
	num_clauses = 0
	clauses = []

	if return_no_clauses:
		num_var = 0
		num_clauses = perm_length**2
		return num_var, num_clauses, []

	code1 = lambda x, y: x*perm_length + y + 1 + offset1
	code2 = lambda x: offset2 + x + 1
	code3 = lambda x: offset3 + x + 1

	for i in range(perm_length):
		for k in range(perm_length):
			clauses += [[-code1(i, k), -code2(k), code3(i), 0]]
			num_clauses += 1

	return num_var, num_clauses, clauses

def get_cnf_selector_permutation_product(perm_length, selectors, offsets1, offset2, offset3, return_no_clauses = False):
	# selectors is a list of codes for the selecting variables
	# offsets1 is a list of offsets for the first factor
	# offset2 is for the second factor matrix
	# offset3 is for the new permutation matrix
	# assumes all three already exist

	num_var = 0
	num_clauses = 0
	clauses = []

	if return_no_clauses:
		num_var = 0
		num_clauses = len(offsets1) * (perm_length**3)
		return num_var, num_clauses, []

	code2 = lambda x, y: x*perm_length + y + 1 + offset2
	code3 = lambda x, y: x*perm_length + y + 1 + offset3

	for n, offset1 in enumerate(offsets1):
		code1 = lambda x, y: x*perm_length + y + 1 + offset1  
		for i in range(perm_length):
			for j in range(perm_length):
				for k in range(perm_length):
					clauses += [[-(selectors[n] + 1), -code1(i, k), -code2(k, j), code3(i, j), 0]]
					num_clauses += 1

	return num_var, num_clauses, clauses

def get_cnf_selector_permutation_product_with_vector(perm_length, selectors, offsets1, offset2, offset3, return_no_clauses = False):
	# selectors is a list of codes for the selecting variables
	# offsets1 is a list of offsets for the first factor
	# offset2 is for the row vector (also length perm_length)
	# offset3 is for the result vector (also length perm_length)
	# assumes all three already exist

	num_var = 0
	num_clauses = 0
	clauses = []

	if return_no_clauses:
		num_var = 0
		num_clauses = len(offsets1) * (perm_length**2)
		return num_var, num_clauses, []

	code2 = lambda x: x + offset2 + 1
	code3 = lambda x: x + offset3 + 1

	for n, offset1 in enumerate(offsets1):
		code1 = lambda x, y: x*perm_length + y + 1 + offset1  
		for i in range(perm_length):
			for k in range(perm_length):
				clauses += [[-(selectors[n] + 1), -code1(i, k), -code2(k), code3(i), 0]]
				num_clauses += 1

	return num_var, num_clauses, clauses

def get_cnf_selector_permutation_product_with_vector_optimized(perm_length, selectors, offsets1, offset2, offset3, return_no_clauses = False):
	# selectors is a list of codes for the selecting variables
	# offsets1 is a list of offsets for the first factor
	# offset2 is for the row vector (also length perm_length)
	# offset3 is for the result vector (also length perm_length)
	# assumes all three already exist

	num_var = 0
	num_clauses = len(offsets1) * (perm_length**2)
	if return_no_clauses:
		return num_var, num_clauses, []

	clauses = ""

	for n, offset1 in enumerate(offsets1):
		temp = "-" + str(selectors[n] + 1)
		for i in range(perm_length):
			temp2 = str(i + offset3 + 1)
			for k in range(perm_length):
				clauses += temp + " -" + str(i*perm_length + k + 1 + offset1) + " -" + str(k + offset2 + 1) + " " + temp2 + " 0\n"

	return num_var, num_clauses, clauses

def get_cnf_permutation_as_identity(perm_length, offset, return_no_clauses = False):
	# set the permutation matrix at offset as the identity matrix
	num_var = 0
	num_clauses = 0
	clauses = []

	if return_no_clauses:
		num_var = 0
		num_clauses = perm_length
		return num_var, num_clauses, []

	code = lambda x, y: x*perm_length + y + 1 + offset

	for i in range(perm_length):
		clauses += [[code(i, i), 0]]
		num_clauses += 1

	return num_var, num_clauses, clauses

def get_cnf_ct_permutation_equality(perm_length, index, offset, return_no_clauses = False):
	# in the permutation matrix at offset, in row zero, set index to true (corresponds to top card in deck cipher)
	num_var = 0
	num_clauses = 0
	clauses = []

	if return_no_clauses:
		num_var = 0
		num_clauses = 1
		return num_var, num_clauses, []

	code = lambda x, y: x*perm_length + y + 1 + offset

	clauses += [[code(0, index), 0]]
	num_clauses += 1

	return num_var, num_clauses, clauses

def get_cnf_equality(index, val = True, return_no_clauses = False):
	# set the variable at index to val
	num_var = 0
	num_clauses = 0
	clauses = []

	if return_no_clauses:
		num_var = 0
		num_clauses = 1
		return num_var, num_clauses, []

	clauses += [[index * int((int(val)-0.5)*2), 0]]
	num_clauses += 1

	return num_var, num_clauses, clauses

def get_cnf_unique_top_card(perm_length, offsets, return_no_clauses = False):
	# constrain the permutation matrices at offsets such that the top row is different
	# offsets is list of offsets
	num_var = 0
	num_clauses = 0
	clauses = []

	if return_no_clauses:
		num_var = 0
		num_clauses = perm_length * (len(offsets) * (len(offsets) - 1) / 2)
		return num_var, num_clauses, []

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

def get_merge_cnf(l_list, r_list, s_list):
	clauses = []

	l_len = len(l_list)
	r_len = len(r_list)
	s_len = len(s_list)

	l_code = lambda x: l_list[x]
	r_code = lambda x: r_list[x]
	s_code = lambda x: s_list[x]

	for s in range(s_len):
		for r in range(-1, s+1):
			l = s-r-1
			if r >= r_len: continue # -r{r} is always true, drop entire clause
			if l >= l_len: continue # -l{l} is always true, drop entire clause
			if r == -1: clauses += [[-l_code(l), s_code(s), 0]]; continue # -r{r} is always false, can be dropped
			if l == -1: clauses += [[-r_code(r), s_code(s), 0]]; continue # -l{l} is always false, can be dropped
			clauses += [[-l_code(l), -r_code(r), s_code(s), 0]]
		for r in range(s+1):
			l = s-r
			if r >= r_len: clauses += [[l_code(l), -s_code(s), 0]]; continue # r{r} is always false, can be dropped
			if l >= l_len: clauses += [[r_code(r), -s_code(s), 0]]; continue # l{l} is always false, can be dropped
			clauses += [[l_code(l), r_code(r), -s_code(s), 0]]

	return clauses

def split_list(original_list, code, depth = None):
	if depth is None: depth = int(np.ceil(np.log2(len(original_list))))

	if len(original_list) == 1:
		return (original_list, [])

	if len(original_list) == 2:
		list1 = original_list[:1]
		list2 = original_list[1:]
		list3 = list(map(lambda y: code(depth, y), original_list))
		#print(f"sort {list1} and {list2} into {list3}")
		clauses = get_merge_cnf(list1, list2, list3)
		return (list3, clauses)

	l = int(np.power(2, np.floor(np.log2(len(original_list)-1))))
	list1, clauses1 = split_list(original_list[:l], code, depth - 1)
	list2, clauses2 = split_list(original_list[l:], code, depth - 1)
	list3 = list(map(lambda y: code(depth, y), original_list))
	#print(f"merge {list1} and {list2} into {list3}")
	clauses3 = get_merge_cnf(list1, list2, list3)
	return (list3, clauses1 + clauses2 + clauses3)

def get_cnf_totalizer(input_vars, offset_out):
	num_var = 0
	num_clauses = 0

	lis = [i+1 for i in range(len(input_vars))]
	#print(f"original list: {lis}")
	outlist, clauses = split_list(lis, code = lambda x, y: len(lis)*x + y)
	#print(outlist)
	#print(clauses)

	# because single values may terminate early, some variables may be missing from this
	remaining_vars = list(range(lis[0], outlist[-1]+1))
	for c in clauses:
		for i in map(abs, c):
			if i in remaining_vars:
				remaining_vars.remove(i)

	for r in remaining_vars:
		f = lambda x: np.sign(x)*(abs(x)-1) if abs(x) >= r else x
		outlist = list(map(f, outlist))
		for i in range(len(clauses)):
			clauses[i] = list(map(f, clauses[i]))

	#print(outlist)
	#print(clauses)

	replacement = {0: 0}
	for i in range(lis[0], outlist[-1]+1):
		if i <= len(lis):
			replacement[i] = input_vars[i-1]
		else:
			replacement[i] = i - len(lis) + offset_out
			num_var += 1

	f = lambda x: np.sign(x)*replacement[abs(x)]
	outlist = list(map(f, outlist))
	for i in range(len(clauses)):
		clauses[i] = list(map(f, clauses[i]))

	#print(outlist)
	#print(clauses)

	num_clauses = len(clauses)

	return num_var, num_clauses, clauses, outlist

def get_cnf_set_totalizer_counter(input_vars, min_true, max_true = None):
	# get a list of input vars and treat them as a totalizer counter
	# set everything below min_true to TRUE and everything above max_true to FALSE
	if max_true is None: max_true = min_true

	num_var = 0
	num_clauses = 0
	clauses = []

	for i, v in enumerate(input_vars):
		if i <= min_true-1:
			clauses += [[v, 0]]
			num_clauses += 1
		if i > max_true-1:
			clauses += [[-v, 0]]
			num_clauses += 1

	return num_var, num_clauses, clauses

def get_cnf_permutation_equality_up_to_selector(perm_length, offset1, offset2, selector_list, return_no_clauses = False):
	# ...

	num_var = 0
	num_clauses = 0
	clauses = []

	if return_no_clauses:
		num_var = 0
		num_clauses = 2 * (perm_length**2)
		return num_var, num_clauses, []

	code1 = lambda x, y: x*perm_length + y + 1 + offset1
	code2 = lambda x, y: x*perm_length + y + 1 + offset2
	code_selector = lambda x: selector_list[x]

	for i in range(perm_length):
		for j in range(perm_length):
			clauses += [[code_selector(i), -code1(i, j),  code2(i, j), 0]]
			clauses += [[code_selector(i),  code1(i, j), -code2(i, j), 0]]
			num_clauses += 2

	return num_var, num_clauses, clauses


###################################

def solve(use_known_pt, ct_alphabet, ct, pt_alphabet, pt = None, permutation_table = None, cribs = [], debug = True, related_permutations = False, related_permutations_free_rows = 3, use_multiple_ct = False, other_cts = [], write_cnf_then_exit = False):
	# if use_multiple_ct is True, then for now I will ignore use_known_pt
	if use_known_pt and use_multiple_ct:
		print("[Error] Known pt combined with multiple ct is currently not supported!")
		return {}

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

	if use_multiple_ct:
		list_other_ct_arrays = []
		list_other_pt_lengths = []
		for c in other_cts:
			list_other_ct_arrays += [dc.str_to_array(c, ct_alphabet)]
			list_other_pt_lengths += [len(c)]


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
	if debug: print("Creating permutation matrices for pt letters...")
	for i in range(pt_alphabet_size):
		num_var, num_clauses, clauses = get_cnf_permutation(perm_length, offset = total_var())
		permutations += [{"type": "perm_matrix", "offset": total_var(), "num_var": num_var, "num_clauses": num_clauses, "clauses": clauses}]

	pt_letter_permutation_matrix_offsets = perm_matrix_offsets()

	# create the deck
	if debug: print("Creating permutation matrix for the deck...")
	num_var, num_clauses, clauses = get_cnf_permutation(perm_length, offset = total_var())
	permutations += [{"type": "perm_matrix_deck", "offset": total_var(), "num_var": num_var, "num_clauses": num_clauses, "clauses": clauses}]

	# create the states of the shuffled deck
	if debug: print("Creating permutation matrices for states of the deck...")
	for i in range(pt_length):
		num_var, num_clauses, clauses = get_cnf_permutation(perm_length, offset = total_var())
		permutations += [{"type": "perm_matrix_deck", "offset": total_var(), "num_var": num_var, "num_clauses": num_clauses, "clauses": clauses}]

	# set deck in an ordered state
	if debug: print("Setting initial ordering of the deck...")
	num_var, num_clauses, clauses = get_cnf_permutation_as_identity(perm_length, offset = perm_matrix_offset(pt_alphabet_size))
	permutations += [{"type": "constraint_identity_matrix", "offset": 0, "num_var": num_var, "num_clauses": num_clauses, "clauses": clauses}]

	if use_known_pt:
		# NOTE: This step REQUIRES the plain text to be known
		# If it is possible to say "it must be one of the perm_matrices that does it, one of them does but idk which one" instead of the one at pt_letter, then it would not depend on the plain text
		#
		# constrain the deck states sequentially as permutation x old_deck = new_deck
		if debug: print("Constraining the deck with the pt...")
		for i in range(pt_length):
			pt_letter = pt_array[i]

			num_var, num_clauses, clauses = get_cnf_permutation_product(perm_length, offset1 = perm_matrix_offset(pt_letter), offset2 = perm_matrix_offset(pt_alphabet_size + i), offset3 = perm_matrix_offset(pt_alphabet_size + i + 1))
			permutations += [{"type": "constraint_perm_matrix_product", "offset": 0, "num_var": num_var, "num_clauses": num_clauses, "clauses": clauses}]
	else:
		# If we do not wish to use the plain text, we need to create an array to hold the reconstructed pt
		if debug: print("Creating selectors for the pt...")
		selector_offsets = []
		for i in range(pt_length):
			num_var, num_clauses, clauses = get_cnf_pt_selector(pt_alphabet_size, offset = total_var())
			selector_offsets += [total_var()]
			permutations += [{"type": "pt_selector", "offset": total_var(), "num_var": num_var, "num_clauses": num_clauses, "clauses": clauses}]

		if debug: print("Constraining the deck with the pt selectors...")
		# constrain the deck states sequentially as selector x permutation x old_deck = new_deck
		for i in range(pt_length):
			num_var, num_clauses, clauses = get_cnf_selector_permutation_product(perm_length, selectors = [selector_offsets[i] + j for j in range(pt_alphabet_size)], offsets1 = pt_letter_permutation_matrix_offsets, offset2 = perm_matrix_offset(pt_alphabet_size + i), offset3 = perm_matrix_offset(pt_alphabet_size + i + 1))
			permutations += [{"type": "constraint_perm_matrix_product", "offset": 0, "num_var": num_var, "num_clauses": num_clauses, "clauses": clauses}]

		# process cribs
		if debug: print("Adding cribs...")
		for i, crib in enumerate(crib_array):
			if crib == -1: continue
			num_var, num_clauses, clauses = get_cnf_equality(selector_offsets[i] + crib + 1)
			permutations += [{"type": "constraint_crib", "offset": 0, "num_var": num_var, "num_clauses": num_clauses, "clauses": clauses}]

		# If we want to disallow some plaintext, we would just set the specific variables in the selector matrix to false, or rather say not first letter or not second letter etc. such that as soon as at least one letter deviates, the condition is trivially satisfied and thus allowed.
		# If we want to disallow some plaintext UP TO MONOALPHABETIC SUBSTITUTION (i.e. disallow that particular isomorph code), then introduce a permutation matrix (pt_alphabet_size x pt_alphabet_size) and then disallow -position x permutation matrix etc.? Maybe that works? Need to calculate it on paper.

	# constrain the cipher text
	if debug: print("Constraining the deck to the cipher text...")
	for i in range(pt_length):
		ct_letter = ct_array[i]

		num_var, num_clauses, clauses = get_cnf_ct_permutation_equality(perm_length, ct_letter, offset = perm_matrix_offset(pt_alphabet_size + i + 1))
		permutations += [{"type": "constraint_ct_letter", "offset": 0, "num_var": num_var, "num_clauses": num_clauses, "clauses": clauses}]

	# if we are given multiple cipher texts, we want to have another deck, plaintext selectors, etc., but reuse the plaintext permutation matrices (so one permutation table has to decrypt multiple messages)
	if use_multiple_ct:
		if debug: print("Processing additional cts...")
		all_other_selector_offsets = []
		for ct_number, other_ct_array in enumerate(list_other_ct_arrays):
			other_pt_length = list_other_pt_lengths[ct_number]

			# create the deck
			if debug: print("Creating permutation matrix for the deck...")
			num_var, num_clauses, clauses = get_cnf_permutation(perm_length, offset = total_var())
			offset_of_ordered_deck = total_var()
			permutations += [{"type": f"perm_matrix_deck{ct_number+2}", "offset": total_var(), "num_var": num_var, "num_clauses": num_clauses, "clauses": clauses}]

			# create the states of the shuffled deck
			if debug: print("Creating permutation matrices for states of the deck...")
			shuffled_deck_offsets = []
			for i in range(other_pt_length):
				num_var, num_clauses, clauses = get_cnf_permutation(perm_length, offset = total_var())
				shuffled_deck_offsets += [total_var()]
				permutations += [{"type": f"perm_matrix_deck{ct_number+2}", "offset": total_var(), "num_var": num_var, "num_clauses": num_clauses, "clauses": clauses}]

			# set deck in an ordered state
			if debug: print("Setting initial ordering of the deck...")
			num_var, num_clauses, clauses = get_cnf_permutation_as_identity(perm_length, offset = offset_of_ordered_deck)
			permutations += [{"type": f"constraint_identity_matrix{ct_number+2}", "offset": 0, "num_var": num_var, "num_clauses": num_clauses, "clauses": clauses}]

			# create an array to hold the reconstructed pt
			if debug: print("Creating selectors for the pt...")
			selector_offsets_new_ct = []
			for i in range(other_pt_length):
				num_var, num_clauses, clauses = get_cnf_pt_selector(pt_alphabet_size, offset = total_var())
				selector_offsets_new_ct += [total_var()]
				permutations += [{"type": f"pt_selector{ct_number+2}", "offset": total_var(), "num_var": num_var, "num_clauses": num_clauses, "clauses": clauses}]
			all_other_selector_offsets += [selector_offsets_new_ct]

			# constrain the deck states sequentially as selector x permutation x old_deck = new_deck
			if debug: print("Constraining the deck with the pt selectors...")
			deck_offsets = lambda x: offset_of_ordered_deck if x == -1 else shuffled_deck_offsets[x]
			for i in range(other_pt_length):
				num_var, num_clauses, clauses = get_cnf_selector_permutation_product(perm_length, selectors = [selector_offsets_new_ct[i] + j for j in range(pt_alphabet_size)], offsets1 = pt_letter_permutation_matrix_offsets, offset2 = deck_offsets(i-1), offset3 = deck_offsets(i))
				permutations += [{"type": f"constraint_perm_matrix_product{ct_number+2}", "offset": 0, "num_var": num_var, "num_clauses": num_clauses, "clauses": clauses}]

			# constrain the cipher text
			if debug: print("Constraining the deck to the cipher text...")
			for i in range(other_pt_length):
				ct_letter = other_ct_array[i]

				num_var, num_clauses, clauses = get_cnf_ct_permutation_equality(perm_length, ct_letter, offset = shuffled_deck_offsets[i])
				permutations += [{"type": f"constraint_ct_letter{ct_number+2}", "offset": 0, "num_var": num_var, "num_clauses": num_clauses, "clauses": clauses}]

		
	# constrain the pt permutation matrices to map to unique letters
	if debug: print("Constraining the pt matrices to have unique top cards...")
	num_var, num_clauses, clauses = get_cnf_unique_top_card(perm_length, offsets = perm_matrix_offsets()[:pt_alphabet_size])
	permutations += [{"type": "constraint_unique_top_card", "offset": 0, "num_var": num_var, "num_clauses": num_clauses, "clauses": clauses}]

	# if this option is chosen, we add additional constraints on the pt permutation matrices
	# in short, we want to have one parent permutation that all the pt permutation matrices derive from
	# we set some number of rows in that they at most differ
	# so we need to add that parent permutation matrix, the row selector and what is basically a counter
	# to count the row selector
	# the row selector should be FALSE when the rows are forced equal and TRUE when they are free,
	# so (s v ~a v b) ^ (s v a v ~b) for a and b corresponding entries between permutation matrices should do that
	# (because s being TRUE trivially satisfies these and thus 'disables' the equality constraint)
	if related_permutations:
		# create parent permutation matrix
		if debug: print("Creating parent permutation matrix...")
		num_var, num_clauses, clauses = get_cnf_permutation(perm_length, offset = total_var())
		parent_permutation_offset = total_var()
		permutations += [{"type": "perm_matrix_parent", "offset": total_var(), "num_var": num_var, "num_clauses": num_clauses, "clauses": clauses}]
		
		if debug: print("Creating free row counters...")
		for i in range(pt_alphabet_size):
			# selectors are free variables
			offset = total_var()
			permutations += [{"type": "row_selectors", "offset": offset, "num_var": perm_length, "num_clauses": 0, "clauses": []}]

			# add a counter to the selectors
			row_selectors = [j+1 for j in range(offset, offset + perm_length)]
			num_var, num_clauses, clauses, outlist = get_cnf_totalizer(row_selectors, offset_out = total_var())
			permutations += [{"type": "row_selector_totalizer", "offset": total_var(), "num_var": num_var, "num_clauses": num_clauses, "clauses": clauses}]

			# set the counter (outlist) to the chosen number
			num_var, num_clauses, clauses = get_cnf_set_totalizer_counter(outlist, min_true = related_permutations_free_rows, max_true = related_permutations_free_rows)
			permutations += [{"type": "row_selector_constraints", "offset": 0, "num_var": num_var, "num_clauses": num_clauses, "clauses": clauses}]

			# set equality between the parent permutation matrix and the pt permutation matrix up to free row constraints
			num_var, num_clauses, clauses = get_cnf_permutation_equality_up_to_selector(perm_length, offset1 = parent_permutation_offset, offset2 = pt_letter_permutation_matrix_offsets[i], selector_list = row_selectors)
			permutations += [{"type": "row_selector_equality_constraints", "offset": 0, "num_var": num_var, "num_clauses": num_clauses, "clauses": clauses}]



	if debug: print("Writing CNF...")
	with open("permutation_test.cnf", "w") as f:
		f.write(f"p cnf {total_var()} {total_clauses()}\n")
		ac = all_clauses()
		for clause in ac:
			f.write(" ".join(list(map(str, clause))) + "\n")

	#print(clauses)

	if write_cnf_then_exit:
		print("Written CNF, exiting...")
		return {}

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
		parent_permutation = None
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
				elif p["type"] == "perm_matrix_parent":
					parent_permutation = permutation		

		if not use_known_pt:
			for n in expression.strip().split(" "):
				if (m := int(n)) != 0 and abs(m) >= selector_offsets[0] and abs(m) <= (selector_offsets[-1] + pt_alphabet_size):	
					selection_matrix[selector_code_to_pos(abs(m), selector_offsets[0])] = np.sign(m)

		if use_multiple_ct:
			all_selection_matrices = []
			for i, selector_offsets_new_ct in enumerate(all_other_selector_offsets):
				all_selection_matrices += [np.empty((list_other_pt_lengths[i], pt_alphabet_size), dtype = int)]
				for n in expression.strip().split(" "):	
					if (m := int(n)) != 0 and abs(m) >= selector_offsets_new_ct[0] and abs(m) <= (selector_offsets_new_ct[-1] + pt_alphabet_size):	
						all_selection_matrices[i][selector_code_to_pos(abs(m), selector_offsets_new_ct[0])] = np.sign(m)

		if use_known_pt:
			return {"satisfiable" : True, "permutation_table_reconstructed": permutation_table_reconstructed, "parent_permutation" : parent_permutation}

		else:
			# we need to use the reconstructed pt and the reconstructed permutation table to check
			reconstructed_pt = ""
			for row in selection_matrix:
				reconstructed_pt += pt_alphabet[np.nonzero(row == 1)[0][0]]

			if use_multiple_ct:
				other_reconstructed_pts = []
				for other_selection_matrix in all_selection_matrices:
					other_reconstructed_pt = ""
					for row in other_selection_matrix:
						other_reconstructed_pt += pt_alphabet[np.nonzero(row == 1)[0][0]]
					other_reconstructed_pts += [other_reconstructed_pt]

				return {"satisfiable" : True, "permutation_table_reconstructed": permutation_table_reconstructed, "reconstructed_pt" : reconstructed_pt, "parent_permutation" : parent_permutation, "other_reconstructed_pts" : other_reconstructed_pts}

			else:
				return {"satisfiable" : True, "permutation_table_reconstructed": permutation_table_reconstructed, "reconstructed_pt" : reconstructed_pt, "parent_permutation" : parent_permutation}
		
	else:
		# UNSATISFIABLE
		return {"satisfiable" : False}

def solve_sparse(use_known_pt, ct, ct_alphabet, pt_alphabet, pt = None, debug = True, write_cnf_then_exit = False, use_multiple_ct = False, other_cts = [], lazy_canonical_pt = False, cribs = [], other_cribs = [], write_cnf_incrementally = False, call_function_as_number_calculator = False, use_compression = False):
	# write_cnf_incrementally makes it such that the function writes the cnf incrementally which saves on memory when writing

	# basically the same as solve but we omit lower columns (cards) that dont matter anymore,
	# e.g. in this arbitrary deck evolution:
	#
	#   0 1 2 3 4        0 1 2 3 4
	#   1 2 3 . .        1 3 . . 2
	#   2 1 3 . .   or   2 . . 1 3   or   ...
	#   1 3 . . .        1 . . 3 .
	#   3 . . . .        3 . . . .
	# 
	# we dont actually care where 1 or 2 etc. are in the last deck state, and we dont care about most cards in the previous deck states either --> we can save on clauses and vars and dont actually permute those unused cards
	# but we do need the initial deck state

	# I want an option for a canonical pt or partially canonical pt...
	# --> lazy_canonical_pt

	call_optimized_getcnf_function = True

	## Next todo: other_cribs for the other pts if given

	# cribs and lazy_canonical_pt are mutually exclusive, throw error if both set
	if len(cribs) + len(other_cribs) > 0 and lazy_canonical_pt:
		raise Exception("Cribs and using a canonicalized pt are mutually exclusive!")

	TOTAL_NUM_VARIABLES = 0
	TOTAL_NUM_CLAUSES   = 0
	if write_cnf_incrementally:
		TOTAL_NUM_VARIABLES, TOTAL_NUM_CLAUSES = solve_sparse(use_known_pt, ct, ct_alphabet, pt_alphabet, pt, False, write_cnf_then_exit, use_multiple_ct, other_cts, lazy_canonical_pt, cribs, other_cribs, write_cnf_incrementally = False, call_function_as_number_calculator = True)

		print(f"{TOTAL_NUM_VARIABLES = }\n{TOTAL_NUM_CLAUSES = }")
		print("-"*10 + " starting write "  + "-"*10)
		#exit()

		# TODO: Write to CNF file
		if use_compression:
			#f = lzma.open("permutation_test.cnf.xz", "wt")
			f = lzma_mt.open("permutation_test.cnf.xz", "wt", threads = 13)
		else:
			f = open("permutation_test.cnf", "w")
		f.write(f"p cnf {TOTAL_NUM_VARIABLES} {TOTAL_NUM_CLAUSES}\n")

	clause_to_str_line = lambda x: " ".join(list(map(str, x)))
	clauses_to_str_lines = lambda x: "\n".join([clause_to_str_line(k) for k in x]) + "\n"

	if pt is not None: pt_array = dc.str_to_array(pt, pt_alphabet)
	ct_array = dc.str_to_array(ct, ct_alphabet)
	ct_alphabet_size = len(ct_alphabet)
	pt_alphabet_size = len(pt_alphabet)

	pt_length = len(ct) # using ct here to get the length because pt and ct have the same length anyways and ct is always given
	perm_length = ct_alphabet_size

	# -1 implies unknown
	crib_array = [-1 for i in range(pt_length)]
	for d in cribs:
		for i in range(len(d["val"])):
			crib_array[d["pos"] + i] = pt_alphabet.index(d["val"][i])

	other_crib_arrays = []
	for j in range(len(other_cts)):
		temp_crib_array = [-1 for i in range(pt_length)]
		if j < len(other_cribs):
			oc = other_cribs[j]
			for d in oc:
				for i in range(len(d["val"])):
					temp_crib_array[d["pos"] + i] = pt_alphabet.index(d["val"][i])
		other_crib_arrays += [temp_crib_array]

	# find out what cards are actually needed per deck state
	needed_cards = [[]]
	for c in ct_array[::-1]:
		temp = needed_cards[0].copy()
		if c not in temp: temp += [c]
		needed_cards = [sorted(temp)] + needed_cards
	needed_cards = [list(range(ct_alphabet_size))] + needed_cards[:-1]
	# --> needed cards now contains all the needed cards from state 0 to the final state of the deck
	# --> we need to keep track of them for the deck evolution
	# --> probably good to make a second list of exactly the same size and subsizes that hold the offsets

	# TODO: Continue
	if debug: print(f"{len(ct_array) = }")
	if debug: print(f"{len(needed_cards) = }")


	if use_multiple_ct:
		list_other_ct_arrays = []
		list_other_pt_lengths = []
		for c in other_cts:
			list_other_ct_arrays += [dc.str_to_array(c, ct_alphabet)]
			list_other_pt_lengths += [len(c)]


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
	if debug: print("Creating permutation matrices for pt letters...")
	for i in range(pt_alphabet_size):
		if debug: print(f"> Processing {i+1}/{pt_alphabet_size}")
		if not call_optimized_getcnf_function:
			if not call_function_as_number_calculator:
				num_var, num_clauses, clauses = get_cnf_permutation(perm_length, offset = total_var())

			else:
				num_var, num_clauses, clauses = get_cnf_permutation(perm_length, offset = total_var(), return_no_clauses = True)

				TOTAL_NUM_VARIABLES += num_var
				TOTAL_NUM_CLAUSES += num_clauses
			if write_cnf_incrementally and not call_function_as_number_calculator:
				f.write(clauses_to_str_lines(clauses))
				clauses = []
			permutations += [{"type": "perm_matrix", "offset": total_var(), "num_var": num_var, "num_clauses": num_clauses, "clauses": clauses}]
		else:
			# we dont care about readability, just speed
			if not call_function_as_number_calculator:
				num_var, num_clauses, clauses = get_cnf_permutation_optimized(perm_length, offset = total_var())

			else:
				num_var, num_clauses, clauses = get_cnf_permutation(perm_length, offset = total_var(), return_no_clauses = True)

				TOTAL_NUM_VARIABLES += num_var
				TOTAL_NUM_CLAUSES += num_clauses
			if write_cnf_incrementally and not call_function_as_number_calculator:
				f.write(clauses)
				clauses = []
			permutations += [{"type": "perm_matrix", "offset": total_var(), "num_var": num_var, "num_clauses": num_clauses, "clauses": clauses}]

	pt_letter_permutation_matrix_offsets = perm_matrix_offsets()

	# constrain the pt permutation matrices to map to unique letters
	if debug: print("Constraining the pt matrices to have unique top cards...")
	if not call_function_as_number_calculator:
		num_var, num_clauses, clauses = get_cnf_unique_top_card(perm_length, offsets = pt_letter_permutation_matrix_offsets)

	else:
		num_var, num_clauses, clauses = get_cnf_unique_top_card(perm_length, offsets = pt_letter_permutation_matrix_offsets, return_no_clauses = True)

		TOTAL_NUM_VARIABLES += num_var
		TOTAL_NUM_CLAUSES += num_clauses
	if write_cnf_incrementally and not call_function_as_number_calculator:
		f.write(clauses_to_str_lines(clauses))
		clauses = []
	permutations += [{"type": "constraint_unique_top_card", "offset": 0, "num_var": num_var, "num_clauses": num_clauses, "clauses": clauses}]

	# I think the concept now is to create permutation vectors instead, one vector for each letter we care about for each state of the deck
	# The letters we care about are in needed_cards

	if debug: print("Creating permutation vectors for needed cards...")
	deck_card_offsets = []
	for i in range(len(needed_cards)):
		# create the deck states
		if debug: print(f"> Processing {i+1}/{len(needed_cards)}")
		deck_card_offsets += [[]]
		for card in needed_cards[i]:
			# card is the cards we need
			if not call_function_as_number_calculator:
				num_var, num_clauses, clauses = get_cnf_permutation_vector(perm_length, offset = total_var())

			else:
				num_var, num_clauses, clauses = get_cnf_permutation_vector(perm_length, offset = total_var(), return_no_clauses = True)

				TOTAL_NUM_VARIABLES += num_var
				TOTAL_NUM_CLAUSES += num_clauses
			if write_cnf_incrementally and not call_function_as_number_calculator:
				f.write(clauses_to_str_lines(clauses))
				clauses = []
			deck_card_offsets[-1] += [total_var()]
			permutations += [{"type": f"perm_vector_layer{i}_card{card}", "offset": total_var(), "num_var": num_var, "num_clauses": num_clauses, "clauses": clauses}]

	# set the inital deck in an ordered state
	for i in range(len(needed_cards[0])):
		card_offset = deck_card_offsets[0][i]
		if not call_function_as_number_calculator:
			num_var, num_clauses, clauses = get_cnf_equality(card_offset + i + 1, val = True)

		else:
			num_var, num_clauses, clauses = get_cnf_equality(card_offset + i + 1, val = True, return_no_clauses = True)

			TOTAL_NUM_VARIABLES += num_var
			TOTAL_NUM_CLAUSES += num_clauses
		if write_cnf_incrementally and not call_function_as_number_calculator:
			f.write(clauses_to_str_lines(clauses))
			clauses = []
		permutations += [{"type": "constraint_ordered_deck", "offset": total_var(), "num_var": num_var, "num_clauses": num_clauses, "clauses": clauses}]


	# add constraint that no two deck cards per state can be in the same position
	for i in range(len(needed_cards)):
		if not call_function_as_number_calculator:
			num_var, num_clauses, clauses = get_cnf_permutation_vector_constraints(perm_length, offsets = deck_card_offsets[i])

		else:
			num_var, num_clauses, clauses = get_cnf_permutation_vector_constraints(perm_length, offsets = deck_card_offsets[i], return_no_clauses = True)

			TOTAL_NUM_VARIABLES += num_var
			TOTAL_NUM_CLAUSES += num_clauses
		if write_cnf_incrementally and not call_function_as_number_calculator:
			f.write(clauses_to_str_lines(clauses))
			clauses = []
		permutations += [{"type": "constraint_no_same_card_pos", "offset": total_var(), "num_var": num_var, "num_clauses": num_clauses, "clauses": clauses}]

	
	if use_known_pt:
		# worry about this later
		raise Exception("Not implemented yet")
		pass

	else:
		# If we do not wish to use the plain text, we need to create an array to hold the reconstructed pt
		if debug: print("Creating selectors for the pt...")
		selector_offsets = []
		for i in range(pt_length):
			if not call_function_as_number_calculator:
				num_var, num_clauses, clauses = get_cnf_pt_selector(pt_alphabet_size, offset = total_var())

			else:
				num_var, num_clauses, clauses = get_cnf_pt_selector(pt_alphabet_size, offset = total_var(), return_no_clauses = True)

				TOTAL_NUM_VARIABLES += num_var
				TOTAL_NUM_CLAUSES += num_clauses
			if write_cnf_incrementally and not call_function_as_number_calculator:
				f.write(clauses_to_str_lines(clauses))
				clauses = []
			selector_offsets += [total_var()]
			permutations += [{"type": "pt_selector", "offset": total_var(), "num_var": num_var, "num_clauses": num_clauses, "clauses": clauses}]

		if debug: print("Constraining the deck with the pt selectors...")
		# constrain the deck states sequentially as selector x permutation x old_deck = new_deck
		# --> here we need to instead do the vector multiplication

		# This seems to be by far the most expensive part of the operation
		# TODO: Also do this in the multiple ct section

		for i in range(len(needed_cards)-1):
			if debug: print(f"> Processing {i+1}/{len(needed_cards)-1}")

			if not call_optimized_getcnf_function:
				for j in range(len(needed_cards[i])):
					current_offset = deck_card_offsets[i][j]

					# find offset of card in the next layer
					next_cards = needed_cards[i+1]
					if needed_cards[i][j] not in next_cards: continue # the card does not appear in the next layer
					next_offset = deck_card_offsets[i+1][next_cards.index(needed_cards[i][j])]

					# contstrain as selector x permutation x old_card = new_card
					if not call_function_as_number_calculator:
						num_var, num_clauses, clauses =  get_cnf_selector_permutation_product_with_vector(perm_length, selectors = [selector_offsets[i] + j for j in range(pt_alphabet_size)], offsets1 = pt_letter_permutation_matrix_offsets, offset2 = current_offset, offset3 = next_offset)

					else:
						num_var, num_clauses, clauses =  get_cnf_selector_permutation_product_with_vector(perm_length, selectors = [selector_offsets[i] + j for j in range(pt_alphabet_size)], offsets1 = pt_letter_permutation_matrix_offsets, offset2 = current_offset, offset3 = next_offset, return_no_clauses = True)

						TOTAL_NUM_VARIABLES += num_var
						TOTAL_NUM_CLAUSES += num_clauses
					if write_cnf_incrementally and not call_function_as_number_calculator:
						f.write(clauses_to_str_lines(clauses))
						clauses = []
					permutations += [{"type": "constraint_perm_vector_product", "offset": 0, "num_var": num_var, "num_clauses": num_clauses, "clauses": clauses}]

			else:
				# here we dont really care about readability, just speed

				for j in range(len(needed_cards[i])):
					current_offset = deck_card_offsets[i][j]

					# find offset of card in the next layer
					next_cards = needed_cards[i+1]
					if needed_cards[i][j] not in next_cards: continue # the card does not appear in the next layer
					next_offset = deck_card_offsets[i+1][next_cards.index(needed_cards[i][j])]

					# contstrain as selector x permutation x old_card = new_card
					if not call_function_as_number_calculator:
						num_var, num_clauses, clauses =  get_cnf_selector_permutation_product_with_vector_optimized(perm_length, selectors = [selector_offsets[i] + j for j in range(pt_alphabet_size)], offsets1 = pt_letter_permutation_matrix_offsets, offset2 = current_offset, offset3 = next_offset)

					else:
						num_var, num_clauses, clauses =  get_cnf_selector_permutation_product_with_vector(perm_length, selectors = [selector_offsets[i] + j for j in range(pt_alphabet_size)], offsets1 = pt_letter_permutation_matrix_offsets, offset2 = current_offset, offset3 = next_offset, return_no_clauses = True)

						TOTAL_NUM_VARIABLES += num_var
						TOTAL_NUM_CLAUSES += num_clauses
					if write_cnf_incrementally and not call_function_as_number_calculator:
						f.write(clauses)
						clauses = []
					permutations += [{"type": "constraint_perm_vector_product", "offset": 0, "num_var": num_var, "num_clauses": num_clauses, "clauses": clauses}]


		# constrain the top card
		for i in range(pt_length):
			ct_letter = ct_array[i]

			card_offsets = deck_card_offsets[i+1]
			cards = needed_cards[i+1]

			offset = card_offsets[cards.index(ct_letter)]

			if not call_function_as_number_calculator:
				num_var, num_clauses, clauses =  get_cnf_equality(offset + 1, val = True)

			else:
				num_var, num_clauses, clauses =  get_cnf_equality(offset + 1, val = True, return_no_clauses = True)

				TOTAL_NUM_VARIABLES += num_var
				TOTAL_NUM_CLAUSES += num_clauses
			if write_cnf_incrementally and not call_function_as_number_calculator:
				f.write(clauses_to_str_lines(clauses))
				clauses = []
			permutations += [{"type": "constraint_ct_letter", "offset": 0, "num_var": num_var, "num_clauses": num_clauses, "clauses": clauses}]

		# lazily canonicalize pt
		# set upper right triangle in pt selectors to false because it is possible WLOG
		if lazy_canonical_pt:
			for i in range(min(pt_alphabet_size-1, pt_length)):
				#print("DEBUG-------------------!")
				set_to_zero = list(range(selector_offsets[i] + i + 1, selector_offsets[i] + pt_alphabet_size))
				for offset in set_to_zero:
					if not call_function_as_number_calculator:
						num_var, num_clauses, clauses =  get_cnf_equality(offset + 1, val = False)

					else:
						num_var, num_clauses, clauses =  get_cnf_equality(offset + 1, val = False, return_no_clauses = True)

						TOTAL_NUM_VARIABLES += num_var
						TOTAL_NUM_CLAUSES += num_clauses
					if write_cnf_incrementally and not call_function_as_number_calculator:
						f.write(clauses_to_str_lines(clauses))
						clauses = []
					permutations += [{"type": "constraint_lazy_canonical_pt", "offset": 0, "num_var": num_var, "num_clauses": num_clauses, "clauses": clauses}]

		# process cribs
		if debug: print("Adding cribs...")
		for i, crib in enumerate(crib_array):
			if crib == -1: continue
			if not call_function_as_number_calculator:
				num_var, num_clauses, clauses = get_cnf_equality(selector_offsets[i] + crib + 1)

			else:
				num_var, num_clauses, clauses = get_cnf_equality(selector_offsets[i] + crib + 1, return_no_clauses = True)

				TOTAL_NUM_VARIABLES += num_var
				TOTAL_NUM_CLAUSES += num_clauses
			if write_cnf_incrementally and not call_function_as_number_calculator:
				f.write(clauses_to_str_lines(clauses))
				clauses = []
			permutations += [{"type": "constraint_crib", "offset": 0, "num_var": num_var, "num_clauses": num_clauses, "clauses": clauses}]


	# if we are given multiple cipher texts, we want to have another deck, plaintext selectors, etc., but reuse the plaintext permutation matrices (so one permutation table has to decrypt multiple messages)
	if use_multiple_ct:
		if debug: print("Processing additional cts...")
		all_other_selector_offsets = []
		for ct_number, other_ct_array in enumerate(list_other_ct_arrays):
			print(f"Processing additional ct {ct_number+1}/{len(list_other_ct_arrays)}...")

			other_pt_length = list_other_pt_lengths[ct_number]

			other_needed_cards = [[]]
			for c in other_ct_array[::-1]:
				temp = other_needed_cards[0].copy()
				if c not in temp: temp += [c]
				other_needed_cards = [sorted(temp)] + other_needed_cards
			other_needed_cards = [list(range(ct_alphabet_size))] + other_needed_cards[:-1]

			# create the deck
			# create the states of the shuffled deck
			if debug: print("Creating permutation vectors for needed cards...")

			other_deck_card_offsets = []
			for i in range(len(other_needed_cards)):
				# create the deck states
				if debug: print(f"> Processing {i+1}/{len(other_needed_cards)}")
				other_deck_card_offsets += [[]]
				for card in other_needed_cards[i]:
					# card is the cards we need
					if not call_function_as_number_calculator:
						num_var, num_clauses, clauses = get_cnf_permutation_vector(perm_length, offset = total_var())

					else:
						num_var, num_clauses, clauses = get_cnf_permutation_vector(perm_length, offset = total_var(), return_no_clauses = True)

						TOTAL_NUM_VARIABLES += num_var
						TOTAL_NUM_CLAUSES += num_clauses
					if write_cnf_incrementally and not call_function_as_number_calculator:
						f.write(clauses_to_str_lines(clauses))
						clauses = []
					other_deck_card_offsets[-1] += [total_var()]
					permutations += [{"type": f"perm_vector_ct{ct_number}_layer{i}_card{card}", "offset": total_var(), "num_var": num_var, "num_clauses": num_clauses, "clauses": clauses}]

			# set the inital deck in an ordered state
			for i in range(len(other_needed_cards[0])):
				card_offset = other_deck_card_offsets[0][i]
				if not call_function_as_number_calculator:
					num_var, num_clauses, clauses = get_cnf_equality(card_offset + i + 1, val = True)

				else:
					num_var, num_clauses, clauses = get_cnf_equality(card_offset + i + 1, val = True, return_no_clauses = True)

					TOTAL_NUM_VARIABLES += num_var
					TOTAL_NUM_CLAUSES += num_clauses
				if write_cnf_incrementally and not call_function_as_number_calculator:
					f.write(clauses_to_str_lines(clauses))
					clauses = []
				permutations += [{"type": f"constraint_ordered_deck_ct{ct_number}", "offset": total_var(), "num_var": num_var, "num_clauses": num_clauses, "clauses": clauses}]

			# add constraint that no two deck cards per state can be in the same position
			for i in range(len(other_needed_cards)):
				if not call_function_as_number_calculator:
					num_var, num_clauses, clauses = get_cnf_permutation_vector_constraints(perm_length, offsets = other_deck_card_offsets[i])

				else:
					num_var, num_clauses, clauses = get_cnf_permutation_vector_constraints(perm_length, offsets = other_deck_card_offsets[i], return_no_clauses = True)

					TOTAL_NUM_VARIABLES += num_var
					TOTAL_NUM_CLAUSES += num_clauses
				if write_cnf_incrementally and not call_function_as_number_calculator:
					f.write(clauses_to_str_lines(clauses))
					clauses = []
				permutations += [{"type": "constraint_no_same_card_pos", "offset": total_var(), "num_var": num_var, "num_clauses": num_clauses, "clauses": clauses}]

			# If we do not wish to use the plain text, we need to create an array to hold the reconstructed pt
			if debug: print("Creating selectors for the pt...")
			other_selector_offsets = []
			for i in range(other_pt_length):
				if not call_function_as_number_calculator:
					num_var, num_clauses, clauses = get_cnf_pt_selector(pt_alphabet_size, offset = total_var())

				else:
					num_var, num_clauses, clauses = get_cnf_pt_selector(pt_alphabet_size, offset = total_var(), return_no_clauses = True)

					TOTAL_NUM_VARIABLES += num_var
					TOTAL_NUM_CLAUSES += num_clauses
				if write_cnf_incrementally and not call_function_as_number_calculator:
					f.write(clauses_to_str_lines(clauses))
					clauses = []
				other_selector_offsets += [total_var()]
				permutations += [{"type": f"pt_selector_ct{ct_number}", "offset": total_var(), "num_var": num_var, "num_clauses": num_clauses, "clauses": clauses}]
			all_other_selector_offsets += [other_selector_offsets]

			# constrain the deck states sequentially as selector x permutation x old_deck = new_deck
			# --> here we need to instead do the vector multiplication

			if debug: print("Constraining the deck with the pt selectors...")
			if not call_optimized_getcnf_function:
				for i in range(len(other_needed_cards)-1):
					for j in range(len(other_needed_cards[i])):
						current_offset = other_deck_card_offsets[i][j]

						# find offset of card in the next layer
						next_cards = other_needed_cards[i+1]
						if other_needed_cards[i][j] not in next_cards: continue # the card does not appear in the next layer
						next_offset = other_deck_card_offsets[i+1][next_cards.index(other_needed_cards[i][j])]

						# contstrain as selector x permutation x old_card = new_card
						if not call_function_as_number_calculator:
							num_var, num_clauses, clauses =  get_cnf_selector_permutation_product_with_vector(perm_length, selectors = [other_selector_offsets[i] + j for j in range(pt_alphabet_size)], offsets1 = pt_letter_permutation_matrix_offsets, offset2 = current_offset, offset3 = next_offset)

						else:
							num_var, num_clauses, clauses =  get_cnf_selector_permutation_product_with_vector(perm_length, selectors = [other_selector_offsets[i] + j for j in range(pt_alphabet_size)], offsets1 = pt_letter_permutation_matrix_offsets, offset2 = current_offset, offset3 = next_offset, return_no_clauses = True)

							TOTAL_NUM_VARIABLES += num_var
							TOTAL_NUM_CLAUSES += num_clauses
						if write_cnf_incrementally and not call_function_as_number_calculator:
							f.write(clauses_to_str_lines(clauses))
							clauses = []
						permutations += [{"type": "constraint_perm_vector_product", "offset": 0, "num_var": num_var, "num_clauses": num_clauses, "clauses": clauses}]
			else:
				# we dont care about readability, just speed
				for i in range(len(other_needed_cards)-1):
					if debug: print(f"> Processing {i+1}/{len(other_needed_cards)-1}")
					for j in range(len(other_needed_cards[i])):
						current_offset = other_deck_card_offsets[i][j]

						# find offset of card in the next layer
						next_cards = other_needed_cards[i+1]
						if other_needed_cards[i][j] not in next_cards: continue # the card does not appear in the next layer
						next_offset = other_deck_card_offsets[i+1][next_cards.index(other_needed_cards[i][j])]

						# contstrain as selector x permutation x old_card = new_card
						if not call_function_as_number_calculator:
							num_var, num_clauses, clauses =  get_cnf_selector_permutation_product_with_vector_optimized(perm_length, selectors = [other_selector_offsets[i] + j for j in range(pt_alphabet_size)], offsets1 = pt_letter_permutation_matrix_offsets, offset2 = current_offset, offset3 = next_offset)

						else:
							num_var, num_clauses, clauses =  get_cnf_selector_permutation_product_with_vector(perm_length, selectors = [other_selector_offsets[i] + j for j in range(pt_alphabet_size)], offsets1 = pt_letter_permutation_matrix_offsets, offset2 = current_offset, offset3 = next_offset, return_no_clauses = True)

							TOTAL_NUM_VARIABLES += num_var
							TOTAL_NUM_CLAUSES += num_clauses
						if write_cnf_incrementally and not call_function_as_number_calculator:
							f.write(clauses)
							clauses = []
						permutations += [{"type": "constraint_perm_vector_product", "offset": 0, "num_var": num_var, "num_clauses": num_clauses, "clauses": clauses}]

					# uhhhh not sure if selector_offsets should start at zero probably one shorter

			if debug: print("Constraining the deck to the cipher text...")
			# constrain the top card
			for i in range(other_pt_length):
				ct_letter = other_ct_array[i]

				card_offsets = other_deck_card_offsets[i+1]
				cards = other_needed_cards[i+1]

				offset = card_offsets[cards.index(ct_letter)]

				if not call_function_as_number_calculator:
					num_var, num_clauses, clauses =  get_cnf_equality(offset + 1, val = True)

				else:
					num_var, num_clauses, clauses =  get_cnf_equality(offset + 1, val = True, return_no_clauses = True)

					TOTAL_NUM_VARIABLES += num_var
					TOTAL_NUM_CLAUSES += num_clauses
				if write_cnf_incrementally and not call_function_as_number_calculator:
					f.write(clauses_to_str_lines(clauses))
					clauses = []
				permutations += [{"type": "constraint_ct_letter", "offset": 0, "num_var": num_var, "num_clauses": num_clauses, "clauses": clauses}]

			# process cribs
			if debug: print("Adding cribs...")
			for i, crib in enumerate(other_crib_arrays[ct_number]):
				if crib == -1: continue
				if not call_function_as_number_calculator:
					num_var, num_clauses, clauses = get_cnf_equality(other_selector_offsets[i] + crib + 1)

				else:
					num_var, num_clauses, clauses = get_cnf_equality(other_selector_offsets[i] + crib + 1, return_no_clauses = True)

					TOTAL_NUM_VARIABLES += num_var
					TOTAL_NUM_CLAUSES += num_clauses
				if write_cnf_incrementally and not call_function_as_number_calculator:
					f.write(clauses_to_str_lines(clauses))
					clauses = []
				permutations += [{"type": "constraint_crib", "offset": 0, "num_var": num_var, "num_clauses": num_clauses, "clauses": clauses}]


	if call_function_as_number_calculator:
		return TOTAL_NUM_VARIABLES, int(TOTAL_NUM_CLAUSES)

	if not write_cnf_incrementally:
		if debug: print("Writing CNF...")
		if use_compression:
			with lzma.open("permutation_test.cnf", "wt") as f:
				f.write(f"p cnf {total_var()} {total_clauses()}\n")
				ac = all_clauses()
				for clause in ac:
					f.write(" ".join(list(map(str, clause))) + "\n")
		else:
			with open("permutation_test.cnf", "w") as f:
				f.write(f"p cnf {total_var()} {total_clauses()}\n")
				ac = all_clauses()
				for clause in ac:
					f.write(" ".join(list(map(str, clause))) + "\n")
	else:
		f.close()

	#print(clauses)

	if write_cnf_then_exit:
		print("Written CNF, exiting...")
		return {}

	if debug: print("Running kissat...")
	if not use_compression:
		subprocess.run(["./run_kissat_permutation.sh"])
	else:
		subprocess.run(["./run_kissat_permutation_compressed.sh"])

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
		parent_permutation = None
		selection_matrix = np.empty((pt_length, pt_alphabet_size), dtype = int)

		sparse_deck = np.full((pt_length+1, ct_alphabet_size), -1, dtype = int)

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
				elif p["type"] == "perm_matrix_parent":
					parent_permutation = permutation

			elif p["type"].startswith("perm_vector_layer"):
				permutation_vector = np.empty(perm_length, dtype = int)
				for n in expression.strip().split(" "):
					if abs(m := int(n)) < sum([d["num_var"] for d in permutations[:i+1]]) + 1 and abs(m) >= p["offset"] and m != 0:				
						permutation_vector[code_to_pos(abs(m), p["offset"])[1]] = np.sign(m)
				pos = np.nonzero(permutation_vector > 0)[0][0]
				#print(f"pos {p['type']} = {pos}")

				layer, card = list(map(int, p["type"].replace("perm_vector_layer", "").replace("card", "").split("_")))
				sparse_deck[layer, pos] = card

		print("Reconstructed sparse deck:")
		print(sparse_deck)

		if not use_known_pt:
			for n in expression.strip().split(" "):
				if (m := int(n)) != 0 and abs(m) >= selector_offsets[0] and abs(m) <= (selector_offsets[-1] + pt_alphabet_size):	
					selection_matrix[selector_code_to_pos(abs(m), selector_offsets[0])] = np.sign(m)

		if use_multiple_ct:
			all_selection_matrices = []
			for i, selector_offsets_new_ct in enumerate(all_other_selector_offsets):
				all_selection_matrices += [np.empty((list_other_pt_lengths[i], pt_alphabet_size), dtype = int)]
				for n in expression.strip().split(" "):	
					if (m := int(n)) != 0 and abs(m) >= selector_offsets_new_ct[0] and abs(m) <= (selector_offsets_new_ct[-1] + pt_alphabet_size):	
						all_selection_matrices[i][selector_code_to_pos(abs(m), selector_offsets_new_ct[0])] = np.sign(m)

		if use_known_pt:
			return {"satisfiable" : True, "permutation_table_reconstructed": permutation_table_reconstructed, "parent_permutation" : parent_permutation}

		else:
			# we need to use the reconstructed pt and the reconstructed permutation table to check
			reconstructed_pt = ""
			for row in selection_matrix:
				reconstructed_pt += pt_alphabet[np.nonzero(row == 1)[0][0]]

			if use_multiple_ct:
				other_reconstructed_pts = []
				for other_selection_matrix in all_selection_matrices:
					other_reconstructed_pt = ""
					for row in other_selection_matrix:
						other_reconstructed_pt += pt_alphabet[np.nonzero(row == 1)[0][0]]
					other_reconstructed_pts += [other_reconstructed_pt]

				return {"satisfiable" : True, "permutation_table_reconstructed": permutation_table_reconstructed, "reconstructed_pt" : reconstructed_pt, "parent_permutation" : parent_permutation, "other_reconstructed_pts" : other_reconstructed_pts}

			else:
				return {"satisfiable" : True, "permutation_table_reconstructed": permutation_table_reconstructed, "reconstructed_pt" : reconstructed_pt, "parent_permutation" : parent_permutation}
		
	else:
		# UNSATISFIABLE
		return {"satisfiable" : False}



def solve_with_omflip():
	# express the problem using omega-flip networks to calculate the permutations instead of matrix multiplication

	pass

	# structure:
	# deck: per state array of 128x7 where the last 42 bits are all set to 1 and the first are all set to 0,1,2...82 in binary
	# make as many deck states as needed and connect them via omega-flip permutation networks
	# the selection variables introduced here are connected to the pt selectors
	# finally set the other restrictions like the top card in the deck states
	# issue: idk how I would encode the fact that no two permutations can have the same top card (reversibility reasons)...



def analyse_result(use_known_pt, ct_alphabet, ct, pt_alphabet, pt = None, permutation_table = None, permutation_table_reconstructed = None, reconstructed_pt = None, satisfiable = None, parent_permutation = None, use_multiple_ct = False, other_cts = [], other_reconstructed_pts = [], other_pts = []):
	if parent_permutation is not None:
		print("Parent permutation:")
		print(np.array(parent_permutation))
	print("Reconstructed permutation table:")
	print(permutation_table_reconstructed)
	print("Original permutation table (if given):")
	print(permutation_table)

	if satisfiable == False:
		return

	if use_known_pt:
		pt_array_from_reconstructed_permutation_table = dc.decrypt(ct_array, permutation_table_reconstructed)
		pt_from_reconstructed_permutation_table = dc.array_to_str(pt_array_from_reconstructed_permutation_table, pt_alphabet)

		# we need to use the original pt to check the permutation table
		print("Decrypting ct with reconstructed permutation table:")
		print(f"{pt_from_reconstructed_permutation_table = }")
		print(f"Correct decryption: {pt_from_reconstructed_permutation_table == pt}")

		return

	# we need to use the reconstructed pt and the reconstructed permutation table to check
	reconstructed_pt_array = dc.str_to_array(reconstructed_pt, pt_alphabet)
	reconstructed_ct_array = dc.encrypt(reconstructed_pt_array, permutation_table_reconstructed)
	reconstructed_ct = dc.array_to_str(reconstructed_ct_array, ct_alphabet)

	if pt is not None: print(f"{pt               = }")
	print(f"{reconstructed_pt = }")
	print(f"{ct               = }")
	print(f"{reconstructed_ct = }")

	print(f"Correct ct reproduction: {ct == reconstructed_ct}")
	#print("-"*10)

	if pt is not None: print(f"pt isomorph code               = '{dc.get_isomorph_code(pt)}'")
	if pt is not None: print(f"reconstructed pt isomorph code = '{dc.get_isomorph_code(reconstructed_pt)}'")
	if pt is not None: print(f"reconstructed pt is monoalphabetic substitution of pt: {dc.get_isomorph_code(pt) == dc.get_isomorph_code(reconstructed_pt)}")

	if use_multiple_ct:
		for i, c in enumerate(other_cts):
			print("-"*10 + f" for ct {i+2} " + "-"*10)
			reconstructed_pt = other_reconstructed_pts[i]
			reconstructed_pt_array = dc.str_to_array(reconstructed_pt, pt_alphabet)
			reconstructed_ct_array = dc.encrypt(reconstructed_pt_array, permutation_table_reconstructed)
			reconstructed_ct = dc.array_to_str(reconstructed_ct_array, ct_alphabet)
			
			if len(other_pts) > 0: print(f"pt               = '{other_pts[i]}'")
			print(f"{reconstructed_pt = }")
			print(f"ct               = '{c}'")
			print(f"{reconstructed_ct = }")

			print(f"Correct ct reproduction: {c == reconstructed_ct}")

			if len(other_pts) > 0:
				other_pt = other_pts[i]
				print(f"pt isomorph code               = '{dc.get_isomorph_code(other_pt)}'")
				print(f"reconstructed pt isomorph code = '{dc.get_isomorph_code(reconstructed_pt)}'")
				print(f"reconstructed pt is monoalphabetic substitution of pt: {dc.get_isomorph_code(other_pt) == dc.get_isomorph_code(reconstructed_pt)}")


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

def fun1_reconstruct_pt():
	# Try to reconstruct some plaintext and permutation table from some ciphertext
	pt = "aaaaaaaaa"
	pt_alphabet = "ab"
	ct_alphabet = "ABCD"
	ct, permutation_table = generate_some_ct(pt, pt_alphabet, ct_alphabet, seed = 0, double_free = True, debug = True)
	result = solve(use_known_pt = False, ct = ct, ct_alphabet = ct_alphabet, pt = pt, pt_alphabet = pt_alphabet, permutation_table = permutation_table, cribs = [], debug = True)
	analyse_result(use_known_pt = False, ct = ct, ct_alphabet = ct_alphabet, pt = pt, pt_alphabet = pt_alphabet, permutation_table = permutation_table, **result)

def fun2_calculate_reachable_and_unreachable_ct():
	# calculate the number of reachable and unreachable ciphertexts for some pt_alphabet and ct_alphabet as well as 
	result_dict = {}
	l_stats = {}

	pt_alphabet = "abcd"
	ct_alphabet = "ABCDE"

	unsat_prefixes = []

	for max_ct_len in range(1, 11):
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


def fun3_adversarial_ct_generation():
	# adversarial ct generation

	pt_alphabet = "abcd"
	ct_alphabet = "ABCDE"

	min_length = None
	min_ct = None
	for j in range(1):
		#ct = "".join([ct_alphabet[x] for x in np.random.randint(0, len(ct_alphabet), size = 2)]) # low(incl.) - high(excl.)
		ct = "A"
		max_attempt_len = 100
		for i in range(max_attempt_len):
			print(f"Attempted length {i}")
			result = solve(use_known_pt = False, ct = ct, ct_alphabet = ct_alphabet, pt = None, pt_alphabet = pt_alphabet, permutation_table = None, cribs = [], debug = False)
			if not result["satisfiable"]: break
			pt = result["reconstructed_pt"]
			permutation_table = result["permutation_table_reconstructed"]
			ct_array, deck = dc.encrypt(dc.str_to_array(pt, pt_alphabet), permutation_table, return_deck = True)
			for k in range(len(ct_alphabet)):
				if k not in permutation_table[:,0]:
					ct += ct_alphabet[deck[k]]
					break
		if min_length is None or min_length > len(ct):
			min_length = len(ct)
			min_ct = ct
		print(len(ct)-1)
		#print(f"estimated longest guaranteed valid ct for pt_alphabet_size = {len(pt_alphabet)} and ct_alphabet_size = {len(ct_alphabet)} (found unsat example '{ct}'):\n{len(ct)-1}")
	print(f"L_0({len(pt_alphabet)},{len(ct_alphabet)}) ≤ {min_length-1}")
	print(ct)

def fun4_does_lzero_depend_on_ct_alphabet_size():
	# calculate the number of reachable and unreachable ciphertexts for some pt_alphabet and ct_alphabet as well as 
	result_dict = {}
	l_stats = {}

	pt_alphabet       = "abc"
	ct_alphabet_small = "ABCD"
	ct_alphabet       = "ABCDE"

	unsat_prefixes = []

	break_outer_loop = False
	for max_ct_len in range(1, 10):
		l_stats[max_ct_len] = {True: 0, False: 0}
		m = len(ct_alphabet_small)**max_ct_len
		for i in range(m):
			ct = ""
			k = i
			for j in range(max_ct_len):
				r = k%len(ct_alphabet_small)
				ct = ct_alphabet_small[r] + ct
				k = k//len(ct_alphabet_small)
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

			distinct_letters_in_ct = 0
			l = []
			for c in ct:
				if c not in l:
					l += [c]
					distinct_letters_in_ct += 1

			if distinct_letters_in_ct == len(ct_alphabet_small) and not result["satisfiable"]:
				print(f"UNSAT ct found with {distinct_letters_in_ct} symbols, {ct = }")
				break_outer_loop = True
				break
		if break_outer_loop: break

		#print(l_stats)

	#print("Finish")
	#print(result_dict)
	#print(l_stats)

def fun5_reconstruct_pt_with_limited_transpositions():
	pt_alphabet = "abcdefgh"
	ct_alphabet = "ABCDEFGHIJK"
	#pt = "gbacggfeadabebageddfabgaeefgf"

	rng = np.random.default_rng(seed = 1)
	t = rng.choice(len(pt_alphabet), size = 20)
	pt = ""
	for x in t:
		pt += pt_alphabet[x]

	print(pt)

	#permutation_table = dc.get_permutation_table_with_swaps(len(ct_alphabet), len(pt_alphabet), seed = 0, double_free = False, swaps_from_parent = 8)
	permutation_table = dc.get_permutation_table(len(ct_alphabet), len(pt_alphabet), seed = 0, double_free = False)
	pt_array = dc.str_to_array(pt, pt_alphabet)
	ct_array = dc.encrypt(pt_array, permutation_table)
	ct = dc.array_to_str(ct_array, ct_alphabet)

	print(ct)

	result = solve(use_known_pt = False, ct = ct, ct_alphabet = ct_alphabet, pt = None, pt_alphabet = pt_alphabet, permutation_table = None, cribs = [], debug = True, related_permutations = True, related_permutations_free_rows = 3)
	analyse_result(use_known_pt = False, ct = ct, ct_alphabet = ct_alphabet, pt = pt, pt_alphabet = pt_alphabet, permutation_table = permutation_table, **result)

	# sanity check: it really is a restriction on the permutation space.
	# for example, pt = "deghabghbcgdcgcdfeaa" --> ct = "AEDAGIBDHKBBAHJJCBJF" with pt_alphabet = "abcdefgh", ct_alphabet = "ABCDEFGHIJK" (from the permutation table below) cannot be reconstructed using only two free rows:
	# [[ 5 10  9  8  1  4  6  7  2  0  3]
	#  [ 2 10  3  6  0  8  4  9  7  5  1]
	#  [ 7  9  3  5  4 10  0  8  2  1  6]
	#  [ 0  8  6  5  4  9  7  2  3  1 10]
	#  [ 4  7  9  3  6 10  1  2  5  8  0]
	#  [ 1  9  5  4  6  2  3  8  7 10  0]
	#  [ 9  3  1  2  8  7  0  5  6  4 10]
	#  [10  7  1  6  3  5  9  2  4  8  0]]
	# but it can be done with three free rows!

def fun6_solve_parallel_ct():
	pt = "abbbacaba"
	pt_alphabet = "abc"
	ct_alphabet = "ABCD"
	ct, permutation_table = generate_some_ct(pt, pt_alphabet, ct_alphabet, seed = 0, double_free = True, debug = True)
	
	pt2 = "bbaccbb"
	pt2_array = dc.str_to_array(pt2, pt_alphabet)
	ct2_array = dc.encrypt(pt2_array, permutation_table)

	ct2 = dc.array_to_str(ct2_array, ct_alphabet)

	print(ct)
	print(ct2)

	result = solve(use_known_pt = False, ct = ct, ct_alphabet = ct_alphabet, pt = None, pt_alphabet = pt_alphabet, permutation_table = None, cribs = [], debug = True, related_permutations = False, use_multiple_ct = True, other_cts = [ct2])
	analyse_result(use_known_pt = False, ct = ct, ct_alphabet = ct_alphabet, pt = pt, pt_alphabet = pt_alphabet, permutation_table = permutation_table, use_multiple_ct = True, other_cts = [ct2], other_pts = [pt2], **result)


def fun7_test_cnf_size():
	pt_alphabet = "".join([chr(i+97) for i in range(26)]) + " "
	ct_alphabet = "".join([chr(i+33) for i in range(83)])
	ct = "hi"

	print(pt_alphabet)
	print(ct_alphabet)

	solve(use_known_pt = False, ct = ct, ct_alphabet = ct_alphabet, pt = None, pt_alphabet = pt_alphabet, permutation_table = None, cribs = [], debug = True, write_cnf_then_exit = True)


def fun8_another_parallel_solve():
	pt = "plaintextplaintext"
	pt_alphabet = "aeilnptx"
	ct_alphabet = "ABCDEFGHIJK"
	ct, permutation_table = generate_some_ct(pt, pt_alphabet, ct_alphabet, seed = 0, double_free = True, debug = True)
	
	pt2 = "textplaintext"
	pt2_array = dc.str_to_array(pt2, pt_alphabet)
	ct2_array = dc.encrypt(pt2_array, permutation_table)
	ct2 = dc.array_to_str(ct2_array, ct_alphabet)

	pt3 = "ptptnilltxt"
	pt3_array = dc.str_to_array(pt3, pt_alphabet)
	ct3_array = dc.encrypt(pt3_array, permutation_table)
	ct3 = dc.array_to_str(ct3_array, ct_alphabet)

	print(ct)
	print(ct2)
	print(ct3)

	result = solve(use_known_pt = False, ct = ct, ct_alphabet = ct_alphabet, pt = None, pt_alphabet = pt_alphabet, permutation_table = None, cribs = [], debug = True, related_permutations = False, use_multiple_ct = True, other_cts = [ct2, ct3])
	analyse_result(use_known_pt = False, ct = ct, ct_alphabet = ct_alphabet, pt = pt, pt_alphabet = pt_alphabet, permutation_table = permutation_table, use_multiple_ct = True, other_cts = [ct2, ct3], other_pts = [pt2, pt3], **result)

def fun9_compare_solve_and_sparse_solve():
	pt_alphabet = "abcd"
	ct_alphabet = "ABCDEFG"
	ct = "AEBACDCADAEDEBEDEACBDACDBABCABCBC"
	result = solve_sparse(use_known_pt = False, ct = ct, ct_alphabet = ct_alphabet, pt_alphabet = pt_alphabet, debug = True, write_cnf_then_exit = False)
	result2 = solve(use_known_pt = False, ct = ct, ct_alphabet = ct_alphabet, pt_alphabet = pt_alphabet, debug = True, write_cnf_then_exit = False)
	print("-"*20 + "SPARSE RESULT" + "-"*20)
	analyse_result(use_known_pt = False, ct = ct, ct_alphabet = ct_alphabet, pt = None, pt_alphabet = pt_alphabet, permutation_table = None, **result)
	print("-"*20 + "NONSPARSE RESULT" + "-"*20)
	analyse_result(use_known_pt = False, ct = ct, ct_alphabet = ct_alphabet, pt = None, pt_alphabet = pt_alphabet, permutation_table = None, **result2)

def fun10_solve_sparse_parallel_ct():
	pt = "abdbbacabaddcbaac"
	pt_alphabet = "abcd"
	ct_alphabet = "ABCDEF"
	ct, permutation_table = generate_some_ct(pt, pt_alphabet, ct_alphabet, seed = 0, double_free = True, debug = True)
	
	pt2 = "bdbadccbdbccabdcdd"
	pt2_array = dc.str_to_array(pt2, pt_alphabet)
	ct2_array = dc.encrypt(pt2_array, permutation_table)
	ct2 = dc.array_to_str(ct2_array, ct_alphabet)

	pt3 = "cbdbadccbdbccabdcdd"
	pt3_array = dc.str_to_array(pt3, pt_alphabet)
	ct3_array = dc.encrypt(pt3_array, permutation_table)
	ct3 = dc.array_to_str(ct3_array, ct_alphabet)

	print(ct)
	print(ct2)
	print(ct3)

	result = solve_sparse(use_known_pt = False, ct = ct, ct_alphabet = ct_alphabet, pt = None, pt_alphabet = pt_alphabet, debug = True, use_multiple_ct = True, other_cts = [ct2, ct3], lazy_canonical_pt = False, cribs = [{"pos" : 1, "val": "bdb"}], other_cribs = [[{"pos" : 0, "val": "bdba"}], [{"pos" : 2, "val": "dba"}]])
	analyse_result(use_known_pt = False, ct = ct, ct_alphabet = ct_alphabet, pt = pt, pt_alphabet = pt_alphabet, permutation_table = permutation_table, use_multiple_ct = True, other_cts = [ct2, ct3], other_pts = [pt2, pt3], **result)


def fun11_encode_eyes():
	import eye_data as eyes
	import deckcipher as dc

	pt_alphabet = "".join([chr(i) for i in range(65, 65+26)])
	ct_alphabet = "".join([chr(i) for i in range(33, 33+83)])

	ct1 = dc.array_to_str(eyes.west_1, ct_alphabet)
	ct2 = dc.array_to_str(eyes.east_1, ct_alphabet)
	ct3 = dc.array_to_str(eyes.west_2, ct_alphabet)
	ct4 = dc.array_to_str(eyes.east_2, ct_alphabet)
	ct5 = dc.array_to_str(eyes.west_3, ct_alphabet)
	ct6 = dc.array_to_str(eyes.east_3, ct_alphabet)
	ct7 = dc.array_to_str(eyes.west_4, ct_alphabet)
	ct8 = dc.array_to_str(eyes.east_4, ct_alphabet)
	ct9 = dc.array_to_str(eyes.east_5, ct_alphabet)

	solve_sparse(use_known_pt = False, ct = ct1, ct_alphabet = ct_alphabet, pt = None, pt_alphabet = pt_alphabet, debug = True, use_multiple_ct = True, other_cts = [ct2, ct3, ct4, ct5, ct6, ct7, ct8, ct9], lazy_canonical_pt = False, write_cnf_then_exit = True, write_cnf_incrementally = True, use_compression = True)

	#import cProfile
	#import pstats

	#with cProfile.Profile() as profile:
	#	solve_sparse(use_known_pt = False, ct = ct, ct_alphabet = ct_alphabet, pt = None, pt_alphabet = pt_alphabet, debug = True, use_multiple_ct = False, other_cts = [], lazy_canonical_pt = False, write_cnf_then_exit = True, write_cnf_incrementally = True, use_compression = True)
		
	#results = pstats.Stats(profile)
	#results.sort_stats(pstats.SortKey.TIME)
	#results.print_stats(10)
	


if __name__ == "__main__":
	#fun1_reconstruct_pt()
	#fun2_calculate_reachable_and_unreachable_ct()
	#fun3_adversarial_ct_generation()
	#fun4_does_lzero_depend_on_ct_alphabet_size()
	#fun5_reconstruct_pt_with_limited_transpositions()
	#fun6_solve_parallel_ct()
	#fun7_test_cnf_size()
	#fun8_another_parallel_solve()
	#fun9_compare_solve_and_sparse_solve()
	#fun10_solve_sparse_parallel_ct()

	fun11_encode_eyes()

	
