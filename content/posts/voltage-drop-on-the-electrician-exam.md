---
title: Voltage Drop on the Electrician Exam: Formula, Traps and a Worked Example
date: 2026-10-10
author: Pass Your Electrician Exam
excerpt: The two voltage-drop formulas, where the constants come from, the 3 and 5 percent recommendations, and a worked example that shows why the obvious conductor is often one size too small.
tags: calculations, NEC
takeaways: Single phase VD = 2 × K × I × L ÷ CM; three phase swaps the 2 for 1.732. K is about 12.9 for copper and 21.2 for aluminium; L is one-way length. | Circular mil areas come from Chapter 9 Table 8; the exam expects you to look them up, not remember them. | The code recommends no more than 3 percent on a branch circuit and 5 percent total; questions use those limits to ask which conductor to install. | The common trap is doubling the length when the formula already includes the return path.
---
Voltage drop questions look like arithmetic and are really about reading. The formula is short, the constants are given or in a table, and the trap is always in the setup: one-way or round-trip length, single or three phase, copper or aluminium, and which limit the question is holding you to.

## The formulas

For a single-phase, two-wire circuit:

VD = 2 × K × I × L ÷ CM

For a three-phase circuit:

VD = 1.732 × K × I × L ÷ CM

Where VD is the drop in volts, K is the resistance of a conductor one circular mil in area and one foot long (about 12.9 ohms for copper and 21.2 for aluminium at 75 degrees), I is the load current in amperes, L is the one-way length of the run in feet, and CM is the conductor's area in circular mils from Chapter 9 Table 8.

The 2 in the single-phase formula is the return path. The 1.732 in the three-phase formula is the square root of three, which accounts for the way currents share the neutral in a balanced three-phase system.

To find the conductor size for a given drop, rearrange: CM = 2 × K × I × L ÷ VD.

## Where the limits come from

The code does not mandate a voltage drop in most installations. The informational notes to 210.19(A) and 215.2(A) recommend no more than 3 percent on a branch circuit or feeder and no more than 5 percent on the two combined. Exam questions treat those recommendations as the target: "to keep voltage drop within 3 percent, what is the minimum conductor size?" Some sensitive-electronics and fire-pump sections set hard limits; know that they exist and that the general case is a recommendation.

## A worked example

A 120 volt single-phase branch circuit supplies a 16 ampere load 150 feet from the panel. The run is copper. What is the minimum conductor to keep the drop within 3 percent?

Three percent of 120 volts is 3.6 volts. Rearrange for circular mils:

CM = 2 × 12.9 × 16 × 150 ÷ 3.6 = 17,200

Chapter 9 Table 8: 12 AWG is 6,530 circular mils, 10 AWG is 10,380, 8 AWG is 16,510, 6 AWG is 26,240. The first size at or above 17,200 is 6 AWG.

Check it: VD = 2 × 12.9 × 16 × 150 ÷ 26,240 = 2.36 volts, about 2 percent. Good. And 8 AWG: 2 × 12.9 × 16 × 150 ÷ 16,510 = 3.75 volts, 3.1 percent, just over the line. The exam wants 6 AWG. A candidate who stops at 12 AWG because that is the normal conductor for a 20 ampere circuit has a drop of 9.5 volts, nearly 8 percent, and the wrong answer.

That is the pattern: ampacity says one thing, voltage drop says another, and on a long run the voltage drop wins.

## The three-phase version

A 208 volt three-phase feeder carries 60 amperes 300 feet on copper. The drop with 4 AWG (41,740 circular mils):

VD = 1.732 × 12.9 × 60 × 300 ÷ 41,740 = 9.63 volts, which is 4.6 percent of 208. Over 3 percent, so a feeder question with a 3 percent target wants 2 AWG (66,360 circular mils): 6.06 volts, 2.9 percent.

## The traps

**Round trip.** If the question gives the total conductor length, divide by two before using the single-phase formula, because the 2 is already there. Most questions give one-way distance; read carefully.

**Aluminium.** K changes to about 21.2 and the answer moves up a size or two. The question will say aluminium; the trap is not noticing.

**Percent of what.** Three percent of 120 is 3.6 volts; of 240 is 7.2; of 277 is 8.31; of 480 is 14.4. Use the circuit voltage in the question, not 120 by habit.

**The limit.** Branch circuit alone, 3 percent. Feeder plus branch circuit, 5 percent total. If the question gives a feeder drop of 2 percent and asks for the branch circuit, you have 3 percent left, which happens to be the same number; if the feeder is already at 3 percent, the branch gets 2.

**Rounding.** Always round up to the next conductor size. A result of 17,200 circular mils is 6 AWG, not 8, even though 8 is close.

## Practice

Do ten problems with the formula on paper, then ten with it from memory. Vary voltage, phase, metal and length. After twenty, the setup becomes the only part that takes thought, and that is where you want to be on exam day.
