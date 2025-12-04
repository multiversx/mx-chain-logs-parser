"""
miniblock_timeline_report.py

Produces miniblock timeline report PDF:
- multiple miniblocks per page
- each miniblock: subtitle + full hash + meta info
- timeline table: columns = rounds (including gaps), each column contains stacked colored rectangles for mentions
- colors: use mention['color'] if present, otherwise derived from mention type + reserved
"""

import json
from typing import Any
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.platypus.flowables import Flowable


from multiversx_cross_shard_analysis.constants import TYPE_NAMES

from multiversx_cross_shard_analysis.miniblock_data import MiniblockData

# -----------------------------
# CONFIG
# -----------------------------

PAGE_WIDTH, PAGE_HEIGHT = A4
LEFT_MARGIN = RIGHT_MARGIN = 20
TOP_MARGIN = BOTTOM_MARGIN = 20

MINIBLOCKS_PER_PAGE = 6

ROUND_HEADER_FONT = 7
RECT_LABEL_FONT = 8
RECT_INFO_FONT = 8

# rectangle drawing dimensions
RECT_H = 20
RECT_PADDING_X = 4

# -----------------------------
# small flowable for a left-aligned rectangle inside a table cell
# -----------------------------


class RectCell(Flowable):
    '''not used currently, included for further development'''

    def __init__(self, label: str, info: str, color: colors.Color, width: float, height: float = 14, padding: float = 2):
        super().__init__()
        self.label = label
        self.info = info
        self.color = color
        self.width = width
        self.height = height
        self.padding = padding

    def wrap(self, aW: float, aH: float):
        # force rect to match column width, never bigger
        return self.width, self.height * 2

    def draw(self):
        c = self.canv

        c.setFillColor(self.color)
        c.rect(0, 0, self.width, self.height * 2, fill=1, stroke=0)

        c.setFillColor(colors.black)
        c.setFont("Helvetica", 7)

        # label line
        c.drawString(self.padding, self.height + 1, self.label)
        # info line
        c.drawString(self.padding, 2, self.info)


# -----------------------------
# build stacked drawing for one round
# -----------------------------


def build_stack_for_round(items: list[tuple[str, str, colors.Color]], col_width: float) -> Drawing:
    """
    items: list of (label, info, color)
    """

    rows = max(1, len(items))
    total_h = rows * RECT_H
    d = Drawing(col_width, total_h)
    y = total_h - RECT_H

    for label, info, col in items:
        rect_w = max(2, col_width - RECT_PADDING_X * 2) - 4
        if 'proposed' in label:
            # dashed border for proposed
            d.add(Rect(0, y + 2, rect_w, RECT_H - 4, fillColor=col, strokeColor=colors.black, strokeWidth=1, strokeDashArray=[3, 2]))  # type: ignore
        else:
            # solid border for committed
            d.add(Rect(0, y + 2, rect_w, RECT_H - 4, fillColor=col, strokeColor=colors.black))  # type: ignore

        # text: two rows inside rectangle
        text_x = RECT_PADDING_X + 3
        base_y = y + 4

        d.add(String(text_x, base_y + 8, label, fontSize=RECT_LABEL_FONT))
        d.add(String(text_x, base_y, info, fontSize=RECT_INFO_FONT))

        y -= RECT_H

    # empty case
    if len(items) == 0:
        rect_w = max(2, col_width - RECT_PADDING_X * 2) - 4
        d.add(Rect(0, total_h / 2 - 6, rect_w, 12, fillColor=colors.whitesmoke, strokeColor=colors.grey))  # type: ignore
        d.add(String(RECT_PADDING_X + 2, total_h / 2 - 2, "no action", fontSize=RECT_LABEL_FONT))

    return d


