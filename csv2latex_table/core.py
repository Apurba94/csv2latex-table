"""Table readers and a booktabs LaTeX writer."""
import csv
import io
import re

_SPECIAL = {"&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}",
            "~": r"\textasciitilde{}", "^": r"\textasciicircum{}", "\\": r"\textbackslash{}"}
_NUM = re.compile(r"^[-+−]?(\d+(?:,\d{3})*|\d*)(\.\d+)?(?:[eE][-+]?\d+)?$")


def latex_escape(s):
    if s.startswith("$") and s.endswith("$") and len(s) > 1:
        return s  # already math
    return "".join(_SPECIAL.get(c, c) for c in s)


def is_number(s):
    s = s.strip()
    return bool(s) and bool(_NUM.match(s)) and any(c.isdigit() for c in s)


def format_number(s, decimals=None, thousands=False):
    """Round a numeric string; optional thousands separator ({,} for LaTeX)."""
    t = s.strip().replace(",", "").replace("−", "-")
    try:
        v = float(t)
    except ValueError:
        return s
    if decimals is None:
        out = s.strip().replace(",", "")
    else:
        out = "%.*f" % (decimals, v)
    if thousands:
        intpart, _, frac = out.partition(".")
        sign = "-" if intpart.startswith("-") else ""
        intpart = intpart.lstrip("-")
        intpart = re.sub(r"(\d)(?=(\d{3})+$)", r"\1{,}", intpart)
        out = sign + intpart + ("." + frac if frac else "")
    return out.replace("-", "$-$", 1) if out.startswith("-") else out


def read_csv(text, delimiter=None):
    if delimiter is None:
        try:
            delimiter = csv.Sniffer().sniff(text[:2048], delimiters=",;\t|").delimiter
        except csv.Error:
            delimiter = ","
    rows = [r for r in csv.reader(io.StringIO(text), delimiter=delimiter)]
    return [[c.strip() for c in r] for r in rows if any(c.strip() for c in r)]


def read_markdown(text):
    """Parse a GitHub-style Markdown table; returns rows and per-column alignment from the separator row."""
    rows, align = [], None
    for line in text.strip().splitlines():
        line = line.strip()
        if not line.startswith("|") and "|" not in line:
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if all(re.fullmatch(r":?-{3,}:?", c) for c in cells if c):
            align = ["c" if c.startswith(":") and c.endswith(":") else "r" if c.endswith(":") else "l" for c in cells]
            continue
        rows.append(cells)
    return rows, align


def to_latex(rows, caption=None, label=None, align=None, decimals=None, thousands=False, bold_max=(),
             bold_min=(), notes=None, position="htbp", header_rows=1, size=None):
    """Render rows (first `header_rows` rows are headers) as a booktabs table.

    Numeric columns are right-aligned by default. bold_max/bold_min: column indices where the
    best (max/min) value is bolded, as is common in results tables.
    """
    if not rows:
        raise ValueError("empty table")
    ncol = max(len(r) for r in rows)
    rows = [r + [""] * (ncol - len(r)) for r in rows]
    head, body = rows[:header_rows], rows[header_rows:]
    if align is None:
        align = []
        for j in range(ncol):
            vals = [r[j] for r in body if r[j]]
            align.append("r" if vals and all(is_number(v) for v in vals) else "l")
    highlight = {}
    for cols, pick in ((bold_max, max), (bold_min, min)):
        for j in cols:
            nums = [(float(r[j].replace(",", "")), i) for i, r in enumerate(body) if is_number(r[j])]
            if nums:
                best = pick(v for v, _ in nums)
                for v, i in nums:
                    if v == best:
                        highlight[(i, j)] = True
    lines = ["\\begin{table}[%s]" % position, "  \\centering"]
    if size:
        lines.append("  \\%s" % size)
    if caption:
        lines.append("  \\caption{%s}" % latex_escape(caption))
    if label:
        lines.append("  \\label{%s}" % label)
    lines += ["  \\begin{tabular}{%s}" % "".join(align), "    \\toprule"]
    for h in head:
        lines.append("    " + " & ".join("\\textbf{%s}" % latex_escape(c) if c else "" for c in h) + " \\\\")
    lines.append("    \\midrule")
    for i, r in enumerate(body):
        cells = []
        for j, c in enumerate(r):
            v = format_number(c, decimals, thousands) if is_number(c) else latex_escape(c)
            cells.append("\\textbf{%s}" % v if highlight.get((i, j)) else v)
        lines.append("    " + " & ".join(cells) + " \\\\")
    lines += ["    \\bottomrule", "  \\end{tabular}"]
    if notes:
        lines.append("  \\par\\smallskip{\\footnotesize\\textit{Note.} %s\\par}" % latex_escape(notes))
    lines.append("\\end{table}")
    return "\n".join(lines) + "\n"
