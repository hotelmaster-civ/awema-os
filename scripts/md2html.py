#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Convertisseur Markdown -> HTML autonome (sans dépendance externe).

Gère : titres, gras, italique, code inline, blocs de code, listes, tableaux,
citations, séparateurs. Applique la charte graphique AWEMA (Bleu Nuit / Bleu Ciel /
Gold, Montserrat + Poppins) pour un rendu PDF professionnel.

Usage : python3 md2html.py entree.md sortie.html ["Titre du document"]
"""
import html
import re
import sys

CSS = """
@page { size: A4; margin: 2cm; }
* { box-sizing: border-box; }
body { font-family: 'Poppins','Segoe UI',sans-serif; color:#2B2F38; line-height:1.55;
       font-size:11pt; max-width:900px; margin:0 auto; padding:24px; }
h1,h2,h3,h4 { font-family:'Montserrat','Poppins',sans-serif; color:#0A1F44; line-height:1.25; }
h1 { font-size:24pt; border-bottom:4px solid #D4AF37; padding-bottom:8px; }
h2 { font-size:17pt; color:#0A1F44; border-left:6px solid #4BA3FF; padding-left:10px; margin-top:28px; }
h3 { font-size:13pt; color:#4BA3FF; }
a { color:#4BA3FF; text-decoration:none; }
strong { color:#0A1F44; }
code { background:#F0F4FA; color:#0A1F44; padding:1px 5px; border-radius:4px;
       font-family:'Consolas',monospace; font-size:9.5pt; }
pre { background:#0A1F44; color:#F7F9FC; padding:14px 16px; border-radius:8px;
      overflow-x:auto; font-size:9pt; line-height:1.4; }
pre code { background:transparent; color:#F7F9FC; padding:0; }
table { border-collapse:collapse; width:100%; margin:14px 0; font-size:10pt; }
th { background:#0A1F44; color:#fff; font-family:'Montserrat',sans-serif; text-align:left; padding:8px 10px; }
td { border:1px solid #D8E0EC; padding:7px 10px; }
tr:nth-child(even) td { background:#F7F9FC; }
blockquote { border-left:5px solid #D4AF37; background:#FBF7EC; margin:14px 0;
             padding:10px 16px; color:#5a5320; }
hr { border:none; border-top:2px dashed #D8E0EC; margin:26px 0; }
ul,ol { margin:8px 0 8px 22px; }
li { margin:3px 0; }
.brand { color:#D4AF37; font-weight:600; }
"""


def inline(text):
    text = html.escape(text)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<em>\1</em>', text)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    return text


def convert(md):
    lines = md.split("\n")
    out, i = [], 0
    in_code = False
    list_stack = []  # 'ul' / 'ol'

    def close_lists():
        while list_stack:
            out.append(f"</{list_stack.pop()}>")

    while i < len(lines):
        line = lines[i]

        # blocs de code
        if line.strip().startswith("```"):
            if not in_code:
                close_lists()
                out.append("<pre><code>")
                in_code = True
            else:
                out.append("</code></pre>")
                in_code = False
            i += 1
            continue
        if in_code:
            out.append(html.escape(line))
            i += 1
            continue

        # tableaux
        if "|" in line and i + 1 < len(lines) and re.match(r'^\s*\|?[\s:|-]+\|?\s*$', lines[i + 1]) and "|" in lines[i + 1]:
            close_lists()
            headers = [c.strip() for c in line.strip().strip("|").split("|")]
            out.append("<table><thead><tr>" + "".join(f"<th>{inline(h)}</th>" for h in headers) + "</tr></thead><tbody>")
            i += 2
            while i < len(lines) and "|" in lines[i] and lines[i].strip():
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                out.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in cells) + "</tr>")
                i += 1
            out.append("</tbody></table>")
            continue

        # titres
        m = re.match(r'^(#{1,6})\s+(.*)$', line)
        if m:
            close_lists()
            lvl = len(m.group(1))
            out.append(f"<h{lvl}>{inline(m.group(2))}</h{lvl}>")
            i += 1
            continue

        # séparateur
        if re.match(r'^\s*---\s*$', line):
            close_lists()
            out.append("<hr>")
            i += 1
            continue

        # citation
        if line.strip().startswith(">"):
            close_lists()
            out.append(f"<blockquote>{inline(line.strip()[1:].strip())}</blockquote>")
            i += 1
            continue

        # listes
        mul = re.match(r'^(\s*)[-*+]\s+(.*)$', line)
        mol = re.match(r'^(\s*)\d+\.\s+(.*)$', line)
        if mul or mol:
            tag = "ul" if mul else "ol"
            content = (mul or mol).group(2)
            if not list_stack or list_stack[-1] != tag:
                if list_stack:
                    out.append(f"</{list_stack.pop()}>")
                out.append(f"<{tag}>")
                list_stack.append(tag)
            out.append(f"<li>{inline(content)}</li>")
            i += 1
            continue

        # ligne vide / paragraphe
        if line.strip() == "":
            close_lists()
        else:
            close_lists()
            out.append(f"<p>{inline(line)}</p>")
        i += 1

    close_lists()
    if in_code:
        out.append("</code></pre>")
    return "\n".join(out)


def main():
    src, dst = sys.argv[1], sys.argv[2]
    title = sys.argv[3] if len(sys.argv) > 3 else "AWEMA — Document"
    with open(src, encoding="utf-8") as f:
        md = f.read()
    # retirer un éventuel front-matter YAML (--- ... ---) en tête
    md = re.sub(r'^---\n.*?\n---\n', '', md, count=1, flags=re.DOTALL)
    body = convert(md)
    doc = (f"<!DOCTYPE html><html lang='fr'><head><meta charset='utf-8'>"
           f"<title>{html.escape(title)}</title><style>{CSS}</style></head>"
           f"<body>{body}</body></html>")
    with open(dst, "w", encoding="utf-8") as f:
        f.write(doc)
    print(f"HTML écrit : {dst}")


if __name__ == "__main__":
    main()
