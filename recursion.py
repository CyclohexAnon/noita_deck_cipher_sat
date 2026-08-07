import numpy as np
import copy

def report(pt_array, permutation_table, deck):
	print("permutation table:")
	print(np.array(permutation_table, dtype = int))
	print("deck states:")
	print(np.array(deck, dtype = int))
	print("pt array:")
	print(np.array(pt_array, dtype = int))

def check_if_legal_permutation_table(permutation_table):
	# no repeats in a row
	for i, row in enumerate(permutation_table):
		for j in range(1, len(row)):
			if row[j] in row[:j] and row[j] != -1:
				return False
	seen = []
	for i in range(len(permutation_table)):
		if permutation_table[i][0] == -1: continue
		if i == 0: seen += [permutation_table[i][0]]; continue
		if permutation_table[i][0] in seen: return False
		seen += [permutation_table[i][0]]

	return True

# percolating upwards
def percolate_up(pt_array, permutation_table, deck, current_pos, target_ct_letter_pos, return_line):
	if debug:
		print(f"> perc up called with {current_pos = }, {target_ct_letter_pos = }, {return_line = }")
		report(pt_array, permutation_table, deck)
		print("."*5)

	# current pos is the position IN THE DECK that we start from
	# i.e. for the first pt letter you start at 1 and not at 0

	#target_ct_letter_pos = 0
	target_ct_letter = deck[current_pos][target_ct_letter_pos] # this is the letter we want to get

	# this letter has to come from somewhere, so check where it could come from
	previous_line = current_pos - 1

	current_pt_position = current_pos - 1

	# first check if it is present: if it is present, we know where we need to look
	positions = []
	for i, val in enumerate(deck[previous_line]):
		if val == target_ct_letter:
			positions += [i]
			break

	if len(positions) == 0:
		# This means it was not found, so next we look for free spots, denoted by -1
		for i, val in enumerate(deck[previous_line]):
			if val == -1:
				positions += [i]

	if len(positions) == 0:
		# if we havent found any position now, that means we are DEFINTELY in a corner
		print("Impossible to continue")
		exit()

	# So we have obtained some possible positions where the letter could have come from in the previous line
	# Thus, we can loop over each of them to try them out exhaustively

	if debug: print(f"{positions = }")

	for pos in positions:
		# try placing it there in the deck
		temp_deck = copy.deepcopy(deck)
		temp_deck[previous_line][pos] = target_ct_letter

		# next we need to ask: how could it have gotten there?

		if pt_array[current_pt_position] != -1:
			# we have already decided on a pt letter here, so we must add this info to permutation table there
			row_indices_in_perm_table = [pt_array[current_pt_position]]
		else:
			# we have not yet decided on a pt letter at this position
			# naively, we have pt_alphabet choices for rows now

			# but actually, if we are in column zero we should also check if we havent already used this elsewhere
			#if target_ct_letter_pos == 0:
			#	row_indices_in_perm_table = []

				#for i in range(len(permutation_table)):
				#	if permutation_table[i][0] == target_ct_letter:
				#		row_indices_in_perm_table += [i]
				#		break
				#print(f"> {row_indices_in_perm_table = }")
				#if len(row_indices_in_perm_table) == 0:
				#	for i in range(len(permutation_table)):
				#		if permutation_table[i][0] == -1:
				#			row_indices_in_perm_table += [i]
			#else:
			#	row_indices_in_perm_table = [i for i in range(len(permutation_table))]
			row_indices_in_perm_table = [i for i in range(len(permutation_table))]


		if debug: print(f"{row_indices_in_perm_table = }")
		#exit()

		for row_index_in_perm_table in row_indices_in_perm_table:
			# the value went from pos in the previous line to target_ct_letter_pos in the current line
			# e.g.
			#      . . . . T . . . previous line
			#      . . T . . . . . current line
			# -->  . . 4 . . . . . perm table row


			# we should check if the spot is even available!
			if permutation_table[row_index_in_perm_table][target_ct_letter_pos] != -1 and \
			   permutation_table[row_index_in_perm_table][target_ct_letter_pos] != pos:
			   # the position is not free and also not already occupied with what we want
			   # a contradiction
			   continue
			temp_permutation_table = copy.deepcopy(permutation_table)
			temp_permutation_table[row_index_in_perm_table][target_ct_letter_pos] = pos

			temp_permutation_table = update_permutation_table(temp_permutation_table)

			temp_pt_array = copy.deepcopy(pt_array)
			temp_pt_array[current_pt_position] = row_index_in_perm_table

			# --> call next step one layer up
			# unless previous_line == 0, then step one layer down on the outside recursion?

			if not check_if_legal_permutation_table(temp_permutation_table):
				if debug: print("Not legal permutation table")
				#print(temp_permutation_table)
				if debug: print("-"*10)
				continue

			# recalculate deck because we have added info to it
			temp_deck = update_deck(temp_pt_array, temp_permutation_table, temp_deck)
			
			if debug:
				print(f"{row_index_in_perm_table = }")
				report(temp_pt_array, temp_permutation_table, temp_deck)
				print("-"*10)

			if previous_line == 0:
				pass
				# percolate down

				#print("AAAAAAAAAAAAAAAAAAAA")

				#exit()

				percolate_down(temp_pt_array, temp_permutation_table, temp_deck, return_line)

			else:
				pass
				percolate_up(temp_pt_array, temp_permutation_table, temp_deck, previous_line, pos, return_line)

	# if we land down here something has gone wrong I think
	# i.e. nothing has worked out
	return
 

	# next todo is where to check if any contradictions arose?

