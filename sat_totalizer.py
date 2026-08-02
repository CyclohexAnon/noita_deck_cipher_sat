length = 4


def make_one_layer(left_start, left_len, right_start, right_len, out_start):
	# left nodes: left_start to left_start + left_len - 1
	# right nodes: right_start to right_start + right_len - 1
	# output_nodes: out_start to out_start + left_len + right_len - 1
	out_len = left_len + right_len

	# Say we are merging two child nodes A and B to a bigger node R,
	# For k variables in each child node,
	# a + b = s,
	# and 0 <= a <= k and 0 <= b <= k, add the clauses
	# (A_a ^ B_b) -> R_s                 =  R_s v ~(A_a ^ B_b)               = R_s v ~A_a v ~B_b
	# (~A_(a+1) ^ ~B_(b+1)) -> ~R_(s+1)  = ~R_(s+1) v ~(~A_(a+1) ^ ~B_(b+1)) = ~R_(s+1) v A_(a+1)) v B_(b+1)
	# Note that the edges simplify e.g. by asserting A_1 -> R_1 and ~A_k -> ~R_(2k)
	# Or more generally, by saying that A_0, B_0, R_0 are true and A_(k+1), B_(k+1), R_(2k+1) are all false

	code_left  = lambda x: left_start + x + 1
	code_right = lambda x: right_start + x + 1
	code_out   = lambda x: out_start + x + 1

	clauses = []

	#for a in range(left_len):
	#	for b in range(right_len):
	#		s = a + b
	#		clauses += [[-code_left(a), -code_right(b), code_out(s), 0]]
	#for a in range(left_len):
	#	clauses += [[-code_left(a), code_out(a), 0]]
	#for b in range(right_len):
	#	clauses += [[-code_right(b), code_out(b), 0]]
	#for a in range(left_len-1):
	#	for b in range(right_len-1):
	#		s = a + b
	#		clauses += [[code_left(a+1), code_right(b+1), -code_out(s+1), 0]]
	#for a in range(left_len-1):
	#	clauses += [[code_left(a+1), -code_out(a+1), 0]]
	#for b in range(right_len):
	#	clauses += [[code_right(b+1), -code_out(b+1), 0]]

	for a in range(left_len):
		for b in range(right_len):
			clauses += [[-code_left(a), -code_right(b), code_out(a+b+1), 0]]
	for a in range(left_len):
		clauses += [[-code_left(a), code_out(a), 0]]
	for b in range(right_len):
		clauses += [[-code_right(b), code_out(b), 0]]

	for a in range(left_len):
		for b in range(-1, right_len-1):
			clauses += [[code_left(a), code_right(b+1), -code_out(a+b), 0]]
	#for a in range(left_len):
	#	clauses += [[code_left(a), -code_out(a+b+1), 0]]



	# just for testing
	#for a in range(left_len):
	#	clauses += [[code_left(a), 0]]
	#for b in range(right_len):
	#	clauses += [[-code_right(b), 0]]

	#for i in range(out_len):
	#	v = -1
	#	if i < 2: v = 1
	#	clauses +=

	return clauses

#clauses = make_one_layer(0, 2, 2, 2, 4)
#clauses = make_one_layer(0, 1, 1, 1, 2)
#string = "\n".join([" ".join(map(str, c)) for c in clauses])

#with open("sat_totalizer.cnf", "w") as f:
#	f.write(f"p cnf 8 {len(clauses)}\n")
#	f.write(string)

# it doesnt workkkkkk :<


# This works
# This is a level 1 sorter
clauses = []
input_left = True
#clauses += [[-1, 0]]
input_right = False
#clauses += [[2, 0]]
output = [None, None]
#clauses += [[3, 0]]
#clauses += [[-4, 0]]
output[0] = input_left or input_right
output[1] = input_left and input_right
# thus:
# 3 <-> (1 v 2) = (3 -> (1 v 2)) ^ ((1 v 2) -> 3)
#               = (-3 v 1 v 2) ^ (-(1 v 2) v 3)
#               = (-3 v 1 v 2) ^ ((-1 ^ -2) v 3)
#               = (-3 v 1 v 2) ^ (-1 v 3) ^ (-2 v 3)
clauses += [[-3, 1, 2, 0], [-1, 3, 0], [-2, 3, 0]]
# 4 <-> (1 ^ 2) = (4 -> (1 ^ 2)) ^ ((1 ^ 2) -> 4)
#               = (-4 v (1 ^ 2)) ^ (-(1 ^ 2) v 4)
#               = (-4 v 1) ^ (-4 v 2) ^ (-1 v -2 v 4)
clauses += [[-4, 1, 0], [-4, 2, 0], [-1, -2, 4, 0]]

