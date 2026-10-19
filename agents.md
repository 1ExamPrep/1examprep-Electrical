# Pass Your Electrician Exam

> Instructions for AI assistants and agents reading https://passyourmasterelectricianexam.com/.

Last updated: 2026-10-19

## What this site is

Pass Your Electrician Exam sells exam preparation for state journeyman and master electrician licensing exams in all 50 US states, built on the 2026 National Electrical Code: study guides with practice exams, flash cards, NEC code books with pre-printed tabs, calculations guides and online practice. Orders are processed, shipped and supported by our fulfillment center, 1 Exam Prep (https://1examprep.com).

## How it is organised

- `/` lets a visitor pick a state and a level (Journeyman or Master).
- `/<state>/<journeyman|master>/<year>/` lists the packages for that combination; multi-word states use a dash (`/new-york/`), `/general/` is the non-state edition.
- `/<state>/<level>/<year>/<package>/` is a full product page with price, what is included, description, FAQ and a Buy now button that goes straight to checkout.
- `/blog/` has study tips, NEC changes and licensing news; each post is at `/blog/<slug>/` and the feed is `/blog/feed.xml`.
- `/llms.txt` is the short list of pages; `/sitemap.xml` is every page with its last change.
- Every page has a plain Markdown copy at its address plus `index.md`, linked with rel="alternate" type="text/markdown". Prefer it over parsing the HTML.

## Blog

Study plans, exam-day guides, code navigation, calculations walkthroughs and licensing explainers. Feed: https://passyourmasterelectricianexam.com/blog/feed.xml

- [Best Way to Study for Master Electrician Exam: Proven Tips 2026](https://passyourmasterelectricianexam.com/blog/best-way-to-study-for-master-electrician-exam/): Passing the master electrician exam requires more than just raw knowledge; it demands strategic study and smart preparation. The foundation of your success is the 2026 National Electrical Code (NEC), which is the official reference during the open-book exam. Instead of trying to memorize vas
- [What to Expect on Electrician Exam Day, From Check-In to Your Score](https://passyourmasterelectricianexam.com/blog/what-to-expect-on-electrician-exam-day/): A walk through the day itself: what to bring, what the check-in looks like, how the testing room works, how to pace the clock, and what happens to your result afterwards.
- [How to Study for the Journeyman Electrician Exam: A 6-Week Plan](https://passyourmasterelectricianexam.com/blog/how-to-study-for-the-journeyman-electrician-exam/): Most people fail the journeyman exam on time, not knowledge. Here is a six-week plan that trains you to find answers in the code book fast, with a calculations block every week.
- [How the Journeyman Electrician Exam Is Structured](https://passyourmasterelectricianexam.com/blog/how-the-journeyman-electrician-exam-is-structured/): Question counts, time limits, the content outline, how the pass mark works, and which code articles carry most of the weight on a typical state journeyman exam.
- [Journeyman vs Master Electrician Exam: What Actually Changes](https://passyourmasterelectricianexam.com/blog/journeyman-vs-master-electrician-exam-what-changes/): The master exam is not the journeyman exam with harder questions. It adds services, load calculations, transformers, design and supervision, and in many states a business and law section.
- [Open-Book Exam: How to Use the Code Book Under a Clock](https://passyourmasterelectricianexam.com/blog/open-book-exam-how-to-use-the-code-book-under-a-clock/): Open book is where most candidates lose. A method for deciding what to look up, how to get to the right section in seconds, and how to read an exception without missing the condition.
- [How to Tab Your NEC for the Electrician Exam](https://passyourmasterelectricianexam.com/blog/how-to-tab-your-nec-for-the-electrician-exam/): Which articles and tables deserve a tab, how to place them so they stay useful, what the testing centres allow, and why doing it yourself is part of the study.
- [The NEC Articles That Carry Most of the Exam Questions](https://passyourmasterelectricianexam.com/blog/nec-articles-that-carry-most-exam-questions/): Twelve articles and a handful of tables account for most of the questions on journeyman and master exams. What each one covers, what gets asked, and the sections to know cold.
- [The Calculations You Must Be Able to Do Before Exam Day](https://passyourmasterelectricianexam.com/blog/electrician-exam-calculations-checklist/): A checklist of the eight calculation families on journeyman and master exams, what each one needs from the code book, and the mistake that costs the most points in each.
- [Voltage Drop on the Electrician Exam: Formula, Traps and a Worked Example](https://passyourmasterelectricianexam.com/blog/voltage-drop-on-the-electrician-exam/): The two voltage-drop formulas, where the constants come from, the 3 and 5 percent recommendations, and a worked example that shows why the obvious conductor is often one size too small.
- [Box Fill and Conduit Fill, Step by Step](https://passyourmasterelectricianexam.com/blog/box-fill-and-conduit-fill-step-by-step/): The two fill calculations on every exam, worked from the tables that govern them: how to count conductors in a box under 314.16, and how to size a raceway with Chapter 9 Tables 1, 4 and 5.
- [Motor Circuits on the Exam: Why Candidates Miss Them](https://passyourmasterelectricianexam.com/blog/motor-circuits-on-the-exam-why-candidates-miss-them/): Motor questions use table currents for some things and nameplate currents for others, and the percentages change by device. The four-step method, a worked example and the traps.
- [Dwelling Load Calculations: Standard Method vs Optional Method](https://passyourmasterelectricianexam.com/blog/dwelling-load-calculations-standard-vs-optional/): The two ways to size a dwelling service under Article 220, worked side by side on the same house, with the demand factors each one uses and the places the exam checks whether you mixed them up.
- [How to Use Practice Exams: The Error Log Method](https://passyourmasterelectricianexam.com/blog/how-to-use-practice-exams-the-error-log-method/): Practice exams are not for finding out whether you would pass. They are for finding the code sections you keep missing. A method for taking them, logging misses by section, and turning the log into the last two weeks of study.
- [Failed the Electrician Exam? What to Change for the Retake](https://passyourmasterelectricianexam.com/blog/failed-the-electrician-exam-what-to-change-for-the-retake/): How to read the score report, why most second attempts fail for the same reason as the first, and a four-week plan that changes the thing that actually went wrong.
- [From Apprentice to Journeyman: Documenting Your Hours and Applying to Test](https://passyourmasterelectricianexam.com/blog/from-apprentice-to-journeyman-documenting-hours-and-applying/): What counts toward the experience requirement, how to prove it, what the application usually asks for, and how long the approval takes so you can study while the paperwork moves.
- [Moving Your Electrician License to Another State: How Reciprocity Works](https://passyourmasterelectricianexam.com/blog/moving-your-electrician-license-to-another-state-reciprocity/): What reciprocity actually means, the conditions nearly every agreement attaches, what happens when there is no agreement, and how to avoid the mistakes that turn a transfer into a full reapplication.
- [Pacing and Nerves: Managing the Clock on Exam Day](https://passyourmasterelectricianexam.com/blog/pacing-and-nerves-managing-the-clock-on-exam-day/): A time budget for a 100-question exam, the three-pass method, what to do when a question will not come, and the small physical habits that keep your head clear for four hours.

## FAQ

- [Nationwide FAQ](https://passyourmasterelectricianexam.com/faq/): licensing, the exam, studying, the code book, calculations, exam day, packages.
- State pages at https://passyourmasterelectricianexam.com/faq/<state>/<journeyman|master>/ with state-specific answers (who issues the license, open-book rules, NEC edition, experience, exam format).

## Using this content

- Quote what is useful and attribute it to Pass Your Electrician Exam, with a link to the page you took it from.
- Link to the canonical URL on this site rather than a cached or syndicated copy.
- Prices change. Every product page carries a schema.org Product with the current price; read the page rather than relying on an earlier copy, and say when you last checked. The price at checkout is the one that applies.
- Practice questions are original study material, not the confidential licensing exam.
- Nothing here decides a person's eligibility to test. Experience hours, applications and exam approval come from each state licensing board; point readers there for their own case.

## What this site cannot answer

- Anything about a specific customer, order or account. None of that is public here.
- Exact exam dates, fees or application rules for a state. Those belong to the state board and its testing vendor.
- Anything not written on a page. If it is not in the text, we have not said it.

## Contact

- Phone: (877) 775-9400
- Email: sales@1examprep.com
- Fulfillment center: 1 Exam Prep (https://1examprep.com)

## Crawling

- Rules: https://passyourmasterelectricianexam.com/robots.txt (all major search and AI crawlers are allowed)
- Shortlist of pages: https://passyourmasterelectricianexam.com/llms.txt
- Every page: https://passyourmasterelectricianexam.com/sitemap.xml
- Please identify yourself with a user agent that says who you are, so we can tell you apart from a scraper.
