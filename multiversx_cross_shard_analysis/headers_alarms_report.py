import argparse
import json
import os
import sys
from typing import Any

from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (Flowable, LongTable, PageBreak, Paragraph,
                                SimpleDocTemplate, Spacer, TableStyle)

from multiversx_cross_shard_analysis.constants import COLORS_MAPPING, Colors
from multiversx_cross_shard_analysis.header_structures import (HeaderData,
                                                               ShardData)
from multiversx_cross_shard_analysis.miniblock_data import MiniblockData

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

def build_stack_rows(items: list[tuple[str, str, colors.Color]], col_width: float) -> list[Drawing]:
    """
    Instead of one giant Drawing, we return a list of small ones.
    Each drawing represents one row in the vertical stack.
    """
    row_drawings = []

    if len(items) == 0:
        # Create a single "no data" row
        d = Drawing(col_width, RECT_H)
        rect_w = max(2, col_width - RECT_PADDING_X * 2) - 4
        d.add(Rect(0, 2, rect_w, 12, fillColor=colors.whitesmoke, strokeColor=colors.grey))  # type: ignore
        d.add(String(RECT_PADDING_X + 2, 6, "no data", fontSize=RECT_LABEL_FONT))
        row_drawings.append(d)
        return row_drawings

    for label, info, col in items:
        # Create a small drawing for just this one item
        d = Drawing(col_width, RECT_H)
        rect_w = max(2, col_width - RECT_PADDING_X * 2) - 4

        d.add(Rect(0, 2, rect_w, RECT_H - 4, fillColor=col, strokeColor=colors.black))  # type: ignore

        text_x = RECT_PADDING_X + 3
        d.add(String(text_x, 12, label, fontSize=RECT_LABEL_FONT))
        d.add(String(text_x, 4, info, fontSize=RECT_INFO_FONT))
        row_drawings.append(d)

    return row_drawings

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

    # 1. Build the Header Row
    header = [Paragraph(f"<b>{r}</b>", styles["BodyText"]) for r in rounds]

    # 2. Transpose the stacks into rows
    # We need to find the max height among all columns to normalize the row count
    column_stacks = [build_stack_rows(data.get(r, []), col_width) for r in rounds]
    max_rows = max(len(stack) for stack in column_stacks)

    table_data = [header]

    # Fill the table row by row
    for i in range(max_rows):
        row = []
        for stack in column_stacks:
            if i < len(stack):
                row.append(stack[i])
            else:
                row.append("")  # Empty cell if this column has fewer items
        table_data.append(row)

    tbl = LongTable(
        table_data,
        colWidths=[col_width] * num_cols,
        hAlign="LEFT",
        splitByRow=True,  # This allows the table to break across pages between rows
    )

    tbl_style = [
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("VALIGN", (0, 1), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 0),  # Tighten padding for large lists
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("FONTSIZE", (0, 0), (-1, 0), ROUND_HEADER_FONT),
    ]

    if highlight:
        tbl_style.append(("BOX", (0, 0), (-1, -1), 2, colors.red))

    tbl.setStyle(TableStyle(tbl_style))

    flow.append(tbl)
    flow.append(Spacer(1, 8))
    return flow


# -----------------------------
# PDF builder
# -----------------------------

def build_nonce_alarms_timeline_pdf(alarm_data: dict[str, dict[int, dict[int, dict[int, list[Any]]]]],
                                    outname="nonce_alarms.pdf"):
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
    story.append(Paragraph("<b>Nonce Alarms Report</b>", styles["Title"]))
    story.append(Spacer(1, 10))

    current_h = 0
    first_page = True
    for alarm, shards_data in alarm_data.items():
        if not shards_data:
            continue
        story.append(Paragraph(f"<b>Alarm: {alarm}</b>", styles["Heading2"]))
        story.append(Spacer(1, 6))
        current_h += 36  # approx height of heading + spacer

        for shard_id, shard_dict in shards_data.items():
            for nonce, rdata in sorted(shard_dict.items()):
                # height estimate based on max stack height
                max_stack = max((len(v) for v in rdata.values()), default=1)
                h_needed = SECTION_BASE_HEIGHT + max(0, max_stack - 2) * EXTRA_LINE_HEIGHT

                effective_page_height = MAX_H - (TITLE_HEIGHT if first_page else 0)
                # print(f"DEBUG: shard {shard_id} nonce {nonce} needs height {h_needed}, current_h={current_h}, effective_page_height={effective_page_height}")
                if current_h + h_needed > effective_page_height:
                    story.append(PageBreak())
                    current_h = 0
                    first_page = False

                round_list = list(rdata.keys())
                story.extend(build_nonce_section(shard_id, nonce, round_list, rdata, usable_width))
                current_h += h_needed
    if not story:
        return
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


def main():

    parser = argparse.ArgumentParser(description="Nonce timeline alarms report generator")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--path", type=str, help="Path to folder containing run output")
    group.add_argument("--run-name", type=str, help="Name of the run inside ./Reports/")

    args = parser.parse_args()

    # resolve final folder path
    if args.path:
        base_path = args.path
    else:
        base_path = os.path.join("Reports", args.run_name)

    # verify base folder exists
    if not os.path.isdir(base_path):
        print(f"Error: folder not found: {base_path}")
        sys.exit(1)

    # verify expected files exist
    shard_ids = [0, 1, 2, 4294967295]
    missing = []

    for shard in shard_ids:
        p = os.path.join(base_path, "Shards", f"{shard}_report.json")
        if not os.path.isfile(p):
            missing.append(p)

    miniblocks_path = os.path.join(base_path, "Miniblocks", "miniblocks_report.json")
    if not os.path.isfile(miniblocks_path):
        missing.append(miniblocks_path)

    if missing:
        print("Error: missing required files:")
        for m in missing:
            print("  -", m)
        sys.exit(1)

    # load JSONs
    headers = ShardData()

    for shard in shard_ids:
        with open(os.path.join(base_path, "Shards", f"{shard}_report.json")) as f:
            data = json.load(f)
        headers.parsed_headers[shard] = HeaderData()
        headers.parsed_headers[shard].header_dictionary = data["shards"]

    with open(miniblocks_path) as f:
        data = json.load(f)
        headers.miniblocks = data["miniblocks"]

    # process
    input_data = MiniblockData(headers.miniblocks).get_data_for_header_alarms_report()

    # output path
    out_folder = os.path.join(base_path, "NonceAlarms")
    os.makedirs(out_folder, exist_ok=True)

    for epoch in sorted(input_data.keys()):
        outfile = os.path.join(out_folder, f"nonce_alarms_report_{epoch}.pdf")
        if not input_data[epoch]:
            print(f"Epoch {epoch} has no alarms, skipping report generation.")
            continue
        build_nonce_alarms_timeline_pdf(input_data[epoch], outname=outfile)
        print(f"Nonce alarms report for Epoch {epoch} generated: {outfile}")


if __name__ == "__main__":
    main()
