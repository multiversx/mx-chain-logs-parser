from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors


def build_miniblock_table_pdf(rows, out_path):
    doc = SimpleDocTemplate(out_path, pagesize=A4)

    header = [
        "miniblock hash",
        "sh0 proposed", "sh0 committed", "sh0 notarize prop", "sh0 notarize comm",
        "sh1 proposed", "sh1 committed", "sh1 notarize prop", "sh1 notarize comm",
        "sh2 proposed", "sh2 committed", "sh2 notarize prop", "sh2 notarize comm",
    ]

    data = [header] + rows

    table = Table(data, repeatRows=1)

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.black),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
    ]))

    doc.build([table])


# example usage:
# each row must be a list of exactly 13 values, same order as the header
rows = [
    [
        "abc123",
        101, 102, 103, 104,
        201, 202, 203, 204,
        301, 302, 303, 304,
    ]
]

build_miniblock_table_pdf(rows, "miniblocks.pdf")
# mb_data = MiniblockData(list(data['miniblocks'].items())).get_data_for_detailed_report1()
