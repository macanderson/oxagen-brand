# Messages

This folder is the registry of every line Oxagen and Stella publish: headlines, pitches, product page sections, feature cards, entry points, proof points, outreach, ads, voice pairs, and the rules writers follow. One YAML file holds one entry.

The registry is the source of truth. `message-bank.html`, `messages/index.json`, and the ad copy in `build/build.py` are generated from it. A copy change starts here, never in the generated files.

The entries follow the adversarial messaging review of 2026-09-15. `findings.yaml` lists its ten findings, each with the rule it imposes, and every entry names the findings that shaped it.

## Layout

```
messages/
  README.md           this file
  schema.json         JSON Schema for one entry
  findings.yaml       the review's findings and the rule each imposes
  index.json          generated: every entry, sorted, for apps/web and other readers
  lead/               hero headline and eyebrow, pitches, the mandate and its clauses, taglines
  sections/           product page sections, docs, and UI strings
  entry-points/       the security, finance, knowledge, and operator review pages
  access/             the access headline and the rules for writing about keys
  proof/              proof points, hypothetical buyer statements, the demo
  workforce/          feature cards 1 to 16
  definition-of-done/ feature cards 17 to 20 and the passing verdict
  witness/            feature cards 21 to 28 and the definition of proven
  identity-equipment/ feature cards 29 to 33
  outreach/           the launch announcement and sales emails
  ads/                ad campaigns, rendered by build/build.py
  voice/              before and after pairs, and word swaps
  rules/              internal rules, including the phrase blocklists
  retired/            lines that are no longer used, with their replacements
```

The folder an entry sits in is its group. The page renders each group in its own section.

## Fields

| Field | Required | Meaning |
|---|---|---|
| `id` | yes | Kebab case, unique, and equal to the file name without `.yaml`. |
| `brand` | yes | `oxagen` or `stella`. |
| `kind` | yes | `headline`, `eyebrow`, `pitch`, `section`, `card`, `entry-point`, `rule`, `proof`, `pair`, `email`, `announcement`, `ad`, or `glossary`. |
| `order` | no | Position within the group on the page. |
| `title` | yes | The line itself. For a pitch, rule, pair, or glossary entry, its label. For an email, the subject. |
| `short`, `long` | no | The short form and the long form. |
| `cta`, `cta_destination` | no | The action, and what it must lead to. |
| `audience` | yes | One or more of `operator`, `platform`, `security`, `finance`, `engineering`, `knowledge`, `investor`. |
| `clause` | yes | `access`, `budget`, `equipment`, `record`, `operations`, or `none`. |
| `surfaces` | yes | Where the entry is used, as free labels such as `site-hero` or `sales-email`. |
| `status` | yes | `candidate`, `approved`, or `retired`. |
| `release` | unless retired | `launch`, or `held` until a capability ships. |
| `gate` | when held | The capabilities the entry waits for, such as `dod`, `witness`, `budgets`, `reconciliation`, `stella-integration`. |
| `qualifier` | no | The scope sentence every short form must keep. |
| `evidence` | approved launch copy | What must be demonstrated for the claim to stand at launch. |
| `owner` | yes | The role accountable for the claim. |
| `review_by` | unless retired | ISO date. The check warns once it has passed. |
| `findings` | yes | Ids from `findings.yaml`. May be empty. |
| `replaced_by` | retired | The entry that replaces it. May be null when `notes` says why. |
| `notes` | no | Internal context. |

Ads also carry `kicker`, `headline` (the tall stack), `wide` (the landscape lines), `short_lines` (the 300x250), `subline`, `subshort`, `picture` (`ghost` or `orbit`), and `scope_terms`. The ad id is `ad-<brand>-<slug>`, and the slug names the files in `ads/`. `headline` and `wide` must join to the title. Every `subline` and `subshort` must contain one of the `scope_terms`, so a short form cannot drop its scope.

Pairs carry `before` and `after`. Sections that are tables carry `rows`, each with a `label` and `text`. Rules may carry `phrases`, which the check rejects in live copy.

## Statuses

- **candidate**: written, not yet approved. It appears on the page, marked, and is never rendered as an ad.
- **approved**: usable. With `release: launch` it can ship now. With `release: held` it waits for its `gate`.
- **retired**: no longer used. The page lists it beside its replacement, and the check fails if its text reappears in an approved entry.

The comprehension testing the review recommends is recorded in `notes` or `evidence`, not as a status.

## Add an entry

1. Create `messages/<group>/<id>.yaml` with the required fields. Copy a neighbour in the same group.
2. Name the findings it answers and, for approved launch copy, the evidence and the owner.
3. Run the check, then regenerate.

## Retire an entry

1. Move the file to `messages/retired/`.
2. Set `status: retired`, remove `release`, `gate`, and `review_by`, and set `replaced_by` to the entry that takes its place. When nothing replaces it, set `replaced_by: null` and say why in `notes`.
3. If it was an ad, regenerate the ads so its files leave `ads/`.

## Regenerate and check

```sh
python3 build/messages.py --check     # validate the registry and confirm the generated files are current
python3 build/messages.py             # write messages/index.json and message-bank.html
python3 build/messages.py --verbose   # also list words that need reading in context
.venv/bin/python build/build.py --only ads social   # render the ads and taglines from the registry
```

The check fails on:

- duplicate ids, an id that differs from its file name, missing required fields, unknown fields, and values outside the enums
- a held entry without a gate, and a retired entry with neither `replaced_by` nor `notes`
- em dashes, en dashes, or exclamation points in any text field, and on the generated page
- words from the "Avoid these" lists in `skills/oxagen-branding/references/words.md` in live copy (workforce and a plain description of autonomous agents are allowed; words the list qualifies, such as never about outcomes, are warnings to read in context)
- phrases listed in any rule entry's `phrases` in live copy, and prospect or deal markers anywhere
- retired text inside an approved entry
- an ad file in `ads/` that no approved, launch-released ad entry produces, or an approved ad whose files are missing
- `message-bank.html` or `index.json` out of date with the registry

A past `review_by` date is a warning. Rule entries, `before` text, and the page's quoted examples are exempt from the word and phrase checks, because they name what not to write.
