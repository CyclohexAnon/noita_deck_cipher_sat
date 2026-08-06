import numpy as np


def prop_down(pt_array, permutation_table, deck, line):
	print("prop_down called")
	#print(f"{pt_array = }")
	#print(f"{permutation_table = }")
	print(f"{deck = }")

	if line >= len(deck):
		exit()

	ct_letter = deck[line][0]
	# call prop_up to percolate ct_letter upwards through the deck
	prop_up(pt_array, permutation_table, deck, line-1, ct_letter, return_line = line+1)
	


def prop_up(pt_array, permutation_table, deck, line, ct_letter, return_line):
	print("prop_up called")
	#print(f"{pt_array = }")
	#print(f"{permutation_table = }")
	print(f"{deck = }")

	if line == 0:
		prop_down(pt_array, permutation_table, deck, return_line)

	for i, v in enumerate(deck[line]):
		if v == -1:
			temp_deck = deck.copy()
			temp_deck[line][i] = ct_letter
			# need to also update permutation table

			# step 1: find ct letter in current line -> position x
			# step 2: find a plaintext letter that would bring the letter from v (line-1) to x (line)
			#         if there is an entry in permutation_table[:,0], use that
			#         otherwise fill the first space of a different row
			#         if no row is free, it is impossible, so return backwards

			prop_up(pt_array, permutation_table, temp_deck, line-1, ct_letter, return_line)




# -1 means undecided
deck = [[0,  1,  2,  3],
		[2, -1, -1, -1],
		[3, -1, -1, -1],
		[0, -1, -1, -1]]
# --> ct_array = [2, 3, 0]

permutation_table = [[2,  -1, -1, -1],
					 [-1, -1, -1, -1]]
# --> 2 at the front is kinda forced due to ct and initial ordering of the deck

pt_array = [0, -1, -1]
# --> corresponds to line 0 in perm table

prop_down(pt_array, permutation_table, deck, line = 2)
# --> line = 2 because we have already set line 1