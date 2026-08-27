# CS Worksheets

Printable computer science worksheets for Robotics & Coding, stored as JSON and
published with GitHub Pages.

**105 worksheets across 7 sets.** Each worksheet is one self-contained page: a
reading passage followed by five multiple-choice questions answerable from that
passage alone. Built for students who need off-Chromebook work.

## What's in it

| Page | What it does |
|---|---|
| `index.html` | Browse every set, search by topic, see answer keys at a glance |
| `worksheet.html` | Printable view — one worksheet per page, with Name / Date / Grade |
| `answers.html` | Full answer key plus the grade checker |
| `select.html` | Bulk Print — check off any worksheets across any sets, search by title, set, or passage content, and print the whole batch as one job |

### Sets

| Set | Worksheets | Notes |
|---|---|---|
| Computer Science Basics — Set 1 | 15 | Algorithms, binary, variables, loops, hardware, CS history |
| Computer Science Basics — Set 2 | 15 | Operating systems, memory, languages, search engines, cloud |
| Cybersecurity | 15 | Phishing, malware, firewalls, 2FA, ransomware, data breaches |
| Roblox Online Safety | 15 | Written at a grade 6 reading level |
| White Hat Hacking & Penetration Testing | 15 | Ethical hacking, pen test phases, careers |
| Data Structures & Variables | 15 | Types, strings, lists, dictionaries, tuples |
| Loops | 15 | Tiered: Q1–3 recall, Q4–5 applied reasoning |

## Publishing it

1. Create a repo on GitHub and push these files to the `main` branch.
2. Go to **Settings → Pages**.
3. Under **Source**, choose **Deploy from a branch**, pick `main` and `/ (root)`.
4. Save. The site appears at `https://<username>.github.io/<repo>/` in a minute or two.

That's the whole setup — no build step, no dependencies. The site is plain HTML,
CSS, and JavaScript that reads the JSON files directly.

### Running it locally

Opening `index.html` by double-clicking **will not work**, because browsers block
JavaScript from reading local JSON files over `file://`. Start a small server instead:

```bash
cd <repo folder>
python3 -m http.server
```

Then open <http://localhost:8000>.

## Printing

Open any worksheet and click **Print** (or Ctrl/Cmd-P).

- Set paper to **Letter**, orientation **Portrait**.
- Turn **off** "Headers and footers" so the browser doesn't add URLs and page numbers.
- Margins can stay at Default; the page sets its own.

Each worksheet is guaranteed to fit on one page. Worksheets with longer passages or
longer answer choices are automatically typeset slightly smaller so they still fit —
this happens on load, so nothing needs adjusting by hand.

To print a whole set at once, use **Print whole set** on the browse page (or on any
set's card in Bulk Print). Every worksheet starts on a fresh page.

### Printing a custom selection

Open the **Bulk Print** tab to build a print job out of any mix of worksheets from
any sets — not just a whole set at once:

1. Use the search box to filter by topic, set name, or the actual text of the
   reading passage and questions.
2. Check off the worksheets you want. Each set also has a **Select all in set**
   checkbox, and the toolbar has a **Select all visible** button for grabbing
   everything that's currently matched by a search.
3. Click **Print Selected** at the bottom. It opens the same printable view as a
   single worksheet or a whole set, but with just your chosen worksheets, one per
   page, in the order you selected them.

The selection lives only in the browser's session storage — it isn't saved
anywhere and clears itself once the tab closes.

## Grading

On the **Answer Keys & Grading** page, pick a worksheet and type the five letters the
student circled, in order:

```
BDACD
```

It marks each question right or wrong as you type, shows the score out of 5 and a
percentage, and lists the correct answer for anything missed. Use a dash (`-`) for a
question the student skipped, e.g. `BD-CD`.

Answers print in a fixed order every time, so one key always works for every copy of
a given worksheet.

## Adding a new worksheet

1. Copy `data/_template.json` into the right set folder and name it to match the
   pattern, e.g. `data/loops/loops-16.json`. The template explains every field.
2. Write the passage and five questions. Set `order` on each question to control which
   choice prints as A, B, C, and D, and vary where the correct answer lands.
3. Rebuild the index and check your work:

```bash
python3 tools/rebuild_index.py
python3 tools/validate.py
```

4. Commit and push. GitHub Pages redeploys automatically.

### Adding a whole new set

Create a folder under `data/` (for example `data/networking/`), add your worksheet
files, then add a matching entry to `data/sets.json` with the set's title,
description, and reading level. Run `rebuild_index.py` and `validate.py` as above.

## Tools

| Command | What it does |
|---|---|
| `python3 tools/validate.py` | Checks every worksheet for structural problems and confirms the manifest matches the files. Exits non-zero on failure. |
| `python3 tools/rebuild_index.py` | Regenerates `data/index.json` from the files on disk. Run after adding or removing worksheets. |

`validate.py` catches the mistakes that actually bite: a missing distractor, an
`order` array that doesn't contain exactly one correct answer, a `correctLetter` that
disagrees with `order`, duplicate answer choices, a manifest key that has drifted out
of sync, and worksheets on disk that the manifest doesn't list.

## How the data is laid out

```
data/
  index.json              generated manifest — every set and worksheet
  sets.json               set titles and descriptions (hand-edited)
  _template.json          copy this to make a new worksheet
  loops/
    loops-01.json
    ...
```

A worksheet file looks like this:

```json
{
  "id": "loops-01",
  "set": "loops",
  "number": 1,
  "title": "Worksheet 1: What Is a Loop?",
  "topic": "What Is a Loop?",
  "paragraph": "A loop is a programming structure that...",
  "questions": [
    {
      "text": "A loop is best described as:",
      "correct": "A programming structure that repeats a block of code multiple times",
      "distractors": ["...", "...", "..."],
      "order": ["c", "d0", "d1", "d2"],
      "correctLetter": "A"
    }
  ]
}
```

Each question stores its correct answer once and its three distractors separately.
The `order` array fixes the printed sequence: `c` is the correct answer and `d0`,
`d1`, `d2` are the distractors by index. So `["d1", "c", "d2", "d0"]` prints the
second distractor as A, the correct answer as B, and makes the key for that question
**B**. Storing the order in the file is what keeps every printed copy identical and
lets one answer key cover the whole class.
