import os

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


class ReportGenerator:
    """
    Generiše PDF izveštaj nezavisno od GUI-ja.

    Ulazi:
      - profile: dict
      - logins: list[dict]
      - messages: dict
      - total_score: int
      - account_level: str ("LOW"/"MEDIUM"/"HIGH")
      - timeline_lines: list[str]
      - chart_paths: list[str] (opciono) - putanje do PNG grafikona
    """

    @staticmethod
    def is_available() -> bool:
        return REPORTLAB_AVAILABLE

    @staticmethod
    def _risk_color(level: str):
        level = (level or "").upper()
        if level == "LOW":
            return colors.HexColor("#22c55e")   # green
        if level == "MEDIUM":
            return colors.HexColor("#f59e0b")   # yellow
        if level == "HIGH":
            return colors.HexColor("#ef4444")   # red
        return colors.white

    @staticmethod
    def generate_pdf(
            path: str,
            profile: dict,
            logins: list,
            messages: dict,
            total_score: int,
            account_level: str,
            timeline_lines: list,
            chart_paths: list | None = None,
            title: str = "FB - Forensics Viewer Report",
            message_summary: dict | None = None,
            login_summary: dict | None = None,
            image_summary: dict | None = None,
    ):
        if not REPORTLAB_AVAILABLE:
            raise RuntimeError("reportlab is not installed. Do: pip install reportlab")

        from datetime import datetime

        c = canvas.Canvas(path, pagesize=A4)
        width, height = A4

        x0 = 2 * cm
        y = height - 2 * cm
        max_width = width - 4 * cm

        def reset_page():
            nonlocal y
            y = height - 2 * cm

        def ensure_page_space(min_y=2 * cm):
            nonlocal y
            if y < min_y:
                c.showPage()
                reset_page()

        def wrap_text(text, font_name="Helvetica", font_size=10, max_w=max_width):
            text = str(text or "")
            words = text.split()
            if not words:
                return [""]

            c.setFont(font_name, font_size)
            lines = []
            current = words[0]

            for word in words[1:]:
                test = current + " " + word
                if c.stringWidth(test, font_name, font_size) <= max_w:
                    current = test
                else:
                    lines.append(current)
                    current = word
            lines.append(current)
            return lines

        def write_line(text, dy=14, font="Helvetica", size=10, color=None):
            nonlocal y
            ensure_page_space()
            c.setFont(font, size)
            c.setFillColor(color if color is not None else colors.black)
            c.drawString(x0, y, str(text))
            y -= dy

        def write_paragraph(text, font="Helvetica", size=10, color=None, dy=12):
            lines = wrap_text(text, font, size)
            for line in lines:
                write_line(line, dy=dy, font=font, size=size, color=color)

        def write_section(title_text):
            write_line(" ", dy=8)
            write_line(title_text, dy=16, font="Helvetica-Bold", size=12)

        p = profile or {}
        m = messages or {}
        fx = message_summary or {}
        ls = login_summary or {}
        img = image_summary or {}
        chart_paths = chart_paths or []
        valid_charts = [cp for cp in chart_paths if cp and os.path.exists(cp)]

        # Header
        write_line(title, dy=18, font="Helvetica-Bold", size=15)
        write_line(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", dy=14, size=10)
        write_line(f"Archive status: {'Loaded' if profile else 'Not loaded'}", dy=14, size=10)

        # 1) Account Overview
        write_section("1) Account Overview")
        write_line(f"Name: {p.get('name', 'N/A')}")
        write_line(f"Email: {p.get('email', 'N/A')}")
        write_line(f"Account created: {p.get('account_created', 'N/A')}")
        write_line(f"Total logins: {len(logins or [])}")
        write_line(f"Total conversations: {m.get('total_conversations', 0)}")
        write_line(f"Total messages: {m.get('total_messages', 0)}")
        write_line(f"Analyzed images: {img.get('total_images', 0)}")

        # 2) Executive Summary
        write_section("2) Executive Summary")
        write_line(f"Account risk score: {total_score}")
        write_line(
            f"Account risk level: {account_level}",
            color=ReportGenerator._risk_color(account_level)
        )
        write_line(f"Unique locations: {ls.get('unique_locations', 0)}")
        write_line(f"Unique IP addresses: {ls.get('unique_ips', 0)}")
        write_line(f"Flagged images: {img.get('flagged_images', 0)}")

        if total_score >= 200:
            write_paragraph(
                "The analyzed account shows a high overall risk score. "
                "This may indicate unusual access patterns, multiple new locations or suspicious behavioral indicators."
            )
        elif total_score >= 120:
            write_paragraph(
                "The analyzed account shows a medium overall risk score. "
                "This suggests partially unusual activity that may require additional review."
            )
        else:
            write_paragraph(
                "The analyzed account currently shows a low overall risk score based on processed activity."
            )

        # 3) Suspicious Login Highlights
        write_section("3) Suspicious Login Highlights")
        suspicious = ls.get("top_suspicious", [])
        if not suspicious:
            write_line("No suspicious login events выделено.")
        else:
            for item in suspicious[:10]:
                date = item.get("date", "N/A")
                loc = item.get("location", "N/A")
                ip = item.get("ip", "N/A")
                score = item.get("score", 0)
                level = item.get("level", "LOW")
                reasons = ", ".join(item.get("reasons", []))
                write_line(
                    f"- [{level}] {date} | {loc} | IP: {ip} | Score: {score}",
                    dy=12,
                    size=9,
                    color=ReportGenerator._risk_color(level)
                )
                if reasons:
                    write_paragraph(f"  Reasons: {reasons}", size=9, dy=11)

        # 4) Timeline Summary
        write_section("4) Timeline Summary")
        lines = timeline_lines or []
        if not lines:
            write_line("No timeline data available.")
        else:
            for ln in lines[:40]:
                write_paragraph(ln, size=9, dy=11)
            if len(lines) > 40:
                write_line("... (timeline abbreviated)", dy=11, size=9)

        # 5) Message Forensics
        write_section("5) Message Forensics")
        write_line(f"Threads: {fx.get('threads', 0)}")
        write_line(f"Total parsed messages: {fx.get('total_messages', 0)}")
        write_line(f"Night messages: {fx.get('night_messages', 0)}")

        msg_risk = fx.get("message_risk", {})
        if msg_risk:
            write_line(f"Message risk score: {msg_risk.get('score', 0)}")
            write_line(
                f"Message risk level: {msg_risk.get('level', 'LOW')}",
                color=ReportGenerator._risk_color(msg_risk.get("level", "LOW"))
            )

            reasons = msg_risk.get("reasons", [])
            if reasons:
                write_line("Reasons:", dy=12, font="Helvetica-Bold", size=10)
                for reason in reasons[:6]:
                    write_paragraph(f"- {reason}", size=9, dy=11)

        top_contacts = fx.get("top_contacts", [])
        if top_contacts:
            write_line("Top contacts:", dy=12, font="Helvetica-Bold", size=10)
            for name, cnt in top_contacts[:8]:
                write_line(f"- {name} ({cnt} messages)", dy=11, size=9)

        # 6) AI Message Analysis
        ai = fx.get("ai_analysis", {})
        if ai:
            write_section("6) AI Message Analysis")
            write_line("Summary:", dy=12, font="Helvetica-Bold", size=10)
            write_paragraph(ai.get("summary", "No AI summary available."), size=9, dy=11)

            write_line(f"AI risk score: {ai.get('score', 0)}", dy=12, size=10)
            write_line(
                f"AI risk level: {ai.get('risk', 'LOW')}",
                color=ReportGenerator._risk_color(ai.get("risk", "LOW"))
            )

            categories = ai.get("categories", [])
            if categories:
                write_line("Detected categories:", dy=12, font="Helvetica-Bold", size=10)
                for cat in categories[:8]:
                    write_line(f"- {cat}", dy=11, size=9)

            flagged = ai.get("flagged_messages", [])
            if flagged:
                write_line("Flagged messages:", dy=12, font="Helvetica-Bold", size=10)
                for item in flagged[:5]:
                    sender = item.get("sender", "Unknown")
                    text = item.get("text", "")
                    cats = ", ".join(item.get("categories", []))
                    short = text[:140] + "..." if len(text) > 140 else text

                    write_line(f"Sender: {sender}", dy=11, size=9)
                    write_paragraph(f"Categories: {cats}", size=9, dy=11)
                    write_paragraph(f"Text: {short}", size=9, dy=11)
                    write_line(" ", dy=4)

        # 7) Image Forensics
        write_section("7) Image Forensics")
        write_line(f"Total analyzed images: {img.get('total_images', 0)}")
        write_line(f"Flagged images: {img.get('flagged_images', 0)}")

        top_results = img.get("top_results", [])
        if not top_results:
            write_line("No image analysis results available.")
        else:
            for item in top_results[:8]:
                file_name = item.get("file_name", "N/A")
                prediction = item.get("prediction", "N/A")
                confidence = item.get("confidence", 0)
                source = item.get("source", "N/A")

                write_line(
                    f"- {file_name} | {source} | {prediction} | Confidence: {confidence}%",
                    dy=11,
                    size=9
                )

        # 8) Charts
        if valid_charts:
            c.showPage()
            reset_page()
            write_line("8) Charts", dy=18, font="Helvetica-Bold", size=12)

            for chart_path in valid_charts:
                ensure_page_space(min_y=10 * cm)
                c.drawImage(
                    chart_path,
                    x0,
                    y - 230,
                    width=16 * cm,
                    height=8 * cm,
                    preserveAspectRatio=True,
                    anchor="sw"
                )
                y -= 260

        c.save()