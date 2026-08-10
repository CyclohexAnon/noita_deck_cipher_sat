include "globals.mzn";

int: pt_len = 4;
int: pt_alphabet_size = 3;
int: ct_alphabet_size = 4;

array[1..pt_len] of int: ct = [1, 0, 2, 2];
array[1..pt_len] of var 0..(pt_alphabet_size-1): pt;

set of int: pt_alphabet = 0..(pt_alphabet_size-1);
set of int: ct_alphabet = 0..(ct_alphabet_size-1);

array[pt_alphabet, ct_alphabet] of var 0..(ct_alphabet_size-1): permutation_table;
array[0..pt_len, ct_alphabet] of var 0..(ct_alphabet_size-1): deck;

% each row is a permutation
constraint forall(p in pt_alphabet)(all_different([permutation_table[p, i] | i in ct_alphabet]));

% first column has unique entries
constraint all_different([permutation_table[p, 1] | p in pt_alphabet]);

% first deck state is ordered
constraint forall(c in ct_alphabet)(deck[0, c] = c);

% each row is a permutation
constraint forall(p in 1..pt_len)(all_different([deck[p, i] | i in ct_alphabet]));

% each following row is the previous row, permuted by the permutation table row for that pt letter
constraint forall(p in 1..pt_len, i in ct_alphabet)(deck[p, i] = deck[p-1, permutation_table[pt[p], i]]);

% the ciphertext are the 0th column of the deck
constraint forall(p in 1..pt_len)(deck[p, 0] = ct[p]);

solve satisfy;