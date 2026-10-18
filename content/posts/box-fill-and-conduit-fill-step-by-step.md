---
title: Box Fill and Conduit Fill, Step by Step
date: 2026-10-09
author: Pass Your Electrician Exam
excerpt: The two fill calculations on every exam, worked from the tables that govern them: how to count conductors in a box under 314.16, and how to size a raceway with Chapter 9 Tables 1, 4 and 5.
tags: calculations, NEC
takeaways: Box fill counts conductors by 314.16(B): each conductor entering the box, all grounds as one, all internal clamps as one, each device as two of its largest conductor. | Volume per conductor comes from Table 314.16(B): 2.00 cubic inches for 14 AWG, 2.25 for 12, 2.50 for 10. | Conduit fill is 40 percent for three or more conductors per Chapter 9 Table 1; add Table 5 conductor areas and pick the raceway from Table 4. | Annex C gives the same answer as Tables 4 and 5 when all conductors are one size and type, and is faster.
---
Fill questions are gifts if you know the two tables and the counting rules, and a time sink if you try to reason them out from scratch. Here is each one as a procedure.

## Box fill

The rule is 314.16: the volume of the box must be at least the sum of the volume allowances for everything in it. The counting rules are in 314.16(B) and the allowances in Table 314.16(B).

**Volume allowance per conductor.** 18 AWG 1.50 cubic inches, 16 AWG 1.75, 14 AWG 2.00, 12 AWG 2.25, 10 AWG 2.50, 8 AWG 3.00, 6 AWG 5.00.

**What counts.**

1. Each conductor that originates outside the box and terminates or is spliced inside: one each. A conductor that passes through the box unbroken counts as one, unless it is looped or coiled inside with at least twice the free-conductor length required by 300.14 (so 12 inches or more), in which case it counts as two. That loop rule is the detail exams test.
2. Equipment grounding conductors: all of them together count as one, based on the largest.
3. Internal cable clamps: all together count as one, based on the largest conductor in the box. External clamps and connectors do not count.
4. Support fittings such as fixture studs or hickeys: one each, based on the largest conductor.
5. Devices: each yoke or strap counts as two conductors, based on the largest conductor connected to that device. A wide device that takes more than one gang space counts two per gang.
6. Pigtails and conductors that do not leave the box: zero.

**Worked example.** A metal box has three 12-2 with ground nonmetallic-sheathed cables entering through internal clamps, feeding one duplex receptacle.

- Conductors: three cables with two insulated conductors each: 6
- Grounds: three, counted as one: 1
- Internal clamps: counted as one: 1
- Device: two: 2
- Total: 10 conductors at 2.25 cubic inches = 22.5 cubic inches

Table 314.16(A): a 4 by 1½ inch square box is 21.0 cubic inches, too small. A 4 by 2⅛ inch square box is 30.3 cubic inches. That is the answer, or a 4 by 1½ square with a raised cover whose marked volume brings the total to 22.5 or more.

**The usual mistakes.** Counting each ground separately. Forgetting the device allowance. Counting the clamp when the cable uses an external connector. Using 14 AWG volume for a 12 AWG box.

## Conduit fill

The rule is in Chapter 9. Table 1 sets the maximum percentage of the raceway's cross-section that conductors may occupy: 53 percent for one conductor, 31 percent for two, 40 percent for three or more. Table 4 gives the internal area of each raceway size and type, with columns already worked out for 40, 53 and 31 percent. Table 5 gives the area of each conductor by insulation type and size.

**Method.**

1. Look up each conductor's area in Table 5 and add them.
2. Open Table 4 for the raceway type (EMT, PVC Schedule 40, RMC and so on).
3. Read down the column for the right percentage (usually 40 percent) and pick the first size whose allowable area meets or exceeds the total.

**Worked example.** How many 12 AWG THHN conductors fit in ¾ inch EMT?

Table 5: 12 AWG THHN is 0.0133 square inches. Table 4, EMT, ¾ inch, 40 percent column: 0.213 square inches. 0.213 ÷ 0.0133 = 16.0, so 16 conductors.

Annex C, Table C.1 for EMT, confirms 16 for 12 AWG THHN in ¾ inch. When all the conductors are the same size and insulation, go straight to Annex C; it is the same arithmetic already done.

**Mixed conductors.** Three 6 AWG THHN (0.0507 each) and one 10 AWG THHN (0.0211) in EMT: total 0.1732 square inches. Table 4, EMT, 40 percent column: ½ inch is 0.122, ¾ inch is 0.213. The answer is ¾ inch EMT.

**The usual mistakes.** Using the total internal area instead of the 40 percent column. Using the wrong insulation type in Table 5 (THW is larger than THHN for the same size). Forgetting that a nipple 24 inches or shorter may be filled to 60 percent under Table 1 Note 4, which is a favourite exam detail.

## Practice

Five of each a day for a week, then mix them. Time yourself: a box fill problem should take under two minutes with the book, a conduit fill problem under ninety seconds with Annex C. If you are slower, the time is going into finding the tables, which is a tabbing problem, not a maths problem.
