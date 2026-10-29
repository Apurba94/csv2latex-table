"""Convert CSV and Markdown tables into publication-ready LaTeX booktabs tables."""
from .core import read_csv, read_markdown, to_latex, latex_escape, format_number

__version__ = "0.1.0"
__all__ = ["read_csv", "read_markdown", "to_latex", "latex_escape", "format_number"]