# -----------------------------
# miniblock section
# -----------------------------
def build_miniblock_section(miniblock: dict[str, Any], page_usable_width: float) -> list[Flowable]:
    flow = []
    styles = getSampleStyleSheet()

    h = miniblock.get("hash", "<no-hash>")
    sender = miniblock.get("senderShardID", "?")
    receiver = miniblock.get("receiverShardID", "?")
    txc = miniblock.get("txCount", "?")
    typ = TYPE_NAMES.get(miniblock.get("type", -1), str(miniblock.get("type", "?")))

    flow.append(Paragraph(f"<b>Miniblock {h}</b>", styles["Heading3"]))
    flow.append(Paragraph(f"- from shard {sender} -> shard {receiver}<br/>- tx_count: {txc}, type: {typ}", styles["BodyText"]))
    flow.append(Spacer(1, 4))

    mentioned = miniblock.get("mentioned", {})
    if not mentioned:
        flow.append(Paragraph("No mentions found.", styles["BodyText"]))
        flow.append(Spacer(1, 6))
        return flow

    first_r = miniblock.get("first_seen_round", 0)
    last_r = miniblock.get("last_seen_round", 0)
    rounds = list(range(first_r, last_r + 1))

    num_cols = max(1, len(rounds))
    col_width = page_usable_width / num_cols

    header = [
        Paragraph(f"<b>round {r}</b>", styles["BodyText"])
        for r in rounds
    ]

    cells = []
    for r in rounds:
        items = mentioned.get(r, [])
        drawing = build_stack_for_round(items, col_width)
        cells.append(drawing)

    tbl = Table(
        [header, cells],
        colWidths=[col_width] * num_cols,
        hAlign="LEFT",
    )

    tbl.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("FONTSIZE", (0, 0), (-1, 0), ROUND_HEADER_FONT),
                ("VALIGN", (0, 1), (-1, -1), "TOP"),
            ]
        )
    )

    flow.append(tbl)
    flow.append(Spacer(1, 8))
    return flow


# -----------------------------
# PDF builder
# -----------------------------
def build_pdf_from_miniblocks(epoch: int, miniblocks: list[dict[str, Any]], outname="miniblock_timeline_report.pdf"):
    doc = SimpleDocTemplate(
        outname,
        pagesize=A4,
        leftMargin=LEFT_MARGIN,
        rightMargin=RIGHT_MARGIN,
        topMargin=TOP_MARGIN,
        bottomMargin=BOTTOM_MARGIN,
    )

    usable_width = PAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN
    MAX_PAGE_HEIGHT = PAGE_HEIGHT - TOP_MARGIN - BOTTOM_MARGIN
    TITLE_HEIGHT = 75
    MINIBLOCK_WITH_2_ROWS = 135
    EXTRA_LINE_HEIGHT = 18

    story = []
    current_height = 0
    first_page = True
    styles = getSampleStyleSheet()
    story.append(Paragraph(f"<b>Miniblock Detail Report — Epoch {epoch}</b>", styles["Title"]))
    story.append(Spacer(1, 8))
    for i, mb in enumerate(miniblocks, 1):
        num_rects = max(len(v) for v in mb.get("mentioned", {}).values())
        EXTRA_LINES = max(0, num_rects - 2)

        miniblock_height = MINIBLOCK_WITH_2_ROWS + EXTRA_LINES * EXTRA_LINE_HEIGHT

        # if first page, reserve title height
        effective_page_height = MAX_PAGE_HEIGHT - (TITLE_HEIGHT if first_page else 0)

        if current_height + miniblock_height > effective_page_height:
            story.append(PageBreak())
            current_height = 0
            first_page = False

        story.extend(build_miniblock_section(mb, usable_width))
        current_height += miniblock_height

    doc.build(story)


if __name__ == "__main__":
    # run PDF build

    with open('./Reports/cross-shard-execution-anal-9afe696daf/Miniblocks/miniblocks_report.json', 'r') as f:
        data = json.load(f)

    mb_data = MiniblockData(data['miniblocks']).get_data_for_detail_report()

    for epoch in sorted(mb_data.keys()):
        print(f"Epoch: {epoch}")
        report_list = mb_data[epoch]
        build_pdf_from_miniblocks(int(epoch), report_list, outname=f"miniblock_timeline_report_epoch_{epoch}.pdf")
