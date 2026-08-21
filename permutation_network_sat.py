import numpy as np

def bits_needed(x):
	# return how many bits are needed to describe a number up until x-1 (i.e. the x numbers from 0 to x-1)
	return int(np.ceil(np.log2(x)))

def get_permlayer_size(ct_alphabet_size):
	# return (width, height) tuple for size of array needed for the layers of a permutation network permuting ct_alphabet_size number of elements
	# we are also NOT counting the top layer because when chaining the top layer is shared. One singular layer does, of course, needed one additional layer (the initial one)
	make_even = lambda n: n + n%2
	code = lambda x: x + offset + 1
	nodes_per_layer = make_even(ct_alphabet_size)
	number_of_layers_per_half = bits_needed(nodes_per_layer)
	return (nodes_per_layer, number_of_layers_per_half*2)

def get_permswitch_size(ct_alphabet_size):
	# return the size needed for the switches
	width, height = get_permlayer_size(ct_alphabet_size)
	return (width//2, height)

# Okay so idea how this should go
# I will use 26 and 83 here in this text but they are obviously pt_alphabet_size and ct_alphabet_size
# Step 1: Create 26x 2d arrays of the shape of the switches in the permutation networks, these are the shuffle rules per letter
# Step 2: Create the pt selectors as pt_len*7 array, and constrain each to be a binary number in the range 0-25
# Step 3: Create the deck
# Step 3: Create pt_len permutation networks and connect them via the pt_selectors to the 26 arrays of the pt_letters
# Step 4: Make the initial deck sorted (if we wanted to have it in a different order, I think it would be best to just insert one more permutation network after the sorted array, and have different ct reuse the same)
# Step 5: Create an additional 26 permutation networks starting with a sorted arrays and enforce pairwise unequality between the first cards of any of the 26 outputs (should be 26*25/2 inequalities?)
# Step 6: For each deck state, constrain the top card in the deck to be the one specified by the ct


ct_alphabet_size = 10
pt_alphabet_size = 5
pt_len = 10
ct_array = [1, 2, 1, 2, 1, 2, 4, 4, 0, 3] # chosen at random, not from actual pt

total_var = 0

# to get the switch array var names for pt_letter[i], retrieve pt_letter_permutations[i]. It is an array of arrays containing row wise the switches for the network
width, height = get_permswitch_size(ct_alphabet_size)
pt_letter_permutations = [[] for i in range(pt_alphabet_size)]
for i in range(pt_alphabet_size):
	pt_letter_permutations[i] = [[j + total_var + 1 + width*k for j in range(width)] for k in range(height)]
	total_var += width*height

# the pt selectors at position i of the pt are in pt_selectors[i]
bits = bits_needed(pt_alphabet_size)
pt_selectors = [[] for i in range(pt_len)]
for i in range(pt_len):
	pt_selectors[i] = [j + total_var + 1 for j in range(bits)]
	total_var += bits

# the initial deck layers are organized the other way around to make the incorporation into the permutation networks easier
# so they are arranged like: [[0, 1, 0, 1, 0, 1, 0, 1],
#                             [0, 0, 1, 1, 0, 0, 1, 1],
#                             [0, 0, 0, 0, 1, 1, 1, 1]] ... etc when looking at the truth values when sorted
bits = bits_needed(ct_alphabet_size)
initial_deck_layers = [[] for i in range(bits)]
for i in range(ct_alphabet_size):
	initial_deck_layers[i] = [i + total_var + 1 for i in range(ct_alphabet_size)]
	total_var += ct_alphabet_size

# The layers of the permutation networks, not including the first layer. The first layer of the first block is the initial deck. The first layer of every subsequent block is the last line of the previous block.
width, height = get_permlayer_size(ct_alphabet_size)
network_blocks = [[] for i in range(pt_len)]
for i in range(pt_len):
	network_blocks[i] = [[j + 1 + total_var + k*width for j in range(width)] for k in range(height)]
	total_var += width*height

# The switches are actually coming from the pt_selectors and the pt_letter_permutations, so they dont need separate variables

# Everything afterwards is just constraints on this structure
# TODO: multiplexer_2to2 with selectors