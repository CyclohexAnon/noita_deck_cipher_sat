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

For reversibility reasons we want each plain text letter to reveal a different top card, which means that each top row of the plain text letter permutation matrices are different: $\mathbf{P}_{0*}(i) \neq \mathbf{P}_{0*}(j)$ for $i \neq j$.

We also need to encode the fact that the shuffling process produces the cipher text, which means that if the $i$th cipher text letter is $\mathrm{ct}(i) = k$, the decks top row needs to reflect that: $\mathbf{D}_{0k}(i) = 1$.

If on the other hand the plain text is not known, then every permutation could come from some unknown $\mathbf{P}(i)$. Therefore another matrix is used to denote one chosen position from the plaintext alphabet: $\mathbf{T} \in \mathbb{B}^{\mathrm{pt\_length} \times \mathrm{pt\_alphabet}}$. Each row $\mathrm{T}_{i*}$ must contain only one 1.

The shuffling of the deck changes accordingly: if $\mathrm{T}_{ij} = 1$, then $\mathbf{D}(i+1) = \mathbf{P}(j) \mathbf{D}(i)$.

(Hopefully there werent any mistakes in that description.)

