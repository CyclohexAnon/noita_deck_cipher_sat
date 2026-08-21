import numpy as np

def multiplexer(a, b, s, c, d):
	# a, b input
	# c, d output
	# s is switch
	# if s is True, then       a = c, b = d
	#               otherwise, a = d, b = c
	clauses = [[-s, -a,  c,  0],
			   [-s,  a, -c,  0],
			   [ s, -b,  c,  0],
			   [ s,  b, -c,  0],
			   [ s, -a,  d,  0],
			   [ s,  a, -d,  0],
			   [-s, -b,  d,  0],
			   [-s,  b, -d,  0]]

	return clauses

def omega_network(layer1, layer2, switches):
	clauses = []
	hl = len(layer1)//2
	for i in range(hl):
		#print("add multiplexer between:")
		#print(f"{layer1[i]}, {layer1[i+hl]} to {layer2[2*i]}, {layer2[2*i+1]} with switch {switches[i]}")
		clauses += multiplexer(layer1[i], layer1[i+hl], switches[i], layer2[2*i], layer2[2*i+1])
	return clauses

def flip_network(layer1, layer2, switches):
	clauses = []
	hl = len(layer1)//2
	for i in range(hl):
		#print("add multiplexer between:")
		#print(f"{layer1[2*i]}, {layer1[2*i+1]} to {layer2[i]}, {layer2[i+hl]} with switch {switches[i]}")
		clauses += multiplexer(layer1[2*i], layer1[2*i+1], switches[i], layer2[i], layer2[i+hl])
	return clauses

bits = 83
offset = 0

make_even = lambda n: n + n%2
code = lambda x: x + offset + 1

nodes_per_layer = make_even(bits)
number_of_layers_per_half = int(np.ceil(np.log2(nodes_per_layer)))

layers = []

for j in range(2*number_of_layers_per_half+1):
	layers += [[code(i + j*nodes_per_layer) for i in range(nodes_per_layer)]]

num_layer_nodes = nodes_per_layer*(2*number_of_layers_per_half+1)

switches = []
for j in range(2*number_of_layers_per_half):
	switches += [[code(i + j*(nodes_per_layer//2) + num_layer_nodes) for i in range(nodes_per_layer//2)]]

print(layers)
print(switches)

# number of variables:
# input layer: nodes_per_layer
# all other layers: nodes_per_layer * 2 * number_of_layers_per_half
# selectors: number_of_layers_per_half * nodes_per_layer

number_of_vars = nodes_per_layer * (2 * number_of_layers_per_half + 1) + number_of_layers_per_half * nodes_per_layer

print("-"*10)

clauses = []

for i in range(number_of_layers_per_half):
	#print("add omega network between:")
	#print(layers[i])
	#print(layers[i+1])
	#print(switches[i])
	clauses += omega_network(layers[i], layers[i+1], switches[i])

for i in range(number_of_layers_per_half, 2*number_of_layers_per_half):
	#print("add flip network between:")
	#print(layers[i])
	#print(layers[i+1])
	#print(switches[i])
	clauses += flip_network(layers[i], layers[i+1], switches[i])

# number of clauses:
# we have 2*number_of_layers_per_half networks
# each network nodes_per_layer//2 multiplexers --> the 2s cancel
# each multiplexer has 8 clauses

number_of_clauses = number_of_layers_per_half * nodes_per_layer * 8


#omega_network(layers[0], layers[1], switches[0])
#flip_network(layers[0], layers[1], switches[0])

#print(clauses)
#print("-"*10)
#print("input:")
#print(layers[0])
#print("output:")
#print(layers[-1])

#h = "010011"
#for i in range(nodes_per_layer):
#	clauses += [[(int(h[i])*2 - 1) * layers[0][i], 0]]
#number_of_clauses += nodes_per_layer

#o = "110010"
#for i in range(nodes_per_layer):
#	clauses += [[(int(o[i])*2 - 1) * layers[-1][i], 0]]
#number_of_clauses += nodes_per_layer

## Must not forget: If bits%2 == 1, then there is one additional undesired variable at the end
# in the context of the deck cipher encoding, we can set this bit
# and the corresponding output bit unconditionally to True, such that when multiple layers are encoded using
# the same switch variables and the stacked input layers count in binary, then this forces the last card to
# remain in the last spot, so it is as if it did not exist at all.

if bits%2 == 1:
	clauses += [[layers[0][-1], 0], [layers[-1][-1], 0]]
	number_of_clauses += 2



print(f"{number_of_vars = }\n{number_of_clauses = }")

#with open("omeganetwork.cnf", "w") as f:
#	f.write(f"p cnf {number_of_vars} {number_of_clauses}\n")
#	f.write("\n".join([" ".join(map(str, c)) for c in clauses]))