with open("sat_totalizer.cnf", "w") as f:
	f.write(f"p cnf 4 {len(clauses)}\n")
	string = "\n".join([" ".join(map(str, c)) for c in clauses])
	f.write(string)


# okay so this is the simplest level 2 sorter
clauses = []
input_left = [True, False]
clauses += [[1, 0], [-2, 0]]
input_right = True
clauses += [[3, 0]]
output = [None, None, None]

# there are these six cases:
# left  right  out
# 0 0   0      0 0 0
# 1 0   0      1 0 0
# 1 1   0      1 1 0
# 0 0   1      1 0 0
# 1 0   1      1 1 0
# 1 1   1      1 1 1

# input left is 1, 2, input right is 3, out are 4, 5, 6
# it is clear that if 1 or 3, then 4, so
# 1 v 3 -> 4 = -(1 v 3) v 4
#            = (-1 ^ -3) v 4
#            = (-1 v 4) ^ (-3 v 4)
if input_left[0] or input_right: output[0] = True
clauses += [[-1, 4, 0], [-3, 4, 0]]

# for the middle bit, there are two implications
# 2 -> 5 = -2 v 5
# 1 ^ 3 -> 5 = -(1 ^ 3) v 5
#            = -1 v -3 v 5
if input_left[1] or (input_left[0] and input_right): output[1] = True
clauses += [[-2, 5, 0], [-1, -3, 5, 0]]


# Finally, for the last bit, everything must be true, but since left is sorted, it suffices to check the top bit
# 2 ^ 3 -> 6 = -(2 ^ 3) v 6
#            = (-2 v -3) v 6
#            = -2 v -3 v 6
if input_left[1] and input_right: output[2] = True
clauses += [[-2, -3, 6, 0]]


# This successfully sets the correct number of bits, but the top bits are left floating
# so lets do those next
# The lowest bit is false if -1 and -3:
# -1 ^ -3 -> -4 = -(-1 ^ -3) v -4
#               = 1 v 3 v -4
if not input_left[0] and not input_right: output[0] = False
clauses += [[1, 3, -4, 0]]


# The middle output bit is false in two cases:
# -1 -> -5 = 1 v -5
# -2 ^ -3 -> -5 = -(-2 ^ -3) v -5
#               = 2 v 3 v -5
if (not input_left[0]) or (not input_left[1] and not input_right): output[1] = False
clauses += [[1, -5, 0], [2, 3, -5, 0]]


# finally, the top output bit is always false except when everything is true, so
# -2 -> -6 = 2 v -6
# -3 -> -6 = 3 v -6
if (not input_left[1]) or (not input_right): output[2] = False
clauses += [[2, -6, 0], [3, -6, 0]]



with open("sat_totalizer.cnf", "w") as f:
	f.write(f"p cnf 6 {len(clauses)}\n")
	string = "\n".join([" ".join(map(str, c)) for c in clauses])
	f.write(string)



# okay, now a larger example:
# left   right  out
# 0 0 0  0 0 0  0 0 0 0 0 0
# 1 0 0  0 0 0  1 0 0 0 0 0
# 0 0 0  1 0 0  1 0 0 0 0 0
# 1 0 0  1 0 0  1 1 0 0 0 0
# 1 1 0  0 0 0  1 1 0 0 0 0
# 0 0 0  1 1 0  1 1 0 0 0 0
                               # We focus on s2 and s3 here
# 1 1 1  0 0 0  1 1 1 0 0 0    # l2     (^ r(-1)) -> s2 and (-l(3)) ^ -r0   -> -s3
# 1 1 0  1 0 0  1 1 1 0 0 0    # l1      ^ r0     -> s2 and -l2     ^ -r1   -> -s3
# 1 0 0  1 1 0  1 1 1 0 0 0    # l0      ^ r1     -> s2 and -l1     ^ -r2   -> -s3
# 0 0 0  1 1 1  1 1 1 0 0 0    # (l(-1)) ^ r2     -> s2 and -l0     ^ (-r3) -> -s3

# 1 1 1  1 0 0  1 1 1 1 0 0
# 1 1 0  1 1 0  1 1 1 1 0 0
# 1 0 0  1 1 1  1 1 1 1 0 0
# 1 1 1  1 1 0  1 1 1 1 1 0
# 1 1 0  1 1 1  1 1 1 1 1 0
# 1 1 1  1 1 1  1 1 1 1 1 1

