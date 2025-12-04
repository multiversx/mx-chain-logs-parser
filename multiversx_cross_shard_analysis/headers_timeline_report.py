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
    Flowable
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.graphics.shapes import Drawing, Rect, String

from multiversx_cross_shard_analysis.constants import COLORS_MAPPING, Colors

from multiversx_cross_shard_analysis.header_structures import HeaderData, ShardData

# -----------------------------
# CONFIG (mirrors miniblock report)
# -----------------------------

PAGE_WIDTH, PAGE_HEIGHT = A4
LEFT_MARGIN = RIGHT_MARGIN = 20
TOP_MARGIN = BOTTOM_MARGIN = 20

RECT_H = 20
RECT_PADDING_X = 4
ROUND_HEADER_FONT = 7
RECT_LABEL_FONT = 8
RECT_INFO_FONT = 8

SECTION_BASE_HEIGHT = 110      # same idea as miniblock
EXTRA_LINE_HEIGHT = 18         # additional rows per stack
TITLE_HEIGHT = 60


# -----------------------------
# build stacked rectangles (same as miniblock version)
# -----------------------------

def build_stack_for_round(items: list[tuple[str, str, colors.Color]], col_width: float) -> Drawing:
    rows = max(1, len(items))
    total_h = rows * RECT_H
    d = Drawing(col_width, total_h)

    y = total_h - RECT_H
    for label, info, col in items:
        rect_w = max(2, col_width - RECT_PADDING_X * 2) - 4

        d.add(Rect(0, y + 2, rect_w, RECT_H - 4, fillColor=col, strokeColor=colors.black))  # type: ignore

        text_x = RECT_PADDING_X + 3
        base_y = y + 4

        d.add(String(text_x, base_y + 8, label, fontSize=RECT_LABEL_FONT))
        d.add(String(text_x, base_y, info, fontSize=RECT_INFO_FONT))

        y -= RECT_H

    if len(items) == 0:
        rect_w = max(2, col_width - RECT_PADDING_X * 2) - 4
        mid = total_h / 2
        d.add(Rect(0, mid - 6, rect_w, 12, fillColor=colors.whitesmoke, strokeColor=colors.grey))   # type: ignore
        d.add(String(RECT_PADDING_X + 2, mid - 2, "no data", fontSize=RECT_LABEL_FONT))

    return d

# -----------------------------
# check for round gaps
# -----------------------------


def has_round_gap(rounds: list[int]) -> bool:
    if len(rounds) < 2:
        return False
    rounds_sorted = sorted(rounds)
    for a, b in zip(rounds_sorted, rounds_sorted[1:]):
        if b != a + 1:
            return True
    return False


# -----------------------------
# build section for one nonce
# -----------------------------

def build_nonce_section(shard_id: int, nonce: int, rounds: list[int], data: dict[int, list[Any]],
                        usable_width: float, highlight: bool = False) -> list[Flowable]:

    flow = []
    styles = getSampleStyleSheet()

    flow.append(Paragraph(f"<b>Shard {shard_id} — Nonce {nonce}</b>", styles["Heading3"]))
    flow.append(Spacer(1, 4))

    num_cols = len(rounds)
    col_width = usable_width / max(1, num_cols)

    header = [Paragraph(f"<b>{r}</b>", styles["BodyText"]) for r in rounds]

    cells = []
    for r in rounds:
        items = data.get(r, [])
        drawing = build_stack_for_round(items, col_width)
        cells.append(drawing)

    tbl = Table(
        [header, cells],
        colWidths=[col_width] * num_cols,
        hAlign="LEFT",
    )

    tbl_style = [
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("VALIGN", (0, 1), (-1, -1), "TOP"),
        ("FONTSIZE", (0, 0), (-1, 0), ROUND_HEADER_FONT),
    ]

    # add red border if highlighted
    if highlight:
        tbl_style.append(("BOX", (0, 0), (-1, -1), 2, colors.red))

    tbl.setStyle(TableStyle(tbl_style))

    flow.append(tbl)
    flow.append(Spacer(1, 8))
    return flow


