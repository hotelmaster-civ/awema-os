#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CSV -> HTML (tableau) avec la charte AWEMA, pour export PDF paysage.

Usage : python3 csv2html.py in.csv out.html "Titre"
"""
import csv
import html
import sys

CSS = """
@page { size: A4 landscape; margin: 1cm; }
body { font-family:'Poppins','Segoe UI',sans-serif; color:#2B2F38; padding:10px; }
h1 { font-family:'Montserrat',sans-serif; color:#0A1F44; border-bottom:4px solid #D4AF37;
     padding-bottom:6px; font-size:18pt; }
table { border-collapse:collapse; width:100%; font-size:7pt; table-layout:fixed; }
th { background:#0A1F44; color:#fff; padding:4px 5px; text-align:left;
     font-family:'Montserrat',sans-serif; position:sticky; top:0; }
td { border:1px solid #D8E0EC; padding:3px 5px; word-wrap:break-word; overflow-wrap:anywhere;
     vertical-align:top; }
tr:nth-child(even) td { background:#F7F9FC; }
"""


def main():
    src, dst = sys.argv[1], sys.argv[2]
    title = sys.argv[3] if len(sys.argv) > 3 else "AWEMA"
    with open(src, encoding="utf-8") as f:
        rows = list(csv.reader(f))
    head, body = rows[0], rows[1:]
    th = "".join(f"<th>{html.escape(c)}</th>" for c in head)
    trs = []
    for r in body:
        tds = "".join(f"<td>{html.escape(c)}</td>" for c in r)
        trs.append(f"<tr>{tds}</tr>")
    doc = (f"<!DOCTYPE html><html lang='fr'><head><meta charset='utf-8'>"
           f"<title>{html.escape(title)}</title><style>{CSS}</style></head><body>"
           f"<h1>{html.escape(title)}</h1>"
           f"<table><thead><tr>{th}</tr></thead><tbody>{''.join(trs)}</tbody></table>"
           f"</body></html>")
    with open(dst, "w", encoding="utf-8") as f:
        f.write(doc)
    print(f"HTML écrit : {dst}")


if __name__ == "__main__":
    main()
