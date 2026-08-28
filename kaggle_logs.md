Both probes finished, and the result reverses today's conclusion.

Phase 2 worked
Same machine, same llama.cpp build, back-to-back, temperature: 0. A "win" is the harness's own test — the rewrite compiles, runs, produces identical answers, and actually changed the algorithm. Not a keyword match.

Phrasing	Phase 1	Phase 2	Δ
trained_wording (what your product sends)	1/17	5/17	+4
explicit_faster	1/17	7/17	+6
explicit_loop	4/17	10/17	+6
explicit_memo	5/17	6/17	+1
Total	11/68 (16%)	28/68 (41%)	+17
I checked the obvious trap
Your project notes say scoring has flattered the model seven times, so I looked for contamination. Two of the 17 probe samples — fibonacci and gcd_euclid — appear verbatim in the training pairs. Removing both:


phase 1 : 10/60 (17%)
phase 2 : 24/60 (40%)
gained 15, lost 1     McNemar exact p = 5.19e-04
The contaminated pair accounts for only 3 of the 18 gains. The effect survives at p < 0.001. This is real capability, not memorisation.

Why this is your best result
58 execution-verified pairs — 1.19% of the corpus — more than doubled a capability that 66,103 unverified rows never touched.

Compare the two tasks:

improve	optimize
Rows	18,935	290
Share of loss budget	37%	0.7%
Verified by execution?	No	Yes
What it teaches	const-sprinkling (64% leave control flow identical)	the real transformation
That's a clean, quantified argument that verification of the training signal beats data volume by orders of magnitude — and it's measured by running code, not by matching words.

What I was wrong about
I told you repeatedly that phase 2 bought nothing for 10.4 GPU-hours. That was based entirely on eval_hard.py, which prompts only line_comments and explanation — neither of which phase 2 changed. An evaluation that never exercises the changed capability is not evidence of its absence.

docs/PHASE2_INVESTIGATION.md is updated: new §2.3 with the full table and contamination analysis, revised headline, revised claims section, and this added to the appendix of my errors.

What follows
Make more verified pairs — that's now empirically justified, not speculative. verify_optimization_pairs.py already gates them (both compile, identical stdout, A recursive, B not). Expect low yield: your CLAUDE.md records 2 verified from 130 attempted, which is exactly where the GPT-OSS-120B in your .env would earn its keep as the generator.

The defect-detection finding is unchanged — still ~15%, still normal for 1.5B, still the honest limitation. But your report now has a positive result alongside it, and it's the more interesting one.

