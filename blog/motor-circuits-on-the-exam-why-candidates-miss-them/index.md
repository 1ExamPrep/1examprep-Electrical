---
title: Motor Circuits on the Exam: Why Candidates Miss Them
url: https://passyourmasterelectricianexam.com/blog/motor-circuits-on-the-exam-why-candidates-miss-them/
updated: 2026-10-29
site: Pass Your Electrician Exam
description: Motor questions use table currents for some things and nameplate currents for others, and the percentages change by device. The four-step method, a worked.
---

[Home](https://passyourmasterelectricianexam.com/) /[Blog](https://passyourmasterelectricianexam.com/blog/) /Motor Circuits on the Exam: Why Candidates Miss Them

October 8, 2026 Pass Your Electrician Exam 3 min read

# Motor Circuits on the Exam: Why Candidates Miss Them

Motor questions use table currents for some things and nameplate currents for others, and the percentages change by device. The four-step method, a worked example and the traps.
[calculations](https://passyourmasterelectricianexam.com/blog/tag/calculations/) · [NEC](https://passyourmasterelectricianexam.com/blog/tag/nec/) · [master](https://passyourmasterelectricianexam.com/blog/tag/master/) · [journeyman](https://passyourmasterelectricianexam.com/blog/tag/journeyman/)

## Key takeaways

- Full-load current for conductors and short-circuit protection comes from Tables 430.247 to 430.250, never the nameplate; overloads come from the nameplate.
- Conductors are sized at 125 percent of table current (430.22); overloads at 115 or 125 percent of nameplate (430.32).
- Branch-circuit short-circuit protection uses the percentages in Table 430.52, with the next standard size up allowed by the exception.
- A 10 horsepower 230 volt three-phase motor needs 35 ampere conductors (10 AWG at 75 degrees) and may have a 70 ampere inverse-time breaker.

Updated October 29, 2026 · prices checked against the 1 Exam Prep store

Article 430 breaks the habit most electricians bring to the exam: that one current number drives everything. For motors, two numbers matter, they come from different places, and each part of the circuit uses its own percentage. Once that is clear the questions are mechanical.

## Two currents

**Table current.** 430.6(A)(1) says that for sizing conductors, switches and branch-circuit short-circuit and ground-fault protection, you use the full-load current from Tables 430.247 (DC), 430.248 (single-phase), 430.249 (two-phase) and 430.250 (three-phase), based on horsepower and voltage. Not the nameplate.

**Nameplate current.** 430.6(A)(2) says that for sizing overload protection you use the motor's nameplate current rating.

Candidates who use the nameplate for conductors get a smaller conductor than the exam wants; candidates who use the table for overloads get the wrong setting. Memorise which is which before anything else.

## The four steps

1. **Conductors, 430.22.** 125 percent of the table full-load current for a single motor. Pick the conductor from Table 310.16 at the 75 degree column (or 60 degree where terminations require it).
2. **Overloads, 430.32.** For a continuous-duty motor over one horsepower: 125 percent of nameplate current if the motor has a service factor of 1.15 or more or a temperature rise of 40 degrees or less; otherwise 115 percent. If that setting does not let the motor start, 430.32(C) allows up to 140 or 130 percent.
3. **Branch-circuit short-circuit and ground-fault protection, 430.52.** Take the percentage from Table 430.52 for the device type: for a typical squirrel-cage AC motor, 300 percent for a nontime-delay fuse, 175 percent for a dual-element time-delay fuse, 250 percent for an inverse-time breaker, applied to the table current. If the result is not a standard size in 240.6, the exception allows the next standard size up.
4. **Disconnect, 430.102 and 430.110.** Within sight of the motor and controller unless the exceptions apply, rated at least 115 percent of the table current.

## Worked example

A 10 horsepower, 230 volt, three-phase squirrel-cage motor, continuous duty, nameplate 26 amperes, service factor 1.15, protected by an inverse-time circuit breaker.

**Table current.** Table 430.250, 10 horsepower at 230 volts: 28 amperes.

**Conductors.** 28 × 1.25 = 35 amperes. Table 310.16, 75 degree column: 10 AWG copper is 35 amperes. 10 AWG.

**Overloads.** Nameplate 26 amperes × 1.25 (service factor 1.15) = 32.5 amperes maximum setting.

**Branch-circuit protection.** Inverse-time breaker: 28 × 2.5 = 70 amperes. 70 is a standard size in 240.6, so a 70 ampere breaker. If the result had been 65 amperes, the exception would allow the next standard size, 70.

**Disconnect.** 28 × 1.15 = 32.2 amperes minimum.

Notice that a 70 ampere breaker protects 10 AWG conductors rated 35 amperes. That looks wrong to candidates who have 240.4 in their heads; it is right because 240.4(G) sends motor circuits to Article 430, where the overloads protect the conductors and the breaker only handles short circuits and ground faults.

## Several motors on one feeder

430.24: feeder conductors carry 125 percent of the largest motor's table current plus the sum of the full-load currents of the rest. 430.62: the feeder protection is the largest branch-circuit protective device for any motor in the group plus the full-load currents of the other motors, not exceeding that total. Exams love a two-motor feeder question because it tests whether you know that only the largest motor gets the 125 percent.

## The traps

**Nameplate for conductors.** The most common miss. If the question gives both a nameplate and a horsepower, the horsepower is there so you can use the table.

**Wrong table.** 430.248 is single-phase, 430.250 is three-phase. Check the phase before reading a number.

**Wrong percentage.** The 250 percent is for inverse-time breakers; a time-delay fuse is 175. The question tells you the device.

**Next size up.** Allowed for the branch-circuit device under 430.52(C)(1) Exception No. 1, not for the overload setting.

**Service factor.** A service factor of 1.15 or a 40 degree rise means 125 percent for overloads; anything else means 115. Read the motor data twice.

## Practice

Work ten motor problems in a row, changing horsepower, voltage, phase and device type each time, with the four steps written at the top of the page. Then ten more without the steps written down. After that, motor questions become the fastest calculation on the exam, because every one follows the same path.

Ready to study?
Pick your state and level, then choose a package.

Every package starts with the state exam prep study guide, built on the 2026 National Electrical Code.
[Pick my package](https://passyourmasterelectricianexam.com/#packs)

## Keep reading

[
What to Expect on Electrician Exam Day, From Che

October 17, 2026 4 min read

## What to Expect on Electrician Exam Day, From Check-In to Your Score

A walk through the day itself: what to bring, what the check-in looks like, how the testing room works, how to pace the clock, and what happens to your result afterwards.
](https://passyourmasterelectricianexam.com/blog/what-to-expect-on-electrician-exam-day/) · [
How to Study for the Journeyman Electrician Exam

October 16, 2026 4 min read

## How to Study for the Journeyman Electrician Exam: A 6-Week Plan

Most people fail the journeyman exam on time, not knowledge. Here is a six-week plan that trains you to find answers in the code book fast, with a calculations block every week.
](https://passyourmasterelectricianexam.com/blog/how-to-study-for-the-journeyman-electrician-exam/) · [
How the Journeyman Electrician Exam Is Structure

October 16, 2026 4 min read

## How the Journeyman Electrician Exam Is Structured

Question counts, time limits, the content outline, how the pass mark works, and which code articles carry most of the weight on a typical state journeyman exam.
](https://passyourmasterelectricianexam.com/blog/how-the-journeyman-electrician-exam-is-structured/)

---

Source: https://passyourmasterelectricianexam.com/blog/motor-circuits-on-the-exam-why-candidates-miss-them/  
Publisher: Pass Your Electrician Exam. Orders are fulfilled by 1 Exam Prep (https://1examprep.com). Phone (877) 775-9400, email sales@1examprep.com.  
Prices change; the product page and checkout show the current price.
