from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)


def build_analytics_pdf(output_path: str, summary: dict, patterns: list, heatmap: list):
    """
    Builds a PDF report combining summary stats, pattern analysis,
    and a category x week heatmap table.

    summary  -> dict from GET /reports/summary
    patterns -> list from GET /reports (the "patterns" key)
    heatmap  -> list from GET /reports/heatmap (the "heatmap" key)
    """
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    title_style = styles["Title"]
    heading_style = styles["Heading2"]
    normal_style = styles["Normal"]

    # ── Title ────────────────────────────────────────────
    story.append(Paragraph("Bustler Pulse — Analytics Report", title_style))
    story.append(Paragraph(
        f"Generated: {datetime.utcnow().strftime('%B %d, %Y at %H:%M UTC')}",
        normal_style
    ))
    story.append(Spacer(1, 20))

    # ── Summary Section ──────────────────────────────────
    story.append(Paragraph("Summary", heading_style))
    story.append(Spacer(1, 8))

    summary_rows = [["Metric", "Value"]]
    label_map = {
        "total_tickets"   : "Total Tickets",
        "open_tickets"    : "Open Tickets",
        "resolved_tickets": "Resolved Tickets",
        "critical_tickets": "Critical Tickets",
        "anger_flagged"   : "Anger Flagged",
        "resolved_today"  : "Resolved Today",
        "total_reports"   : "Total Reports",
        "avg_csat"        : "Average CSAT"
    }
    for key, label in label_map.items():
        value = summary.get(key)
        if value is None:
            value = "—"
        summary_rows.append([label, str(value)])

    summary_table = Table(summary_rows, colWidths=[220, 220])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8232A")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F5F5")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 24))

    # ── Pattern Analysis Section ─────────────────────────
    story.append(Paragraph("Pattern Analysis by Category", heading_style))
    story.append(Spacer(1, 8))

    if patterns:
        pattern_rows = [["Category", "Total Issues", "Avg CSAT", "Priority"]]
        for p in patterns:
            priority_text = (p.get("priority") or "—")
            # Strip emoji for PDF compatibility (built-in fonts lack emoji glyphs)
            priority_text = (
                priority_text.replace("🔴", "[HIGH]")
                             .replace("🟡", "[MED]")
                             .replace("🟢", "[LOW]")
            )
            pattern_rows.append([
                p.get("category", "—"),
                str(p.get("total_issues", "—")),
                str(p.get("avg_csat", "—")),
                priority_text
            ])

        # Wrap priority text in Paragraph so it wraps within the cell
        # instead of clipping at the column edge
        wrapped_pattern_rows = [pattern_rows[0]]
        cell_style = ParagraphStyle("cell", parent=normal_style, fontSize=9)
        for row in pattern_rows[1:]:
            wrapped_pattern_rows.append([
                row[0], row[1], row[2], Paragraph(row[3], cell_style)
            ])

        pattern_table = Table(wrapped_pattern_rows, colWidths=[90, 80, 70, 200])
        pattern_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#00A99D")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F5F5")]),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(pattern_table)
    else:
        story.append(Paragraph("No pattern data available yet.", normal_style))

    story.append(Spacer(1, 24))

    # ── Heatmap Section (pivoted: category rows x week columns) ──
    story.append(Paragraph("Issue Heatmap (Category vs Week)", heading_style))
    story.append(Spacer(1, 8))

    if heatmap:
        categories = sorted(set(row["category"] for row in heatmap))
        weeks = sorted(set(row["week"] for row in heatmap))

        # Build lookup: (category, week) -> count
        lookup = {}
        for row in heatmap:
            lookup[(row["category"], row["week"])] = row["count"]

        header_row = ["Category"] + [f"Wk {w}" for w in weeks]
        heatmap_rows = [header_row]
        for cat in categories:
            row = [cat]
            for w in weeks:
                count = lookup.get((cat, w), 0)
                row.append(str(count) if count else "—")
            heatmap_rows.append(row)

        col_width = 60
        heatmap_table = Table(
            heatmap_rows,
            colWidths=[100] + [col_width] * len(weeks)
        )
        heatmap_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#333333")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F5F5")]),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (1, 0), (-1, -1), "CENTER"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        heatmap_table.repeatRows = 1
        story.append(heatmap_table)
    else:
        story.append(Paragraph("No heatmap data available yet.", normal_style))

    story.append(Spacer(1, 20))
    story.append(Paragraph(
        "— Bustler Pulse Automated Reporting System",
        ParagraphStyle("footer", parent=normal_style, fontSize=8, textColor=colors.grey)
    ))

    doc.build(story)
    return output_path