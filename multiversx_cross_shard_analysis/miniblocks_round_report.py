import argparse
import json
import os
import sys
from typing import Any

from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (Flowable, Paragraph, SimpleDocTemplate, Spacer,
                                Table, TableStyle)

from multiversx_cross_shard_analysis.constants import COLORS_MAPPING
from multiversx_cross_shard_analysis.miniblock_data import MiniblockData

# ----------------------------------------
# legend
# ----------------------------------------


def legend_box(color: colors.Color) -> Drawing:
    d = Drawing(8, 8)
    d.add(Rect(0, 0, 8, 8, fillColor=color, strokeColor=colors.black))  # type: ignore
    return d


def build_legend():
    # turn dict into list of (label, color)
    items = list(COLORS_MAPPING.items())

    # 3 columns grid
    cols = 3
    rows = []
    row = []

    for i, (label, color) in enumerate(items):
        row.append([legend_box(color), label])
        if len(row) == cols:
            rows.append(row)
            row = []

    # leftover
    if row:
        rows.append(row)

    # flatten structure for Table
    flat_rows = []
    for r in rows:
        flat = []
        for (box, label) in r:
            flat.append(box)
            flat.append(label)
        flat_rows.append(flat)

    # widths: box col, text col, box col, text col, etc.
    col_widths = []
    for _ in range(cols):
        col_widths.extend([10, 140])

    tbl = Table(flat_rows, colWidths=col_widths)
    tbl.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 1),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ]))

    return tbl


# ----------------------------------------
# miniblock graphics (stack of boxes)
# ----------------------------------------


def miniblock_box(text: str, stage_color: colors.Color) -> Drawing:
    d = Drawing(120, 18)
    d.add(Rect(0, 0, 120, 18, fillColor=stage_color, strokeColor=colors.black))  # type: ignore
    d.add(String(3, 5, text, fontSize=6, fillColor=colors.black))
    return d


def stacked_miniblocks(miniblocks: list[tuple[str, colors.Color]], shard: int | None = None) -> Drawing:
    height = 20 * (len(miniblocks) + 1 if shard is not None else len(miniblocks))
    d = Drawing(120, height)
    y = height - 20

    # header rectangle (same size, no fill)
    if shard is not None:
        d.add(Rect(0, y, 120, 18, fillColor=None, strokeColor=colors.black))  # type: ignore
        d.add(String(3, y + 5, f"Shard {shard}", fontSize=6, fontName="Helvetica-Bold"))
        y -= 20

    # miniblocks
    for (h, color) in miniblocks:
        d.add(Rect(0, y, 120, 18, fillColor=color, strokeColor=colors.black))  # type: ignore
        d.add(String(3, y + 5, h[:36] + "...", fontSize=6))
        y -= 20

    return d

# ----------------------------------------
# horizontal layout helper
# ----------------------------------------


class HFlowable(Flowable):
    def __init__(self, flowables: list[Flowable], space=6):
        super().__init__()
        self.flowables = flowables
        self.space = space

    def wrap(self, aW: float, aH: float) -> tuple[float, float]:
        w, h = 0, 0
        for fl in self.flowables:
            fw, fh = fl.wrap(aW, aH)
            w += fw + self.space
            h = max(h, fh)
        self.width, self.height = w, h
        return w, h

    def draw(self):
        x = 0
        for fl in self.flowables:
            fl.wrapOn(self.canv, 0, 0)
            fl.drawOn(self.canv, x, 0)
            x += fl.width + self.space


# ----------------------------------------
# build report for one epoch
# ----------------------------------------

def build_report(epoch: int, rounds_data: dict[int, Any], shards: list[int], outname: str):

    doc = SimpleDocTemplate(
        outname,
        pagesize=A4,
        leftMargin=20, rightMargin=20, topMargin=20, bottomMargin=20
    )

    story = []
    styles = getSampleStyleSheet()

    # title
    story.append(Paragraph(f"<b>Miniblock Shards Report — Epoch {epoch}</b>", styles["Title"]))
    story.append(Spacer(1, 8))
    story.append(build_legend())
    story.append(Spacer(1, 12))

    for rnd, shard_map in rounds_data.items():
        # round header
        story.append(Paragraph(f"<b>Round {rnd}</b>", styles["Heading3"]))
        story.append(Spacer(1, 6))

        # for each row: we need max miniblocks across shards
        max_rows = max(len(shard_map.get(s, [])) for s in shards)

        for i in range(max_rows):
            row_flowables = []

            for shard in shards:
                mbs = shard_map.get(shard, [])
                if i < len(mbs):
                    row_flowables.append(stacked_miniblocks([mbs[i]], shard if i == 0 else None))
                else:
                    # empty placeholder to keep columns aligned
                    row_flowables.append(Spacer(120, 20))

            # add horizontal row
            story.append(HFlowable(row_flowables, space=12))

        story.append(Spacer(1, 20))

    doc.build(story)


# ----------------------------------------
# main
# ----------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Miniblock shards timeline report")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--path", type=str, help="Path to run folder")
    group.add_argument("--run-name", type=str, help="Name of the folder under ./Reports/")

    args = parser.parse_args()

    # resolve base path
    if args.path:
        base_path = args.path
    else:
        base_path = os.path.join("Reports", args.run_name)

    if not os.path.isdir(base_path):
        print(f"Error: folder not found: {base_path}")
        sys.exit(1)

    miniblocks_path = os.path.join(base_path, "Miniblocks", "miniblocks_report.json")
    if not os.path.isfile(miniblocks_path):
        print("Error: missing required file:")
        print("  -", miniblocks_path)
        sys.exit(1)

    # load JSON
    with open(miniblocks_path, "r") as f:
        data = json.load(f)

    mb_data = MiniblockData(data["miniblocks"]).get_data_for_round_report()

    # output folder
    out_folder = os.path.join(base_path, "MiniblocksShardTimeline")
    os.makedirs(out_folder, exist_ok=True)

    # generate PDFs per epoch
    for epoch in sorted(mb_data.keys()):
        print(f"Epoch: {epoch}")
        report_dict = mb_data[epoch]
        outfile = os.path.join(out_folder, f"shards_timeline_report_{epoch}.pdf")
        build_report(int(epoch), report_dict, shards=[0, 1, 2, 4294967295], outname=outfile)
        print("→", outfile)


if __name__ == "__main__":
    main()
