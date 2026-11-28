Rectangle-free five-colouring of a 27 by 27 grid

Run each .cnf independently as a standard DIMACS CNF. All restrictions are
included as clauses. No assumptions file or special preprocessing is needed.
For a comparison with our pilot, use one core and a 300 CPU-second solver limit.
Please report solver version, CPU model, elapsed time and CPU time for each input.
For SAT, please return a full DIMACS model (signed variable IDs). For UNSAT,
please save a DRAT or LRAT proof against the original input and indicate the
format and whether it is binary. Checking time is separate from solver time.

01-known-unsat.cnf     5,244 variables     1,067,876 clauses
A calibration case. CaDiCaL 1.9.5 via PySAT proved UNSAT in 236.82 CPU seconds.
drat-trim verified the proof in 446.90 CPU seconds. Kissat 4.0.4 and CaDiCaL
3.1.0 each reached the 300 CPU-second limit. Thirteen row images and thirteen
column images are specified for each of two movable templates.

02-open.cnf            5,244 variables     1,067,827 clauses
An unresolved branch. Only the first three row images of the second 147-cell
template are specified (host rows 0,1,2 map to source rows 15,0,2).
Kissat 4.0.4 and both versions of CaDiCaL reached the same 300 CPU-second limit.

The question is whether five colours suffice so that no two rows and two
columns have four corners of the same colour. These formulas cover one family
of candidate colourings. We fix a 147-cell rectangle-free template for the
first colour. The second colour uses another copy and the third uses a
145-cell template. Each movable template has its own row and column permutations.
The three placements must be disjoint. The remaining 290 cells take the last
two colours and must avoid monochromatic rectangles. The inputs share this
base formula and add different placement constraints.

A SAT model on either input decodes to a full grid. Cropping one row and one
column would then also give a 26 by 26 example. An UNSAT proof excludes the
placements allowed by that particular input. The originating paper is
Liu, Chew and Heule, Avoiding Monochromatic Rectangles Using Shift Patterns
(https://arxiv.org/abs/2012.12582).