# -----------------------------
# PDF builder
# -----------------------------

def build_nonce_timeline_pdf(shards_data: dict[int, dict[int, dict[int, list[Any]]]],
                             outname="nonce_timeline.pdf"):
    doc = SimpleDocTemplate(
        outname,
        pagesize=A4,
        leftMargin=LEFT_MARGIN,
        rightMargin=RIGHT_MARGIN,
        topMargin=TOP_MARGIN,
        bottomMargin=BOTTOM_MARGIN,
    )

    usable_width = PAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN
    MAX_H = PAGE_HEIGHT - TOP_MARGIN - BOTTOM_MARGIN

    styles = getSampleStyleSheet()
    story = []
    story.append(Paragraph("<b>Nonce Timeline Report</b>", styles["Title"]))
    story.append(Spacer(1, 10))

    current_h = 0
    first_page = True

    for shard_id, shard_dict in shards_data.items():
        for nonce, rdata in sorted(shard_dict.items()):
            # height estimate based on max stack height
            max_stack = max((len(v) for v in rdata.values()), default=1)
            h_needed = SECTION_BASE_HEIGHT + max(0, max_stack - 2) * EXTRA_LINE_HEIGHT

            effective_page_height = MAX_H - (TITLE_HEIGHT if first_page else 0)

            if current_h + h_needed > effective_page_height:
                story.append(PageBreak())
                current_h = 0
                first_page = False

            round_list = list(rdata.keys())
            gap = has_round_gap(round_list)
            story.extend(build_nonce_section(shard_id, nonce, round_list, rdata, usable_width, gap))
            current_h += h_needed

    doc.build(story)


