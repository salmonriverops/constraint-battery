# Results

Draft of the follow-up post, written from `runs/2026-09-04-crewfix-full/score.md`,
`runs/2026-09-04-crewfix-lean/score.md` and `delta.md`. Every number in it is
reproducible by running `cli.py score` against the committed match files.

---

Two weeks ago I said I was testing whether the operating rules of my company
could be found by analysis instead of by memory, and that I would post the
number whatever it was.

The number is 10 percent.

Sixty three operating constraints in the answer key. The battery recovered six.
Against the rules I could write down from memory alone, with no documents open,
it recovered three of thirty five.

I said in advance what that would mean. If very few came back, what I have is
judgment rather than a method. By my own stated criterion, that is the answer.
Recovering a known rule set from transaction records is not something this
does. Gear rules, nothing out of thirteen. Timing rules, nothing out of seven.
Sequencing, nothing out of three. Those are not near misses, they are whole
categories the data cannot express.

I am aware that what follows reads like finding a consolation prize in a failed
test. Here is why I do not think it is one.

The same run surfaced eighteen real constraints that two years of manual work
never wrote down. Not variations on rules I had. New ones. How a bus can serve
three trips in a day if the pickups line up. Why a guide driving their own
trip's shuttle is not a double booking. Which trips are exempt from a seat
count because the guests shuttle themselves. That a stated capacity of 120 is
conservative and the real number is closer to 140.

Fourteen of those eighteen came from one place: the log of times a human
overruled the system.

I ran the whole thing again on a thinner export, the kind a normal business
would actually have, with that override log removed. Recall fell from 10
percent to 2 percent. Findings fell from eighteen to three. Every constraint
about eligibility, vehicles, leads and jetboats disappeared entirely.

So the finding is not the one I expected, and it is more useful.

The rules a business has already written down are not sitting in its
transaction records waiting to be recovered. But the record of when somebody
overrode the system is dense with rules nobody ever wrote down, and it is the
cheapest thing in the stack to instrument.

With one precondition that I should state rather than let someone else find. An
override log only exists once there is something to override. A business run off
a whiteboard produces no override events, so this offers it nothing directly.
That is not a caveat on the finding. It is most of the finding.

One caveat that has to travel with the number, because it is the first thing I
would attack if someone else published this. The battery did not state
eighteen rules. It found eighteen places where an undocumented rule was
operating, and I supplied the rule. A probe said "somebody overrode this seven
times, what does the system keep getting wrong." I said "that is the owner, he
holds an outfitting license, he does not need a guide license." Knowing where
to ask is worth a great deal. It is not the same as knowing.

What went wrong, since a test you only report the tidy parts of is not a test.
Two loader bugs, one caught before the run and unremarkable. The second read an
empty field for trip crew while the real crew sat in five other fields, so no
guide on any day trip reached the analysis at all. I found it while judging
candidates, after the first run was already pre registered. I stopped, fixed it,
and re ran, keeping both runs and recording the reason before anything was
scored. I also predicted at the start that the override log would produce the
fewest findings of the four probes. It produced almost all of them.

The answer key was frozen and hashed before either run. It was never edited.
Every number above traces to a committed file, including the mistakes. The
repository is private because it is built around my company's data, so
"checkable" means I will walk anyone who asks through it rather than that you
can go and look right now.

If you work on getting rules out of people, in research or in a product, the
override log is where I would look first. I would like to compare notes.

---

## Where each number comes from

| Claim | Source |
| --- | --- |
| 10 percent, 6 of 63 | `runs/2026-09-04-crewfix-full/score.md`, headline |
| 3 of 35 from memory alone | same file, remembered against written down |
| 18 findings | same file, new constraints found |
| 14 of 18 from the override log | `match.csv`, novelty by probe, p08 |
| 10 percent to 2 percent on the lean run | `delta.md`, headline |
| Categories lost entirely | `delta.md`, which constraint types survive |
| Key frozen at `8ab6bedd`, never edited | `key/key_hash.txt`, recomputed on every score |
| Both loader bugs | `KNOWN-ISSUES.md` and commits `9165361`, `ecc088b` |
| The re run and its reasoning | `PRE-REGISTRATION.md`, a second run and why |
| The one corrected verdict | `PRE-REGISTRATION.md`, a corrected verdict |