def percolate_down(pt_array, permutation_table, deck, current_pos):
	#report(pt_array, permutation_table, deck)

	if debug: print(f"> perc down called with {current_pos = }")

	if current_pos >= len(deck):
		print("Success!")
		report(pt_array, permutation_table, deck)
		print("Validating:")
		validate_solution(pt_array, permutation_table, deck)
		print("Finished successfully, exiting...")
		exit()

	# call prop_up to percolate ct_letter upwards through the deck
	#prop_up(pt_array, permutation_table, deck, line-1, ct_letter, ct_index_prev_line = 0, return_line = line+1)
	percolate_up(pt_array, permutation_table, deck, current_pos, target_ct_letter_pos = 0, return_line = current_pos+1)


# -1 means undecided
#deck = [[0,  1,  2,  3],
#		[2,  0, -1, -1],
#		[3, -1, -1, -1],
#		[0, -1, -1, -1],
#		[0, -1, -1, -1]]
# --> ct_array = [2, 3, 0]

#permutation_table = [[-1, -1, -1, -1],
#					 [-1, -1, -1, -1]]
# --> 2 at the front is kinda forced due to ct and initial ordering of the deck

#pt_array = [-1, -1, -1, -1]
# --> corresponds to line 0 in perm table

#prop_down(pt_array, permutation_table, deck, line = 2)
# --> line = 2 because we have already set line 1

#percolate_down(pt_array, permutation_table, deck, current_pos = 1)
#percolate_up(pt_array, permutation_table, deck, current_pos = 3, target_ct_letter_pos = 0, return_line = 4)

# I think it may work now...

def make_starting_configuration(pt_alphabet_size, ct_alphabet_size, ct_array):
	pt_array = [-1 for i in ct_array]
	permutation_table = [[-1 for i in range(ct_alphabet_size)] for j in range(pt_alphabet_size)]
	deck = [[i for i in range(ct_alphabet_size)]]
	deck += [[j if i == 0 else -1 for i in range(ct_alphabet_size)] for j in ct_array]

	return pt_array, permutation_table, deck

