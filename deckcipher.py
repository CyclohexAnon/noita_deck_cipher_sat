import numpy as np

def get_permutation_table(ct_deck_size, pt_deck_size, seed = None, double_free = False):
	'''
	Generate a random permutation table of shape (pt_deck_size, ct_deck_size) such that first index of each row [i, 0] is unique.

	ct_deck_size: int,
	              size of the cipher text alphabet
	pt_deck_size: int,
	              size of the plain text alphabet
	seed: None or int,
	      set seed for the random number generator
	double_free: bool, if set to False, the first column (i.e. permutation_table[:,0]) will range (0-pt_deck_size-1), if set to True the first column will range (1-pt_deck_size)
	             Setting to True will result in double letters being impossible in a cipher text (because no permutation leaves the first index unchanged)
	'''
	rng = np.random.default_rng(seed = seed)
	assert pt_deck_size + int(double_free) <= ct_deck_size, "Size of cipher alphabet must be at least plaintext alphabet size."	
	permutation_table = np.tile(np.arange(ct_deck_size), (pt_deck_size, 1)) # ordered
	permutation_table = rng.permuted(permutation_table, axis = 1) # shuffle each row individually
	first_element_row_wise = rng.permuted(np.arange(int(double_free), ct_deck_size)) # decide first element of row by permuting all possible cards (except zero if desired) then pick as many as needed
	for i in range(pt_deck_size): # loop over rows
		k = np.nonzero(permutation_table[i] == first_element_row_wise[i])[0][0] # get index of declared first
		permutation_table[i] = np.roll(permutation_table[i], -k) # bring unique element to front by rolling array
	return permutation_table

def encrypt(pt_array, permutation_table):
	'''
	Encrypt a plain text array using a permutation table. The initial state of the deck is assumed to be sorted.
	'''
	ct_deck_size = permutation_table.shape[1]
	deck = np.arange(ct_deck_size) # initialize deck
	ct = np.empty(pt_array.shape, dtype = int)
	for i, k in enumerate(pt_array):
		deck = deck[permutation_table[k]] # permute the deck by the plain text letter
		ct[i] = deck[0] # top card is cipher text
	return ct

def decrypt(ct_array, permutation_table):
	'''
	Decrypt a cipher text array using a permutation table. The initial state of the deck is assumed to be sorted.
	'''
	ct_deck_size = permutation_table.shape[1]
	deck = np.arange(ct_deck_size) # initialize deck
	pt = np.empty(ct_array.shape, dtype = int)
	for i, k in enumerate(ct_array):
		ct_index = np.nonzero(deck == k)[0][0] # find cipher text letter in deck
		pt[i] = np.nonzero(permutation_table[:, 0] == ct_index)[0][0] # find row that brings that letter to the front, which is the plain text letter
		deck = deck[permutation_table[pt[i]]] # permute the deck accordingly
	return pt

def str_to_array(string, alphabet):
	'''
	Convert a string to an array given some alphabet.

	string: str,
	        The string to convert
	alphabet: str,
	          The alphabet to use, where the index of each character will be used to calculate the number in the array
	'''
	pt = np.empty(len(string), dtype = int)
	for i, c in enumerate(string):
		pt[i] = alphabet.index(c)
	return pt

def array_to_str(array, alphabet):
	'''
	Convert an array to a string given some alphabet.

	array: np.ndarray,
	        The array to convert
	alphabet: str,
	          The alphabet to use, where the number in the array will be used as index into the string
	'''
	string = ""
	for i in array:
		string += alphabet[i]
	return string

def get_isomorph_code(string):
	# isomorph pattern is like A..BC.ACB where dots are nonrepeated letters and A, B, C, etc. are repeated letters
	chardict = {}
	charcount = {}
	placeholder = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
	isomorph_pattern = ""

	# count letters
	for c in string:
		if c in charcount:
			charcount[c] += 1
		else:
			charcount[c] = 1

	k = 0
	for c in string:
		if charcount[c] == 1: # letter occurs only once, thus it cannot be repeated
			isomorph_pattern += "."
		else:
			if c not in chardict: # create a unique lookup for that letter if it doesnt exist yet
				chardict[c] = placeholder[k]
				k += 1
			isomorph_pattern += chardict[c]

	return isomorph_pattern

def get_all_isomorphs(string, isomorph_length):
	isomorphs = {}

	for i in range(len(string) - isomorph_length + 1):
		isomorph_code = get_isomorph_code(string[i:i+isomorph_length])
		if isomorph_code in isomorphs:
			isomorphs[isomorph_code]["count"] += 1
			isomorphs[isomorph_code]["pos"] += [i]
		else:
			isomorphs[isomorph_code] = {"count" : 1, "pos" : [i]}

	repeated_isomorphs = {}
	for key in isomorphs:
		if isomorphs[key]["count"] > 1 and key != "." * isomorph_length:
			repeated_isomorphs[key] = isomorphs[key]

	return repeated_isomorphs


if __name__ == "__main__":
	pt = "abcdabcd"
	pt_alphabet = "abcd"
	ct_alphabet = "ABCDEF"

	#pt = "this a very secret message and this a very secret message"
	#pt_alphabet = "abcdefghijklmnopqrstuvwxyz "
	#ct_alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

	permutation_table = get_permutation_table(len(ct_alphabet), len(pt_alphabet), seed = 0, double_free = True)

	print(f"{pt = }")
	pt_array = str_to_array(pt, pt_alphabet)
	ct_array = encrypt(pt_array, permutation_table)
	ct = array_to_str(ct_array, ct_alphabet)
	print(f"{ct = }")
	roundtrip_array = decrypt(ct_array, permutation_table)
	roundtrip = array_to_str(roundtrip_array, pt_alphabet)
	print(f"{roundtrip = }")

	#print(get_all_isomorphs("OLPJ3P-O3OLPJ3P-O3", 9))
	print(get_all_isomorphs(ct, 9))

	# next: merge overlapping isomorphs, trim "." beginning and end, try different lengths?

	print(ct_array)
	print(permutation_table)