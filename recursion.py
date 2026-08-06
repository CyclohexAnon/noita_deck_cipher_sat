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


def prop_down(pt_array, permutation_table, deck, line):
	print("> prop_down called")
	report(pt_array, permutation_table, deck)

	if line >= len(deck):
		exit()

	ct_letter = deck[line][0]
	# call prop_up to percolate ct_letter upwards through the deck
	prop_up(pt_array, permutation_table, deck, line-1, ct_letter, ct_index_prev_line = 0, return_line = line+1)
	


def prop_up(pt_array, permutation_table, deck, line, ct_letter, ct_index_prev_line, return_line):
	print("> prop_up called")
	report(pt_array, permutation_table, deck)
	print(f"{line = }")
	print(f"{ct_letter = }")

	if line == 0:
		print("#######")
		# value needs to go from <value> to ct_index_prev_line for pt_array[0]
		temp_permutation_table = permutation_table.copy()
		temp_permutation_table[pt_array[0]][ct_index_prev_line] = ct_letter
		print(f"set permutation table ({pt_array[0]},{ct_index_prev_line}) = {ct_letter}")

		print("#######")

		r = check_if_legal_permutation_table(temp_permutation_table)
		#if r is False: return

		prop_down(pt_array, temp_permutation_table, deck, return_line)

	for i, v in enumerate(deck[line]):
		if v == ct_letter:
			print("!!!!!!!!!!!!!!!!")
			# this occurs if the previous line already has that ct letter fixed in the deck
			# so we are forced to take that one
			if pt_array[line] == -1:
				# we can decide on a pt letter
				for j, row in enumerate(permutation_table):
					if row[0] == ct_index_prev_line:
						pass
						# we have to use that one

				for j, row in enumerate(permutation_table):
					if row[0] == -1:
						# for every of these choices, continue
						pass

				# if we are here, then nothing worked, so we need to backtrack
				print("Backtracking here...")
				return


			else:
				# we are forced to use a specific pt letter
				if permutation_table[pt_array[line]][0] == ct_index_prev_line:
					# okay, pick that one
					print("Hiiiiiiiiiiiiiiiii")

					report(pt_array, permutation_table, deck)
					print(f"{line = }")
					print(f"{pt_array[line] = }")
					print(f"{ct_index_prev_line = }")
					print(f"{permutation_table[pt_array[line]] = }")
					pass
				else:
					# dead end
					print("Backtracking...")
					return


		if v == -1:
			temp_deck = copy.deepcopy(deck)
			temp_deck[line][i] = ct_letter
			# need to also update permutation table

			# step 1: find ct letter in current line -> position x
			# This is already done by passing the position from the previous call -> ct_index_prev_line

			# step 2: find a plaintext letter that would bring the letter from v (line-1) to x (line)
			#         if there is an entry in permutation_table[:,0], use that
			#         otherwise fill the first space of a different row
			#         if no row is free, it is impossible, so return backwards

			print(f"plaintext {line = } is {pt_array[line]}")
			print(f"{ct_index_prev_line = }")
			print(f"{i = }")

			choice = [False, []]

			if pt_array[line] == -1:
				for j, row in enumerate(permutation_table):
					if row[ct_index_prev_line] == i or row[ct_index_prev_line] == -1: # i think == i is wrong here
						choice[0] = True
						choice[1] += [j]
			else:
				row = permutation_table[pt_array[line]]
				if row[ct_index_prev_line] == i or row[ct_index_prev_line] == -1:
					choice[0] = True
					choice[1] += [pt_array[line]]

			print(f"choice: {choice}")
			if choice[0] == False: return # impossible



			for row_index in choice[1]:
				if ct_index_prev_line == 0:
					if pt_array[line] == -1:
						pt_array[line] = row_index
					elif pt_array[line] != row_index:
						# we would choose an already taken index, a contradiction
						return

				temp_permutation_table = copy.deepcopy(permutation_table)

				#if row_index-1 > 0:
				#	temp_permutation_table[row_index-1][ct_index_prev_line] = i
				#if row_index+1 < len(deck):
				#	temp_permutation_table[row_index+1][ct_index_prev_line] = i

				temp_permutation_table[row_index][ct_index_prev_line] = i
				print(f"Setting permutation_table ({row_index},{ct_index_prev_line}) to {i}")
				prop_up(pt_array, temp_permutation_table, temp_deck, line-1, ct_letter, i, return_line)







