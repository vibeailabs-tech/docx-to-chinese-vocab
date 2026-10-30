---
name: docx-to-chinese-vocab
description: Pipeline agent - take a Word .docx, extract its underlined words/phrases, then turn exactly those words into a Chinese vocabulary .tsv (Vocabulary, Pronunciation, English, Vietnamese, Example, Sentence Pinyin, Sentence Translation). Use whenever the user gives a .docx and wants a vocabulary table / TSV / Anki file from the underlined words ("lọc từ gạch chân rồi làm bảng từ vựng", "docx sang tsv", "chạy agent").
---

# DOCX underlined words -> Chinese vocabulary TSV

Run the two steps in order. Step 2 must use the output of step 1 as its only input.
`<skill-dir>` is the directory containing this SKILL.md. Quote every path (file names may contain spaces).

## Step 1 - Extract underlined words

```bash
python3 "<skill-dir>/scripts/docx_underlined_words.py" "/path/to/file.docx"
```

`scripts/docx_underlined_words.py` (Python 3 standard library only) writes `<name>_gach_chan.txt` next to the .docx - one word/phrase per line, duplicates removed (first occurrence kept), adjacent underlined runs merged into one phrase - and prints the list.

- `.doc` file: convert first (macOS `textutil -convert docx FILE.doc`, or `soffice --headless --convert-to docx FILE.doc`), then rerun.
- Empty list: stop and tell the user. Never invent words.

## Step 2 - Build the vocabulary TSV

1. Read `references/chinese-vocab-tsv.md` and follow all of its rules (7 columns, header row, column rules, `YYYY_MM_DD_STT.tsv` naming, never overwrite, validation).
2. Input = the lines of `<name>_gach_chan.txt` from step 1, in the same order. Include exactly those items - one row per line, no additions, no removals. Keep multi-character phrases as one row.
3. Output directory = `output/` next to the input .docx (create it if missing), unless the user names another directory or file. Pick the next `STT` for today's date among the existing `.tsv` files there.
4. Validate: row count = lines in `<name>_gach_chan.txt` + 1 header, and every row has exactly 7 tab-separated fields:

```bash
awk -F'\t' 'NF!=7{bad++} END{print NR" rows, "(bad+0)" bad"}' "/path/to/output/<file>.tsv"
```

Fix and rewrite the file if validation fails.

## Report

Reply briefly with: number of underlined items, path of the `_gach_chan.txt` file, path of the `.tsv` file, and the validation result.