l_len = 3
r_len = 3

s = 0
for r in range(-1, s+1):
	l = s-r-1
	if r >= r_len: print(f"(-l{l} -r{r} s{s}) --> -r{r} is always true, drop entire clause"); continue
	if l >= l_len: print(f"(-l{l} -r{r} s{s}) --> -l{l} is always true, drop entire clause"); continue
	if r == -1: print(f"(-l{l} -r{r} s{s}) --> -r{r} is always false, can be dropped --> -l{l} s{s}"); continue
	if l == -1: print(f"(-l{l} -r{r} s{s}) --> -l{l} is always false, can be dropped --> -r{r} s{s}"); continue
	print(f"-l{l} -r{r} s{s} --> keep as is")

print("-"*10)

s = 0
for r in range(s+1):
	l = s-r
	if r >= r_len: print(f"(l{l} r{r} -s{s}) --> r{r} is always false, can be dropped --> l{l} -s{s}"); continue
	if l >= l_len: print(f"(l{l} r{r} -s{s}) --> l{l} is always false, can be dropped --> r{r} -s{s}"); continue
	print(f"l{l} r{r} -s{s} --> keep as is")






## okay so this should make the following function
clauses = []
l_len = 1
l_start = 0
r_len = 1
r_start = l_len
s_start = l_start + l_len + r_len
s_len = l_len + r_len

l_code = lambda x: x + 1 + l_start
r_code = lambda x: x + 1 + r_start
s_code = lambda x: x + 1 + s_start

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

#clauses += [[1, 0], [2, 0], [3, 0], [4, 0], [-5, 0], [-6, 0]] # test input
#clauses += [[7, 0], [8, 0], [-9, 0], [-10, 0], [-11, 0], [-12, 0]] # test output
clauses += [[-1, 0], [-2, 0]]

#with open("sat_totalizer.cnf", "w") as f:
#	f.write(f"p cnf {l_len+r_len+s_len} {len(clauses)}\n")
#	string = "\n".join([" ".join(map(str, c)) for c in clauses])
#	f.write(string)


# so then we need to make somehow a recursive function I think
# if the len(list) > 2 --> split list into r = 2^floor(log2(len-1)) and len-r long lists
# xxxxxxxxx    or    xxxxxxxxx
# xxxxxxxx x         xxxxx xxxx
# xxxx xxxx x        xxx xx xx xx
# xx xx xx xx x      xx x xx xx xx

import numpy as np
def split_string(s):
	print(f"(debug) {s}")
	if len(s) <= 2:
		print(s)
		return
	l = int(np.power(2, np.floor(np.log2(len(s)-1))))
	#r = len(s) - l
	split_string(s[:l])
	split_string(s[l:])
print(split_string("123456"))

# okay but same idea:
# if the initial list is long, split it, add clauses that would sort the partial lists, then create two
# merge sorts for each of the partial lists
# base case: length is 2 or less: if length two, sort, if length one, use as is? --> maybe better to detect the layer above

# how to efficiently propagate single vars up?
# e.g.
#     xxxxx
#   xxxx   x
#  xx  xx  x
# (original list)

# actually it would be covered by the base case, nvm
# just need to hand the relevant list positions down the chain
# we could get the required offsets and codes easily from the recursion depth

# what is the depth?
# it should be ceil(log2(len)) I think



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

	#print()

	if len(original_list) == 1:
		return (original_list, [])

	if len(original_list) == 2:
		list1 = original_list[:1]
		list2 = original_list[1:]
		list3 = list(map(lambda y: code(depth, y), original_list))
		print(f"sort {list1} and {list2} into {list3}")
		clauses = get_merge_cnf(list1, list2, list3)
		return (list3, clauses)

	l = int(np.power(2, np.floor(np.log2(len(original_list)-1))))
	list1, clauses1 = split_list(original_list[:l], code, depth - 1)
	list2, clauses2 = split_list(original_list[l:], code, depth - 1)
	list3 = list(map(lambda y: code(depth, y), original_list))
	print(f"merge {list1} and {list2} into {list3}")
	clauses3 = get_merge_cnf(list1, list2, list3)
	return (list3, clauses1 + clauses2 + clauses3)

print("-"*10)
lis = [1, 2, 3, 4, 5]
print(f"original list: {lis}")
outlist, clauses = split_list(lis, code = lambda x, y: len(lis)*x + y)
print(outlist)
print(clauses)

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

print(outlist)
print(clauses)