# I think I need to do this more carefully


# percolating upwards
def percolate_up(pt_array, permutation_table, deck, current_pos, target_ct_letter_pos):
	#current_pos = 1 # chosen bc first position without assigned pt letter

	#target_ct_letter_pos = 0
	target_ct_letter = deck[current_pos][target_ct_letter_pos] # this is the letter we want to get

	# this letter has to come from somewhere, so check where it could come from
	previous_line = current_pos - 1

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

	print(f"{positions = }")

	for pos in positions:
		# try placing it there in the deck
		temp_deck = copy.deepcopy(deck)
		temp_deck[previous_line][pos] = target_ct_letter

		# next we need to ask: how could it have gotten there?

		if pt_array[current_pos] != -1:
			# we have already decided on a pt letter here, so we must add this info to permutation table there
			row_indices_in_perm_table = [pt_array[current_pos]]
		else:
			# we have not yet decided on a pt letter at this position
			# naively, we have pt_alphabet choices for rows now

			# but actually, if we are in column zero we should also check if we havent already used this elsewhere
			if target_ct_letter_pos == 0:
				row_indices_in_perm_table = []
				for i in range(len(permutation_table)):
					if permutation_table[i][0] == target_ct_letter:
						row_indices_in_perm_table += [i]
						break
				if len(row_indices_in_perm_table) == 0:
					for i in range(len(permutation_table)):
						if permutation_table[i][0] == -1:
							row_indices_in_perm_table += [i]

			else:
				row_indices_in_perm_table = [i for i in range(len(permutation_table))]


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

			temp_pt_array = copy.deepcopy(pt_array)
			temp_pt_array[current_pos] = row_index_in_perm_table

			# --> call next step one layer up
			# unless previous_line == 0, then step one layer down on the outside recursion?

			if not check_if_legal_permutation_table(temp_permutation_table):
				print("Not legal permutation table")
				#print(temp_permutation_table)
				print("-"*10)
				continue
			
			print(f"{row_index_in_perm_table = }")
			report(temp_pt_array, temp_permutation_table, temp_deck)
			print("-"*10)

			if previous_line == 0:
				pass
				# percolate down

				print("AAAAAAAAAAAAAAAAAAAA")

				exit()
			else:
				pass
				#percolate_up(temp_pt_array, temp_permutation_table, temp_deck, previous_line, pos)

	# if we land down here something has gone wrong I think
	# i.e. nothing has worked out
	return
 

	# next todo is where to check if any contradictions arose?

def percolate_down(pt_array, permutation_table, deck, current_pos):
	#report(pt_array, permutation_table, deck)

	if current_pos >= len(deck):
		exit()

	# call prop_up to percolate ct_letter upwards through the deck
	#prop_up(pt_array, permutation_table, deck, line-1, ct_letter, ct_index_prev_line = 0, return_line = line+1)
	percolate_up(pt_array, permutation_table, deck, current_pos, target_ct_letter_pos = 0)


# -1 means undecided
deck = [[0,  1,  2,  3],
		[2, -1, -1, -1],
		[3, -1, -1, -1],
		[0, -1, -1, -1],
		[0, -1, -1, -1]]
# --> ct_array = [2, 3, 0]

permutation_table = [[2, -1, -1, -1],
					 [-1, -1, -1, -1]]
# --> 2 at the front is kinda forced due to ct and initial ordering of the deck

pt_array = [0, -1, -1, -1]
# --> corresponds to line 0 in perm table

#prop_down(pt_array, permutation_table, deck, line = 2)
# --> line = 2 because we have already set line 1

percolate_down(pt_array, permutation_table, deck, current_pos = 2)