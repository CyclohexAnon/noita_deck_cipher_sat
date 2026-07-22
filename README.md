# "solving" deck ciphers with kissat
The main file is `permutation_sat.py` with `deckcipher.py` being an auxilliary script that contains functions for encrypting and decrypting.

## Dependencies
The modules used are `numpy` and `subprocess`. The code is tested under Linux on python 3.12.2.

Also note that the fantastic SAT solver [kissat](https://github.com/arminbiere/kissat) is doing most of the heavy lifting here. Please adjust the paths in `run_kissat_permutation.sh` to your liking. The `-v` option is optional, but may be worth using for long runs to make sure the calculation is, in fact, still running.

## Some explanations
The deck cipher mechanism is explained by Lymm's wiki. (insert link here later) To encode the mechanism as a SAT problem, the following steps are used:

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

