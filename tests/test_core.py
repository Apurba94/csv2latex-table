import os
import tempfile
import unittest

from csv2latex_table.cli import main
from csv2latex_table.core import format_number, latex_escape, read_csv, read_markdown, to_latex

CSV = "Model,Accuracy,Loss,Params\nBaseline,0.812,0.53,1200000\nOurs_v2,0.874,0.41,950000\n"


class HelperTests(unittest.TestCase):
    def test_escape(self):
        self.assertEqual(latex_escape("50% & a_b #1"), r"50\% \& a\_b \#1")
        self.assertEqual(latex_escape("$\\alpha$"), "$\\alpha$")

    def test_format_number(self):
        self.assertEqual(format_number("0.87361", 2), "0.87")
        self.assertEqual(format_number("1234567", thousands=True), "1{,}234{,}567")
        self.assertEqual(format_number("-3.14159", 1), "$-$3.1")
        self.assertEqual(format_number("1,200"), "1200")

    def test_read_csv_sniffs_delimiter(self):
        self.assertEqual(read_csv("a;b\n1;2\n"), [["a", "b"], ["1", "2"]])

    def test_read_markdown_alignment(self):
        rows, align = read_markdown("| A | B | C |\n|:---|:---:|---:|\n| x | y | 1 |\n")
        self.assertEqual(rows, [["A", "B", "C"], ["x", "y", "1"]])
        self.assertEqual(align, ["l", "c", "r"])


class TableTests(unittest.TestCase):
    def test_booktabs_output(self):
        tex = to_latex(read_csv(CSV), caption="Results", label="tab:res", decimals=2, bold_max=(1,), bold_min=(2,))
        self.assertIn("\\begin{tabular}{lrrr}", tex)
        self.assertIn("\\toprule", tex)
        self.assertIn("\\textbf{Model} & \\textbf{Accuracy}", tex)
        self.assertIn("Ours\\_v2 & \\textbf{0.87} & \\textbf{0.41} & 950000.00 \\\\", tex)
        self.assertIn("\\label{tab:res}", tex)

    def test_ragged_rows_padded(self):
        tex = to_latex([["a", "b"], ["1"]])
        self.assertIn("1 &  \\\\", tex)

    def test_empty_raises(self):
        with self.assertRaises(ValueError):
            to_latex([])

    def test_cli(self):
        with tempfile.TemporaryDirectory() as d:
            src, out = os.path.join(d, "r.csv"), os.path.join(d, "r.tex")
            with open(src, "w", encoding="utf-8") as fh:
                fh.write(CSV)
            main([src, "-o", out, "--thousands", "--notes", "Best in bold.", "--size", "small"])
            with open(out, encoding="utf-8") as fh:
                tex = fh.read()
            self.assertIn("1{,}200{,}000", tex)
            self.assertIn("\\small", tex)
            self.assertIn("Best in bold.", tex)


if __name__ == "__main__":
    unittest.main()
