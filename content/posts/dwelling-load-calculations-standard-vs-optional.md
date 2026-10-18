---
title: Dwelling Load Calculations: Standard Method vs Optional Method
date: 2026-10-07
author: Pass Your Electrician Exam
excerpt: The two ways to size a dwelling service under Article 220, worked side by side on the same house, with the demand factors each one uses and the places the exam checks whether you mixed them up.
tags: calculations, NEC, master, journeyman
takeaways: The standard method (220 Part III) applies a different demand factor to each load category; the optional method (220.82) applies one factor to nearly everything. | Standard: general lighting at 3 VA per square foot plus 1500 VA per small-appliance and laundry circuit, first 3000 VA at 100 percent and the rest at 35 percent, then ranges from Table 220.55 and dryers at 5000 VA minimum. | Optional: all loads at nameplate, first 10 kVA at 100 percent and the remainder at 40 percent, plus the larger of heating or cooling. | The question tells you which method to use; if it says optional, do not apply the 35 percent lighting factor.
---
Every journeyman exam has at least one dwelling calculation and master exams have several. There are two methods, they live in different parts of Article 220, and the exam checks whether you can keep them apart. Here they are on the same house.

## The house

A 2,400 square foot single-family dwelling, 120/240 volt single-phase service, with: a 12 kW range, a 5 kW dryer, a 1.2 kW dishwasher, a 1 kW garbage disposer, a 4.5 kW water heater, a 10 kW electric space heater, and a 5 kW central air conditioner. Two small-appliance circuits and one laundry circuit, as the code requires.

## Standard method, Article 220 Part III

**General lighting and receptacles, 220.12.** 2,400 square feet × 3 VA = 7,200 VA.

**Small-appliance and laundry, 220.52.** Two small-appliance circuits × 1,500 = 3,000 VA; laundry 1,500 VA. Subtotal with lighting: 11,700 VA.

**Demand factor, Table 220.42.** First 3,000 VA at 100 percent = 3,000. Remaining 8,700 at 35 percent = 3,045. Lighting and small-appliance demand: 6,045 VA.

**Range, Table 220.55.** One range not over 12 kW: Column C, 8,000 VA.

**Dryer, 220.54.** 5,000 VA or nameplate, whichever is larger: 5,000 VA.

**Fixed appliances, 220.53.** Dishwasher 1,200, disposer 1,000, water heater 4,500: three appliances, so no 75 percent factor (that needs four or more). 6,700 VA.

**Heating versus cooling, 220.60.** The larger of the two: heating 10,000 VA.

**Total.** 6,045 + 8,000 + 5,000 + 6,700 + 10,000 = 35,745 VA. Divide by 240: 149 amperes. Service conductors sized from 310.12 for a dwelling: 150 ampere service, or 200 ampere if the question wants the next common size.

## Optional method, 220.82

**General loads, 220.82(B).** Lighting 7,200 + small-appliance 3,000 + laundry 1,500 + range 12,000 (nameplate, not the table) + dryer 5,000 + dishwasher 1,200 + disposer 1,000 + water heater 4,500 = 35,400 VA.

**Demand.** First 10,000 at 100 percent = 10,000. Remaining 25,400 at 40 percent = 10,160. General demand: 20,160 VA.

**Heating or cooling, 220.82(C).** The largest of the listed options. Air conditioning at 100 percent is 5,000; electric space heating with fewer than four separately controlled units is 65 percent of 10,000 = 6,500. Take 6,500 VA.

**Total.** 20,160 + 6,500 = 26,660 VA. Divide by 240: 111 amperes. A 125 ampere service satisfies the calculation, though 220.82(A) requires at least a 100 ampere service in any case.

## Why they differ

The optional method gives a smaller answer because it assumes diversity across all the loads at once rather than category by category. Both are code-compliant. The exam does not ask which is better; it asks you to perform the one it names.

## Where the exam checks you

**Range.** Standard method uses Table 220.55 (8 kW for a 12 kW range). Optional method uses the nameplate (12 kW). Using the table in the optional method is the most common mistake on this question.

**The 35 percent factor.** It applies only to the lighting, small-appliance and laundry subtotal in the standard method. Applying it to the range or dryer is wrong, and applying it anywhere in the optional method is wrong.

**The 10 kVA split.** Optional method only. The first 10,000 VA at 100 percent and the remainder at 40 percent covers everything except heating and cooling.

**Heating in the optional method.** The percentages in 220.82(C) depend on the kind of heating: 100 percent of air conditioning or heat pump compressors, 65 percent of central electric space heating, 65 percent of fewer than four separately controlled units, 40 percent of four or more. Read the list.

**Fixed appliances.** The 75 percent factor in 220.53 needs four or more appliances and excludes ranges, dryers, space heating and air conditioning. Three appliances get no factor.

**Neutral.** A master exam may ask for the neutral load: 220.61 allows the range and dryer neutral at 70 percent and a further reduction above 200 amperes. Journeyman exams rarely go there.

## Practice

Take one house and run both methods until you can do each in under eight minutes. Then change one load at a time (add a second range, swap the heater for a heat pump, add a fourth appliance) and see what moves. By the fifth variation you will know the two methods as separate procedures, which is what the exam is checking.