def update_permutation_table(permutation_table):
	# if there is a row with just a single unset (-1) value, then fill it with the remaining value
	for i, row in enumerate(permutation_table):
		if row.count(-1) == 1:
			replacement_value = len(row)-1
			for j, v in enumerate(sorted(row)[1:]):
				if v != j:
					replacement_value = j
					break
			permutation_table[i] = list(map(lambda x: replacement_value if x == -1 else x, permutation_table[i]))
	return permutation_table


def update_deck(pt_array, permutation_table, deck):
	#print("Deck:")
	#print(deck)
	new_deck = copy.deepcopy(deck)
	
	for j, pt_letter in enumerate(pt_array):
		if pt_letter == -1: continue

		perm = permutation_table[pt_letter]
		validation_deck_state = []
		for i, v in enumerate(perm):
			if v == -1:
				validation_deck_state += [-1]
			else:
				validation_deck_state += [new_deck[j][v]]
		#print(new_deck[j+1])
		#print(validation_deck_state)
		for i, (a, b) in enumerate(zip(new_deck[j+1], validation_deck_state)):
			if a == -1 and b != -1: new_deck[j+1][i] = b

	#print("New deck:")
	#print(new_deck)
	return new_deck

def recalculate_deck(pt_array, permutation_table, deck):
	validation_deck_state = deck[0] # ensure same initial ordering
	validation_deck = [validation_deck_state]
	
	for pt_letter in pt_array:
		if pt_letter == -1: validation_deck += [[-1 for i in range(len(permutation_table[0]))]]; continue
		perm = permutation_table[pt_letter]
		next_validation_deck_state = []
		for i in perm:
			if i == -1:
				next_validation_deck_state += [-1]
			else:
				next_validation_deck_state += [validation_deck_state[i]]

		validation_deck_state = next_validation_deck_state
		validation_deck += [validation_deck_state]
	return validation_deck

def validate_solution(pt_array, permutation_table, deck):
	validation_deck = recalculate_deck(pt_array, permutation_table, deck)
	#print(np.array(validation_deck, dtype = int))

	print(f"{permutation_table = }")
	print(f"{pt_array = }")


import sys
print(sys.getrecursionlimit())
sys.setrecursionlimit(10000)

debug = False
#pt_alphabet_size = 2
#ct_alphabet_size = 4
#ct_array = [2, 3, 0, 0, 1, 2, 3]

pt_alphabet_size = 26
ct_alphabet_size = 83
ct_array = [50, 66, 5, 48, 62, 13, 75, 29, 24, 61, 42, 70, 66, 62, 32, 14, 81, 8, 15, 78, 2, 29, 13, 49, 1, 80, 82, 40, 63, 81, 21, 19, 0, 40, 51, 65, 26, 14, 21, 70, 47, 44, 48, 42, 19, 48, 13, 47, 19, 49, 72, 31, 5, 24, 3, 43, 59, 67, 33, 49, 41, 60, 21, 26, 30, 5, 25, 20, 71, 11, 74, 56, 4, 74, 19, 71, 4, 51, 41, 43, 80, 72, 54, 63, 79, 81, 15, 16, 44, 31, 30, 12, 33, 57, 28, 13, 64, 43, 48]


pt_array, permutation_table, deck = make_starting_configuration(pt_alphabet_size, ct_alphabet_size, ct_array)
percolate_down(pt_array, permutation_table, deck, current_pos = 1)
print("Failure! No answer found.")


# todo: when we update perm_table, we should probably recalculate the deck evolution as well because it may block parts later
# --> done
# at that point we could also do inference like when only a single value is not set in a permutation table, the last value is forced
# --> done

# sanity check: is 2,3,0,0,1,2,3 with ctsize = 4 and ptsize = 2 UNSAT?

# next to do step:
# - more testing
# - how to deal with parallel ciphertexts?
# ---> maybe have a function that checks if a permutation table as given cannot decrypt a ct?
# ---> not sure how I would do that...


