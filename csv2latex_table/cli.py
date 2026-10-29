"""Command-line interface for csv2latex-table."""
import argparse
import sys

from .core import read_csv, read_markdown, to_latex


def _cols(s):
    return tuple(int(x) for x in s.split(",") if x.strip()) if s else ()


def main(argv=None):
    ap = argparse.ArgumentParser(prog="csv2latex-table", description="CSV/Markdown table -> LaTeX booktabs table.")
    ap.add_argument("input", nargs="?", help="CSV/TSV or .md file (stdin if omitted)")
    ap.add_argument("-c", "--caption")
    ap.add_argument("-l", "--label")
    ap.add_argument("-d", "--decimals", type=int, help="round numbers to N decimals")
    ap.add_argument("--thousands", action="store_true", help="thousands separators")
    ap.add_argument("--align", help="column spec, e.g. lrrc")
    ap.add_argument("--bold-max", help="comma-separated 0-based column indices whose max is bolded")
    ap.add_argument("--bold-min", help="comma-separated 0-based column indices whose min is bolded")
    ap.add_argument("--notes", help="table note printed under the table")
    ap.add_argument("--size", help="font size command, e.g. small, footnotesize")
    ap.add_argument("--delimiter")
    ap.add_argument("-o", "--output")
    args = ap.parse_args(argv)

    if args.input:
        with open(args.input, encoding="utf-8-sig") as fh:
            text = fh.read()
    else:
        text = sys.stdin.read()
    align = list(args.align) if args.align else None
    if (args.input or "").lower().endswith(".md") or text.lstrip().startswith("|"):
        rows, md_align = read_markdown(text)
        align = align or md_align
    else:
        rows = read_csv(text, args.delimiter)
    out = to_latex(rows, args.caption, args.label, align, args.decimals, args.thousands,
                   _cols(args.bold_max), _cols(args.bold_min), args.notes, size=args.size)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(out)
    else:
        sys.stdout.write(out)
    return 0