# ----------------------------- Example input data ------------------------------
input_data = {
    0: {
        1: {
            100: [('origin_final', 'Shard 0', COLORS_MAPPING[Colors.origin_final])],
            101: [('origin_notarized', 'Shard 0', COLORS_MAPPING[Colors.meta_origin_committed])],
            102: [('dest_proposed', 'Shard 1', COLORS_MAPPING[Colors.dest_proposed]), ('dest_final', 'Shard 2', COLORS_MAPPING[Colors.dest_final])],
            103: [('dest_partial', 'Shard 1', COLORS_MAPPING[Colors.dest_partial_executed]), ('dest_notarized', 'Shard 2', COLORS_MAPPING[Colors.meta_dest_committed])],
            104: [('dest_final', 'Shard 1', COLORS_MAPPING[Colors.dest_final])],
            105: [('dest_notarized', 'Shard 1', COLORS_MAPPING[Colors.meta_dest_committed])],
        },
        2: {
            101: [('origin_proposed', 'Shard 0', COLORS_MAPPING[Colors.origin_proposed])],
            103: [('origin_final', 'Shard 0', COLORS_MAPPING[Colors.origin_final])],
            104: [('dest_final', 'Shard 2', COLORS_MAPPING[Colors.dest_final]), ('origin_notarized', 'Shard 0', COLORS_MAPPING[Colors.meta_origin_committed])],
            105: [('dest_notarized', 'Shard 2', COLORS_MAPPING[Colors.meta_dest_committed])],
        }
    },
    1: {
        1: {
            101: [('N1', 'S1', COLORS_MAPPING[Colors.origin_final])],
            102: [('N1', 'S1', COLORS_MAPPING[Colors.meta_origin_committed])],
            103: [('N1', 'S0', COLORS_MAPPING[Colors.dest_proposed]), ('N1', 'S2', COLORS_MAPPING[Colors.dest_final])],
            104: [('N1', 'S0', COLORS_MAPPING[Colors.dest_partial_executed]), ('N1', 'S2', COLORS_MAPPING[Colors.meta_dest_committed])],
            105: [('N1', 'S0', COLORS_MAPPING[Colors.dest_final])],
            106: [('N1', 'S0', COLORS_MAPPING[Colors.meta_dest_committed])],
        },
        2: {
            102: [('N2', 'S1', COLORS_MAPPING[Colors.origin_partial_executed])],
            104: [('N2', 'S1', COLORS_MAPPING[Colors.origin_final])],
            105: [('N2', 'S2', COLORS_MAPPING[Colors.dest_final]), ('N2', 'S1', COLORS_MAPPING[Colors.meta_origin_committed])],
            106: [('N2', 'S2', COLORS_MAPPING[Colors.meta_dest_committed])],
        },
    },
    2: {
        1: {
            100: [('N1', 'S2', COLORS_MAPPING[Colors.origin_final])],
            101: [('N1', 'S2', COLORS_MAPPING[Colors.meta_origin_committed])],
            102: [('N1', 'S0', COLORS_MAPPING[Colors.dest_final]), ('N1', 'S1', COLORS_MAPPING[Colors.dest_final])],
            103: [('N1', 'S0', COLORS_MAPPING[Colors.meta_dest_committed]), ('N1', 'S1', COLORS_MAPPING[Colors.meta_dest_committed])],
        },
        2: {
            101: [('N2', 'S2', COLORS_MAPPING[Colors.origin_final])],
            102: [('N2', 'S2', COLORS_MAPPING[Colors.meta_origin_committed])],
            103: [('N2', 'S0', COLORS_MAPPING[Colors.dest_final])],
            104: [('N2', 'S0', COLORS_MAPPING[Colors.meta_dest_committed]), ('N2', 'S1', COLORS_MAPPING[Colors.dest_final])],
            105: [('N2', 'S1', COLORS_MAPPING[Colors.meta_dest_committed])],
        },
        3: {
            103: [('N3', 'S2', COLORS_MAPPING[Colors.origin_final])],
            104: [('N3', 'S2', COLORS_MAPPING[Colors.meta_origin_committed])],
            105: [('N3', 'S1', COLORS_MAPPING[Colors.dest_final])],
            106: [('N3', 'S1', COLORS_MAPPING[Colors.dest_final])],
            107: [('N3', 'S1', COLORS_MAPPING[Colors.meta_dest_committed])],
        },
    },
    4294967295: {
        1: {
            100: [('N1', 'M', COLORS_MAPPING[Colors.origin_final])],
            103: [('N1', 'M', COLORS_MAPPING[Colors.meta_origin_committed])],
            104: [('N1', 'S0', COLORS_MAPPING[Colors.dest_final]), ('N1', 'S1', COLORS_MAPPING[Colors.dest_final])],
            105: [('N1', 'S0', COLORS_MAPPING[Colors.meta_dest_committed]), ('N1', 'S1', COLORS_MAPPING[Colors.meta_dest_committed]), ('N1', 'S2', COLORS_MAPPING[Colors.dest_final])],
            106: [('N1', 'S2', COLORS_MAPPING[Colors.meta_dest_committed])],
        }
    }

}

# build_nonce_timeline_pdf(input_data, outname="nonce_timeline_report.pdf")
# print("Nonce timeline report generated: nonce_timeline_report.pdf")

if __name__ == "__main__":
    # run PDF build

    headers = ShardData()
    for shard in [0, 1, 2, 4294967295]:
        with open(f'./Reports/cross-shard-execution-anal-9afe696daf/Shards/{shard}_report.json', 'r') as f:
            data = json.load(f)

        headers.parsed_headers[shard] = HeaderData()
        headers.parsed_headers[shard].header_dictionary = data['shards']

    with open('./Reports/cross-shard-execution-anal-9afe696daf/Miniblocks/miniblocks_report.json', 'r') as f:
        data = json.load(f)
        headers.miniblocks = data['miniblocks']

    input_data = headers.get_data_for_header_horizontal_report()

    for epoch in sorted(input_data.keys()):
        print(f"Epoch: {epoch}")
        report_list = input_data[epoch]

        build_nonce_timeline_pdf(report_list, outname=f"nonce_timeline_report_{epoch}.pdf")
        print(f"Nonce timeline report generated: nonce_timeline_report_{epoch}.pdf")
