# Commit hashes, private original to public extraction

This repository was extracted from a private repository with
`git subtree split`, then rewritten once to replace four personal names with
roles. Both operations change commit hashes. **Commit dates and authorship are
unchanged**, and the dates are what the pre-registration argument rests on.

`PRE-REGISTRATION.md` and `RESULTS.md` cite the private hashes because they
were written before the extraction. This table maps them.

| private | public | date, UTC | what it is |
| --- | --- | --- | --- |
| `b2355c6` | `46fa01a` | 2026-08-29 14:30 | the loader and the denylist |
| `4af86f6` | `4363b34` | 2026-08-29 14:34 | all four probes and the scorer |
| `016e43f` | `70532b1` | 2026-09-04 04:07 | the key frozen, first time |
| `6c92bf4` | `85af2bf` | 2026-09-04 04:13 | the key re-frozen at 8ab6bedd |
| `9165361` | `36a8735` | 2026-09-04 04:30 | loader bug one, before any run |
| `3b03f21` | `bcbd296` | 2026-09-03 22:35 | run one pre-registered |
| `ecc088b` | `5b7a697` | 2026-09-04 16:02 | loader bug two, mid protocol |
| `7526573` | `2934b65` | 2026-09-04 10:13 | run two pre-registered |

The answer key's own hash, `8ab6bedd`, is a hash of the file's contents and is
unaffected by any of this. `cli.py score` recomputes it on every run and
reports whether it still matches `key/key_hash.txt`. It does.
