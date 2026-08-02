# "solving" deck ciphers with kissat
The main file is `permutation_sat.py` with `deckcipher.py` being an auxilliary script that contains functions for encrypting and decrypting.

## Dependencies
The modules used are `numpy` and `subprocess`. The code is tested under Linux on python 3.12.2.

Also note that the fantastic SAT solver [kissat](https://github.com/arminbiere/kissat) is doing most of the heavy lifting here. Please adjust the paths in `run_kissat_permutation.sh` to your liking. The `-v` option is optional, but may be worth using for long runs to make sure the calculation is, in fact, still running.

## Some explanations
The deck cipher mechanism is explained by [Lymm's wiki](https://github.com/Lymm37/eye-messages/wiki/Group-Autokey-%28GAK%29). To encode the mechanism as a SAT problem, the following steps are used:

For each possible plain text letter, generate a permutation matrix $\mathbf{P}(i) \in \mathbb{B}^{\mathrm{ct\_alphabet} \times \mathrm{ct\_alphabet}}$ corresponding to the assigned shuffling of the deck.

For each possible deck state, generate a permutation matrix $\mathbf{D}(i) \in \mathbb{B}^{\mathrm{ct\_alphabet} \times \mathrm{ct\_alphabet}}$.

This means, that for a given plain text letter $\mathrm{pt}(i) = k$ the recurrence $\mathbf{D}(i+1) = \mathbf{P}(i) \mathbf{D}(i)$ holds.

If the plain text is known and should be tested, no other data structures are needed. By additional constraints, the following things are enforced:

The initial deck is ordered: $\mathrm{D}(0)$ is an identity matrix.

For reversibility reasons we want each plain text letter to reveal a different top card, which means that each top row of the plain text letter permutation matrices are different: $\mathbf{P} _{0*}(i) \neq \mathbf{P} _{0*}(j)$ for $i \neq j$.

We also need to encode the fact that the shuffling process produces the cipher text, which means that if the $i$th cipher text letter is $\mathrm{ct}(i) = k$, the decks top row needs to reflect that: $\mathbf{D}_{0k}(i) = 1$.

If on the other hand the plain text is not known, then every permutation could come from some unknown $\mathbf{P}(i)$. Therefore another matrix is used to denote one chosen position from the plaintext alphabet: $\mathbf{T} \in \mathbb{B}^{\mathrm{pt\_length} \times \mathrm{pt\_alphabet}}$. Each row $\mathbf{T}_{i*}$ must contain only one 1.

The shuffling of the deck changes accordingly: if $\mathbf{T}_{ij} = 1$, then $\mathbf{D}(i+1) = \mathbf{P}(j) \mathbf{D}(i)$.

(Hopefully there werent any mistakes in that description.)

## Math details
Since kissat accepts input in CNF (conjunctive normal form), the constraints are encoded as such.

### Permutation matrices
In order to encode a permutation matrix, $n \times n$ variables are generated. Then for the row $k$ the condition $\bigvee _i a _{ik}$ ensures at least one variable is true per row. The relation
$\bigwedge _i \bigwedge _{j > i} \neg a _{ik} \vee \neg a _{jk}$ ensurses for row $k$ that at most one element can be true (because every possible pair must have at least one false element). The same is done for each column. In the end this results in $n^2$ variables and $n(n+1)$ conditions.

For our case, $n$ is the length of the cipher text alphabet or equivalently the deck size. We need one matrix per letter in the plain text alphabet, one for the inital deck and then for each letter of plain text another deck state, giving $(\mathrm{pt\_alphabet} + \mathrm{pt\_size} + 1) \cdot n^2$ variables and $(\mathrm{pt\_alphabet} + \mathrm{pt\_size} + 1) \cdot n(n+1)$ conditions.

### Permuting the deck (without selectors)
Since permuting the deck is basically matrix multiplication, we can use a matrix multiplication algorithm. However, it is possible to cut down on conditions by using the fact we are dealing with permutation matrices. For the product $\mathbf{A} \mathbf{B} = \mathbf{C}$ where each is a permutation matrix (in our case one permutation matrix acting on the state of the deck), we need $\bigwedge _{i, j, k} \neq a _{ik} \vee \neq b _{kj} \vee c _{ij}$ giving $n^3$ conditions per multiplication.

Because we need one multiplication per letter in the plain text, this results in an additional $\mathrm{pt\_size} \cdot n^3$ with $n$ as the length of the cipher text alphabet.

### Permuting the deck (with selectors)
If the plain text is not known, we need to introduce another matrix to hold the options for the plain text.

This is basically a matrix of size pt times pt_alphabet, and we impose constraints as for permutation matrices, but only for the rows, which encodes the fact that each true entry in this matrix corresponds to a choice for one plaintext letter.

The multiplication is then modified to $\bigwedge _{i, j, k, z} \neg s _z \vee \neg a _{ik} (z) \vee \neg b _{kj} \vee c _{ij}$ with $a(z)$ being an element in one specific permutation matrix for the plain text letters. (This works because every selector variable that is set to False will, due to being negated, will trivially satisfy that specific condition and essentially make it drop out. Only one clause will remain, the chosen one).

The new variables added amount to $\mathrm{pt\_size} \cdot \mathrm{pt\_alphabet}$ and the clauses scale with $\mathrm{pt\_alphabet} \cdot n^3$.

### Everything else
Everything else is just setting specific variables to True or False, which scales much slower than everything else and does not incur additional variables, so I am not going to bother calculating it.


## Some results and experimental observations
### Shortest orphan ciphertexts
For some combination of pt alphabet sizes and cipher text alphabets, there exist combinations of ciphertext symbols for which there is no plaintext/permutation table combination that produces them. In other words, some ciphertexts are unreachable. I call these orphan cipher texts (they have no parents).

Unless we explicitely disallow double letters as we would for the eyes, short enough cipher texts are never orphans. There exists a minimum length of cipher text before it is possible for it to be an orphan, below it all cipher texts have some plain text/permutation table combination that produces them.

Unfortunately the number of ciphertexts grows exponentially with the length of the cipher text, and the minimum orphan length also seems to grow fast with the size of the plain text alphabet, so I was only able to exhaustively calculate it for small sizes.

For a plain text alphabet of size 2 below the (reachable cipher texts, unreachable cipher texts).

| Length | cta = 3        | cta = 4         | cta = 5          | cta = 6          | cta = 7           |
| ------ | -------------- | --------------- | ---------------- | ---------------- | ----------------- |
| 1      | (3,0)          | (4,0)           | (5,0)            | (6,0)            | (7,0)             |
| 2      | (9,0)          | (16,0)          | (25,0)           | (36,0)           | (49,0)            |
| 3      | (27,0)         | (64,0)          | (125,0)          | (216,0)          | (343,0)           |
| 4      | (73,8)         | (232,24)        | (577,48)         | (1216,80)        | (2281,120)        |
| 5      | (171,72)       | (736,288)       | (2357,768)       | (6176,1600)      | (13927,2880)      |
| 6      | (393,336)      | (2200,1896)     | (9145,6480)      | (29956,16700)    | (81709,35940)     |
| 7      | (855,1332)     | (6220,10164)    | (33701,44424)    | (137996,141940)  | (456403,367140)   |
| 8      | (1841,4720)    | (16594,48942)   | (121729,268896)  | (628616,1051000) | (2523661,3241140) |
| 9      | (3863,15820)   | (41638,220506)  | (413717,1539408) |                  |                   |
| 10     | (8053,50996)   | (98998,949578)  |                  |                  |                   |
| 11     | (16567,160580) |                 |                  |                  |                   |
| 12     | (33941,497500) |                 |                  |                  |                   |

For a plain text alphabet of size 3:

| Length | cta = 4        | cta = 5        | cta = 6         |
| ------ | -------------- | -------------- | --------------- |
| 1      | (4,0)          | (5,0)          | (6,0)           |
| 2      | (16,0)         | (25,0)         | (36,0)          |
| 3      | (64,0)         | (125,0)        | (216,0)         |
| 4      | (256,0)        | (625,0)        | (1296,0)        |
| 5      | (1024,0)       | (3125,0)       | (7776,0)        |
| 6      | (4096,0)       | (15625,0)      | (46656,0)       |
| 7      | (16384,0)      | (78125,0)      | (279936,0)      |
| 8      | (65536,0)      | (390625,0)     | (1679616,0)     |
| 9      | (261568,576)   | (1951829,1296) | (10074816,2880) |
| 10     | (1039816,8760) |                |                 |

(For longer ct alphabets I was only able to find the following orphan examples of length 9 for cta = 7 ("AGAEGBFGF") and 8 ("ABABEBDGB"), both found with CAQE.)

From these small experiments it seems as though eventually, by increasing the length by 1, the number of reachable ciphertexts grow with the pt alphabet size and the unreachable ciphertexts grow with the size of the ct alphabet. This would mean eventually, almost all ciphertexts are unreachable.

The shortest orphan cipher text seems to grow only by the size of the plain text alphabet size, not by the cipher text alphabet from this sample. However, this may be incorrect.

If, given some pt alphabet size and ct alphabet size, and some orphan cipher text, does increasing the cipher text alphabet eventually make it reachable? For pt alphabet sizes of 2 and 3 the answer seems to be no, but in general this is not true. Here is a concrete counter example:

Consider the ct `AEBACDCADAEDEBEDEACBDACDBABCABCBC` with a pt alphabet size of 4. Using a ct alphabet size of 5 and 6, this is an orphan, however, using an alphabet size of 7, it no longer is. One possible plaintext/permutation table combination is:

```
pt = "acbbbccdccbbdbdbddbcddcddccdcdccc"
permutation_table = [[0 5 6 3 4 1 2]
                     [6 2 3 0 5 1 4]
                     [4 1 3 2 0 6 5]
                     [3 5 0 2 4 6 1]]
```

It is possible to show the length of the shortest orphan ciphertext is finite when the ciphertext alphabet is at least one larger than the plaintext alphabet. The construction is like so: Create a ciphertext. Find a pt/permutation table pair that creates it. If none exist, we are done. If it does, look at the state of the deck after the last plaintext letter. Look at the permutation table. Since ct alphabet > pt alphabet, there is at least one card in the deck that cannot be reached by adding any pt letter to the found pt. Append the unreachable ct letter to the ct, and repeat. This invalidates the current permutation table, and since we can extend the ct arbitrarily long, but there are only a finite number of permutation tables, eventually we exhaust all of them. So eventually we hit an unreachable ct.

This algorithm does however not, in general, find the shortest possible orphan ct.





















































