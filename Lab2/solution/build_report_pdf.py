#!/usr/bin/env python3
"""
Render REPORT.md into a professionally formatted academic PDF (REPORT.pdf)
using ReportLab Platypus. Parses the subset of Markdown used by the report:
headings (#/##/###), paragraphs, **bold**/`code` inline, fenced code blocks,
pipe tables, bullet/numbered lists, and horizontal rules.
"""
from __future__ import annotations

import html
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable, ListFlowable, ListItem, Paragraph, PageBreak,
    SimpleDocTemplate, Spacer, Table, TableStyle,
)

HERE = Path(__file__).resolve().parent
SRC = HERE / "REPORT.md"
OUT = HERE / "REPORT.pdf"

NAVY = colors.HexColor("#1a2a4a")
ACCENT = colors.HexColor("#2d5a9e")
LIGHT = colors.HexColor("#eef2f8")
GREY = colors.HexColor("#555555")


def make_styles():
    ss = getSampleStyleSheet()
    styles = {
        "title": ParagraphStyle("title", parent=ss["Title"], fontName="Helvetica-Bold",
                                 fontSize=20, textColor=NAVY, leading=24, spaceAfter=4),
        "subtitle": ParagraphStyle("subtitle", parent=ss["Normal"], fontSize=12.5,
                                    textColor=ACCENT, alignment=TA_CENTER, leading=16,
                                    spaceAfter=10),
        "meta": ParagraphStyle("meta", parent=ss["Normal"], fontSize=9.5, textColor=GREY,
                               alignment=TA_CENTER, leading=14),
        "h1": ParagraphStyle("h1", parent=ss["Heading1"], fontName="Helvetica-Bold",
                             fontSize=14.5, textColor=NAVY, spaceBefore=14, spaceAfter=6,
                             leading=18),
        "h2": ParagraphStyle("h2", parent=ss["Heading2"], fontName="Helvetica-Bold",
                             fontSize=12, textColor=ACCENT, spaceBefore=10, spaceAfter=4,
                             leading=15),
        "h3": ParagraphStyle("h3", parent=ss["Heading3"], fontName="Helvetica-Bold",
                             fontSize=10.5, textColor=NAVY, spaceBefore=8, spaceAfter=3,
                             leading=13),
        "body": ParagraphStyle("body", parent=ss["Normal"], fontSize=9.7, leading=14,
                               alignment=TA_LEFT, spaceAfter=5, textColor=colors.HexColor("#1a1a1a")),
        "li": ParagraphStyle("li", parent=ss["Normal"], fontSize=9.7, leading=13.5,
                             textColor=colors.HexColor("#1a1a1a")),
        "code": ParagraphStyle("code", parent=ss["Code"], fontName="Courier", fontSize=6.6,
                               leading=8.8, textColor=colors.HexColor("#222222")),
        "th": ParagraphStyle("th", parent=ss["Normal"], fontName="Helvetica-Bold",
                             fontSize=8.8, textColor=colors.white, leading=11),
        "td": ParagraphStyle("td", parent=ss["Normal"], fontSize=8.8, leading=11,
                             textColor=colors.HexColor("#1a1a1a")),
    }
    return styles


def inline(text: str) -> str:
    """Convert inline markdown (**bold**, `code`) to ReportLab mini-HTML."""
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"`(.+?)`", r'<font face="Courier" size="8.6">\1</font>', text)
    # Normalise a few unicode marks that are fine in UTF-8 PDF text.
    return text


def split_row(line: str):
    cells = line.strip().strip("|").split("|")
    return [c.strip() for c in cells]


