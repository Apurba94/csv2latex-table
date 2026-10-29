# csv2latex-table

**Turn the CSV your analysis produced (or a Markdown table) into a publication-quality
LaTeX `booktabs` table, with rounding, escaping, alignment and bold best results.**

Part of the *Research Automation Toolkit*: 100 open tools for daily research work.

## Why

Hand-copying numbers from analysis output into LaTeX tables is slow and a classic source of
transcription errors that survive into published papers. Regenerating the table from the CSV
on every run keeps manuscript and results in sync.

## Features

- Reads CSV/TSV/semicolon files (delimiter sniffed) and GitHub Markdown tables (alignment kept)
- `booktabs` rules (`\toprule`, `\midrule`, `\bottomrule`), bold headers, caption, label, notes
- Escapes LaTeX special characters (`%`, `&`, `_` ...) but keeps `$math$` cells
- Numeric columns right-aligned automatically; rounding (`-d 2`), thousands separators, proper minus signs
- Bold the best value per column (`--bold-max 1,2`, `--bold-min 3`)

## Usage

```bash
pip install .
csv2latex-table results.csv -c "Test accuracy" -l tab:acc -d 3 --bold-max 1
csv2latex-table table.md --size small -o table.tex
python analysis.py | csv2latex-table -d 2 > results_table.tex
```

Requires `\usepackage{booktabs}` in your preamble.

## Testing

```bash
python -m unittest discover -s tests -t .
```

## License

MIT (c) JANIN A APURBA
