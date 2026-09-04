# Predictions, saved verbatim before any Slack message was read
# Saved: 2026-09-04T20:11:02Z

## Predictions, to be filled in and saved before the session runs

The GroupMe baseline, for calibration:

```
window                19 days, 235 messages, 170 operational
constraints           10
override events       20, of which 9 high confidence
rate                  5.3 high confidence per 100 operational
entity recoverable    unreliable
rule recoverable      unreliable
actor recoverable     role only
lead time recoverable rarely
```

Fill in all of these first:

**Pass H, humans only, the fair comparison**

- High confidence events per 100 operational: __15__ (GroupMe was 5.3)
- Coverage of the 24 withheld operating rules: _5___ of 24
- Coverage of the 18 findings from the main run: _2___ of 18
- Entity recoverable, share of events: _20___ %
- Lead time recoverable, share of events: _26___ %

**Pass A, everything**

- High confidence events per 100 operational: _25___
- The gap between A and H that would mean Slack's advantage is mostly the
  operator's own tooling rather than Slack: __10__ percentage points

**The claim being tested**

- Pass H beats GroupMe by at least _10___ on events per 100, or the "move to
  Slack" argument is not supported by this experiment.
- If Pass H roughly matches GroupMe and only Pass A pulls ahead, the honest
  conclusion is: _operator tooling is the key change.___

Write that last sentence before you see the result. It is the one that will be
tempting to rewrite afterwards.