def build():
    lines = SRC.read_text(encoding="utf-8").splitlines()
    styles = make_styles()
    story = []

    i = 0
    n = len(lines)
    # --- Title block (first H1 + following bold meta lines) ---
    while i < n and not lines[i].startswith("# "):
        i += 1
    if i < n:
        story.append(Paragraph(inline(lines[i][2:].strip()), styles["title"]))
        i += 1
    # subtitle (## line immediately after)
    if i < n and lines[i].startswith("## "):
        story.append(Paragraph(inline(lines[i][3:].strip()), styles["subtitle"]))
        i += 1
    story.append(HRFlowable(width="100%", thickness=1.4, color=ACCENT, spaceAfter=8))

    def flush_para(buf):
        if buf:
            story.append(Paragraph(inline(" ".join(buf)), styles["body"]))
            buf.clear()

    para_buf: list[str] = []

    while i < n:
        line = lines[i]
        stripped = line.strip()

        # Fenced code block
        if stripped.startswith("```"):
            flush_para(para_buf)
            i += 1
            code_lines = []
            while i < n and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1  # skip closing fence
            code_html = "<br/>".join(
                html.escape(cl, quote=False).replace(" ", "&nbsp;") for cl in code_lines
            )
            tbl = Table([[Paragraph(code_html, styles["code"])]], colWidths=[16.9 * cm])
            tbl.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f4f5f7")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]))
            story.append(tbl)
            story.append(Spacer(1, 6))
            continue

        # Pipe table
        if stripped.startswith("|") and i + 1 < n and set(lines[i + 1].strip()) <= set("|-: "):
            flush_para(para_buf)
            header = split_row(lines[i])
            i += 2  # skip header + separator
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append(split_row(lines[i]))
                i += 1
            data = [[Paragraph(inline(c), styles["th"]) for c in header]]
            for r in rows:
                # pad/truncate to header width
                r = (r + [""] * len(header))[:len(header)]
                data.append([Paragraph(inline(c), styles["td"]) for c in r])
            ncols = len(header)
            total_w = 16.5 * cm
            col_w = [total_w / ncols] * ncols
            tbl = Table(data, colWidths=col_w, repeatRows=1)
            tbl.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#c4cede")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 3.5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
            ]))
            story.append(tbl)
            story.append(Spacer(1, 7))
            continue

        # Horizontal rule
        if stripped == "---":
            flush_para(para_buf)
            story.append(HRFlowable(width="100%", thickness=0.7, color=colors.HexColor("#cccccc"),
                                    spaceBefore=4, spaceAfter=6))
            i += 1
            continue

        # Headings
        if stripped.startswith("### "):
            flush_para(para_buf)
            story.append(Paragraph(inline(stripped[4:]), styles["h3"]))
            i += 1
            continue
        if stripped.startswith("## "):
            flush_para(para_buf)
            story.append(Paragraph(inline(stripped[3:]), styles["h2"]))
            i += 1
            continue
        if stripped.startswith("# "):
            flush_para(para_buf)
            story.append(Paragraph(inline(stripped[2:]), styles["h1"]))
            i += 1
            continue

        # List items (bullet or numbered) — collect a contiguous block
        if re.match(r"^(\-|\d+\.)\s+", stripped):
            flush_para(para_buf)
            items = []
            bullet_type = "bullet" if stripped.startswith("-") else "1"
            while i < n and re.match(r"^(\-|\d+\.)\s+", lines[i].strip()):
                content = re.sub(r"^(\-|\d+\.)\s+", "", lines[i].strip())
                items.append(ListItem(Paragraph(inline(content), styles["li"]),
                                      value=None))
                i += 1
            story.append(ListFlowable(items, bulletType=bullet_type,
                                      leftIndent=14, bulletColor=ACCENT,
                                      bulletFontSize=8))
            story.append(Spacer(1, 4))
            continue

        # Blank line -> paragraph break
        if stripped == "":
            flush_para(para_buf)
            i += 1
            continue

        # Otherwise accumulate into current paragraph
        para_buf.append(stripped)
        i += 1

    flush_para(para_buf)

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(GREY)
        canvas.drawString(2 * cm, 1.1 * cm,
                          "CSE 532 — Lab 2 — Ahmed Hossam Abdelrahman")
        canvas.drawRightString(A4[0] - 2 * cm, 1.1 * cm, f"Page {doc.page}")
        canvas.setStrokeColor(colors.HexColor("#dddddd"))
        canvas.line(2 * cm, 1.4 * cm, A4[0] - 2 * cm, 1.4 * cm)
        canvas.restoreState()

    doc = SimpleDocTemplate(
        str(OUT), pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=1.8 * cm, bottomMargin=1.8 * cm,
        title="CSE 532 Lab 2 Report", author="Ahmed Hossam Abdelrahman",
    )
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    build()
