import deckcipher as dc
import eye_data as eyes

#pt_alphabet = "abcdefgh"
#ct_alphabet = "ABCDEFGHIJKLMN"
#pt_alphabet_size = len(pt_alphabet)
#ct_alphabet_size = len(ct_alphabet)
#permutation_table = dc.get_permutation_table(len(ct_alphabet), len(pt_alphabet), seed = 0, double_free = True)
#print("Permutation table:")
#print(permutation_table)
#pts = ["abgcaefbgcabc", "hcabagbbah", "abcedfghab"]
#pt_arrays = list(map(lambda p: dc.str_to_array(p, pt_alphabet), pts))
#ct_arrays = list(map(lambda p: dc.encrypt(p, permutation_table), pt_arrays))
#pt_lens = list(map(len, ct_arrays))

pt_alphabet_size = 26
ct_alphabet_size = 83
ct_arrays = [eyes.east_1, eyes.west_1, eyes.east_2, eyes.west_2, eyes.east_3, eyes.west_3, eyes.east_4, eyes.west_4, eyes.east_5]
pt_lens = list(map(len, ct_arrays))

with open("minizinc_cipher.mzn", "w") as f:
	f.write(f'include "globals.mzn";\n\n')
	f.write(f'int: pt_alphabet_size = {pt_alphabet_size};\n')
	f.write(f'int: ct_alphabet_size = {ct_alphabet_size};\n')

	for i in range(len(ct_arrays)):
		ct_array = ct_arrays[i]
		pt_len = pt_lens[i]

		f.write(f'int: pt_len_{i} = {pt_len};\n')
		f.write(f'array[1..pt_len_{i}] of int: ct_{i} = {list(map(int, ct_array))};\n')
		f.write(f'array[1..pt_len_{i}] of var 0..(pt_alphabet_size-1): pt_{i};\n')

	f.write(f'set of int: pt_alphabet = 0..(pt_alphabet_size-1);\n')
	f.write(f'set of int: ct_alphabet = 0..(ct_alphabet_size-1);\n')
	f.write(f'array[pt_alphabet, ct_alphabet] of var 0..(ct_alphabet_size-1): permutation_table;\n')
	# each row is a permutation
	f.write(f'constraint forall(p in pt_alphabet)(all_different([permutation_table[p, i] | i in ct_alphabet]));\n')
	# first column has unique entries
	f.write(f'constraint all_different([permutation_table[p, 0] | p in pt_alphabet]);\n')

	for i in range(len(ct_arrays)):
		f.write(f'array[0..pt_len_{i}, ct_alphabet] of var 0..(ct_alphabet_size-1): deck_{i};\n')
		# first deck state is ordered
		f.write(f'constraint forall(c in ct_alphabet)(deck_{i}[0, c] = c);\n')
		# each row is a permutation
		f.write(f'constraint forall(p in 1..pt_len_{i})(all_different([deck_{i}[p, i] | i in ct_alphabet]));\n')
		# each following row is the previous row, permuted by the permutation table row for that pt letter
		f.write(f'constraint forall(p in 1..pt_len_{i}, i in ct_alphabet)(deck_{i}[p, i] = deck_{i}[p-1, permutation_table[pt_{i}[p], i]]);\n')
		# the ciphertext are the 0th column of the deck
		f.write(f'constraint forall(p in 1..pt_len_{i})(deck_{i}[p, 0] = ct_{i}[p]);\n')

	f.write(f'solve satisfy;\n')