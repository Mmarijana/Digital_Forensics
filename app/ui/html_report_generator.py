import os
from datetime import datetime
from html import escape


class HTMLReportGenerator:
    @staticmethod
    def generate_report(
        output_path: str,
        profile: dict,
        logins: list,
        messages: dict,
        message_summary: dict,
        total_score: int,
        account_level: str,
        timeline_lines: list,
        chart_paths: list | None = None,
        title: str = "Facebook Forensics Report",
        source_file: str = "N/A"
    ):
        chart_paths = chart_paths or []
        valid_chart_paths = [p for p in chart_paths if p and os.path.exists(p)]

        name = escape(str(profile.get("name", "N/A")))
        email = escape(str(profile.get("email", "N/A")))
        created = escape(str(profile.get("account_created", "N/A")))

        total_logins = len(logins or [])
        total_conversations = messages.get("total_conversations", 0)
        total_messages = messages.get("total_messages", 0)

        unique_locations = len({x.get("location", "N/A") for x in (logins or [])})
        suspicious_count = sum(
            1 for x in message_summary.get("flags", [])
        ) + sum(
            1 for x in message_summary.get("suspicious_links", [])
        )

        top_contacts = message_summary.get("top_contacts", [])[:5]
        suspicious_links = message_summary.get("suspicious_links", [])[:5]
        burst_events = message_summary.get("burst_events", [])[:5]
        ai = message_summary.get("ai_analysis", {})
        msg_risk = message_summary.get("message_risk", {})

        # recent messages from AI flagged
        flagged_messages = ai.get("flagged_messages", [])[:5]

        # risky activities list
        risky_activities = []

        for login in (logins or [])[:10]:
            risky_activities.append({
                "date": login.get("date", "N/A"),
                "activity": f"Login from {login.get('location', 'N/A')} | IP: {login.get('ip', 'N/A')}",
                "level": account_level
            })

        for reason in msg_risk.get("reasons", [])[:5]:
            risky_activities.append({
                "date": "Message analysis",
                "activity": reason,
                "level": msg_risk.get("level", "LOW")
            })

        risky_activities = risky_activities[:8]

        evidence_items = [
            "Profile information extracted",
            "Login history analyzed",
            "Message threads parsed",
            "Timeline generated",
            "Charts generated",
            "AI-assisted message analysis completed"
        ]

        ai_summary = escape(ai.get("summary", "No AI summary available."))

        categories_html = "".join(
            f"<li>{escape(str(cat))}</li>" for cat in ai.get("categories", [])[:8]
        ) or "<li>No suspicious semantic categories detected.</li>"

        top_contacts_html = "".join(
            f"""
            <div class="contact-item">
                <div class="avatar">{escape(str(name[:1] if name else '?'))}</div>
                <div>
                    <div class="contact-name">{escape(str(name))}</div>
                    <div class="contact-meta">{count} messages</div>
                </div>
            </div>
            """
            for name, count in top_contacts
        ) or "<div class='muted'>No contacts found.</div>"

        risky_html = "".join(
            f"""
            <tr>
                <td>{escape(str(item["date"]))}</td>
                <td>{escape(str(item["activity"]))}</td>
                <td><span class="badge {str(item["level"]).lower()}">{escape(str(item["level"]))}</span></td>
            </tr>
            """
            for item in risky_activities
        ) or """
            <tr><td colspan="3">No risky activities found.</td></tr>
        """

        flagged_html = "".join(
            f"""
            <tr>
                <td>{escape(str(item.get("sender", "Unknown")))}</td>
                <td>{escape(", ".join(item.get("categories", [])))}</td>
                <td>{escape((item.get("text", "")[:90] + "...") if len(item.get("text", "")) > 90 else item.get("text", ""))}</td>
            </tr>
            """
            for item in flagged_messages
        ) or """
            <tr><td colspan="3">No AI-flagged messages.</td></tr>
        """

        links_html = "".join(
            f"<li>{escape(str(item.get('url')))} — {escape(str(item.get('sender')))}</li>"
            for item in suspicious_links
        ) or "<li>No suspicious links detected.</li>"

        bursts_html = "".join(
            f"<li>{escape(str(item.get('count')))} messages between {escape(str(item.get('start')))} and {escape(str(item.get('end')))}</li>"
            for item in burst_events
        ) or "<li>No burst activity detected.</li>"

        evidence_html = "".join(f"<li>{escape(item)}</li>" for item in evidence_items)

        timeline_preview = "".join(
            f"<li>{escape(str(line))}</li>"
            for line in (timeline_lines or [])[:8]
        ) or "<li>No timeline lines available.</li>"

        chart_html = ""
        for p in valid_chart_paths:
            rel = os.path.basename(p)
            chart_html += f'<img class="chart-img" src="{escape(rel)}" alt="Chart">'

        if not chart_html:
            chart_html = "<div class='muted'>No charts available.</div>"

        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{escape(title)}</title>
<style>
    body {{
        margin: 0;
        font-family: Arial, sans-serif;
        background: #eef2f7;
        color: #1f2937;
    }}
    .page {{
        max-width: 1200px;
        margin: 0 auto;
        background: white;
        min-height: 100vh;
    }}
    .header {{
        background: linear-gradient(135deg, #0f3d7a, #1557b0);
        color: white;
        padding: 24px 32px 18px 32px;
    }}
    .header h1 {{
        margin: 0;
        font-size: 32px;
    }}
    .header .sub {{
        margin-top: 10px;
        font-size: 13px;
        opacity: 0.95;
    }}
    .meta-bar {{
        background: #dbe3ee;
        color: #334155;
        padding: 10px 32px;
        font-size: 13px;
        border-bottom: 1px solid #cbd5e1;
    }}
    .section-title {{
        text-align: center;
        font-weight: bold;
        color: #475569;
        padding: 18px 0 10px 0;
        font-size: 20px;
    }}
    .cards {{
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 14px;
        padding: 0 24px 20px 24px;
    }}
    .card {{
        color: white;
        border-radius: 8px;
        padding: 16px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.12);
    }}
    .blue {{ background: #2563eb; }}
    .green {{ background: #65a30d; }}
    .orange {{ background: #ea580c; }}
    .red {{ background: #dc2626; }}
    .slate {{ background: #475569; }}
    .card .num {{
        font-size: 28px;
        font-weight: bold;
    }}
    .card .label {{
        font-size: 13px;
        margin-top: 6px;
    }}
    .grid {{
        display: grid;
        grid-template-columns: 2fr 1fr;
        gap: 18px;
        padding: 0 24px 24px 24px;
    }}
    .panel {{
        border: 1px solid #dbe2ea;
        background: #f8fafc;
    }}
    .panel h3 {{
        margin: 0;
        padding: 12px 14px;
        font-size: 16px;
        color: #334155;
        background: #e9eef5;
        border-bottom: 1px solid #dbe2ea;
    }}
    .panel-body {{
        padding: 14px;
    }}
    table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
        background: white;
    }}
    th, td {{
        border: 1px solid #dbe2ea;
        padding: 8px;
        vertical-align: top;
    }}
    th {{
        background: #edf2f7;
        text-align: left;
        color: #334155;
    }}
    .badge {{
        display: inline-block;
        padding: 4px 10px;
        border-radius: 6px;
        color: white;
        font-size: 12px;
        font-weight: bold;
    }}
    .badge.low {{ background: #16a34a; }}
    .badge.medium {{ background: #f59e0b; }}
    .badge.high {{ background: #dc2626; }}
    .list {{
        margin: 0;
        padding-left: 18px;
    }}
    .contact-item {{
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 10px 0;
        border-bottom: 1px solid #e5e7eb;
    }}
    .avatar {{
        width: 38px;
        height: 38px;
        border-radius: 50%;
        background: #2563eb;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
    }}
    .contact-name {{
        font-weight: bold;
        color: #1e293b;
    }}
    .contact-meta {{
        font-size: 12px;
        color: #64748b;
    }}
    .muted {{
        color: #64748b;
        font-size: 13px;
    }}
    .note {{
        margin: 0 24px 24px 24px;
        background: #fef3c7;
        color: #7c5e10;
        border: 1px solid #f5d97b;
        padding: 12px 14px;
        font-size: 13px;
    }}
    .footer {{
        text-align: center;
        color: #64748b;
        font-size: 12px;
        padding: 18px 10px 28px 10px;
    }}
    .chart-img {{
        width: 100%;
        margin-bottom: 12px;
        border: 1px solid #dbe2ea;
        background: white;
    }}
    .two-col {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 16px;
    }}
</style>
</head>
<body>
<div class="page">
    <div class="header">
        <h1>{escape(title)}</h1>
        <div class="sub">
            Case: Facebook Account Analysis |
            Examiner: FB - Forensics Viewer |
            Report Generated: {escape(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))}
        </div>
    </div>

    <div class="meta-bar">
        Source file: {escape(source_file)} |
        Account: {name} |
        Email: {email} |
        Account created: {created}
    </div>

    <div class="section-title">Summary of Findings</div>

    <div class="cards">
        <div class="card blue">
            <div class="num">{total_messages}</div>
            <div class="label">Messages Parsed</div>
        </div>
        <div class="card green">
            <div class="num">{len(top_contacts)}</div>
            <div class="label">Key Contacts</div>
        </div>
        <div class="card orange">
            <div class="num">{unique_locations}</div>
            <div class="label">Unique Locations</div>
        </div>
        <div class="card red">
            <div class="num">{suspicious_count}</div>
            <div class="label">Suspicious Indicators</div>
        </div>
        <div class="card slate">
            <div class="num">{escape(account_level)}</div>
            <div class="label">Account Risk Level</div>
        </div>
    </div>

    <div class="grid">
        <div>
            <div class="panel">
                <h3>Flagged Messages</h3>
                <div class="panel-body">
                    <table>
                        <thead>
                            <tr>
                                <th>Sender</th>
                                <th>AI Categories</th>
                                <th>Message Snippet</th>
                            </tr>
                        </thead>
                        <tbody>
                            {flagged_html}
                        </tbody>
                    </table>
                </div>
            </div>

            <div class="panel" style="margin-top:16px;">
                <h3>Risky Activities</h3>
                <div class="panel-body">
                    <table>
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>Activity</th>
                                <th>Risk Level</th>
                            </tr>
                        </thead>
                        <tbody>
                            {risky_html}
                        </tbody>
                    </table>
                </div>
            </div>

            <div class="panel" style="margin-top:16px;">
                <h3>Evidence Collected</h3>
                <div class="panel-body">
                    <ul class="list">
                        {evidence_html}
                    </ul>
                </div>
            </div>

            <div class="panel" style="margin-top:16px;">
                <h3>AI Summary</h3>
                <div class="panel-body">
                    <p>{ai_summary}</p>
                    <strong>Detected categories:</strong>
                    <ul class="list">
                        {categories_html}
                    </ul>
                </div>
            </div>
        </div>

        <div>
            <div class="panel">
                <h3>Charts</h3>
                <div class="panel-body">
                    {chart_html}
                </div>
            </div>

            <div class="panel" style="margin-top:16px;">
                <h3>Timeline Preview</h3>
                <div class="panel-body">
                    <ul class="list">
                        {timeline_preview}
                    </ul>
                </div>
            </div>

            <div class="panel" style="margin-top:16px;">
                <h3>Key Contacts</h3>
                <div class="panel-body">
                    {top_contacts_html}
                </div>
            </div>

            <div class="panel" style="margin-top:16px;">
                <h3>Suspicious Links / Bursts</h3>
                <div class="panel-body">
                    <div class="two-col">
                        <div>
                            <strong>Links</strong>
                            <ul class="list">
                                {links_html}
                            </ul>
                        </div>
                        <div>
                            <strong>Burst Events</strong>
                            <ul class="list">
                                {bursts_html}
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="note">
        <strong>Note:</strong>
        Account risk level is <strong>{escape(account_level)}</strong>,
        message risk level is <strong>{escape(str(msg_risk.get("level", "LOW")))}</strong>.
        Additional analyst review is recommended for medium and high risk indicators.
    </div>

    <div class="footer">
        Generated by FB - Forensics Viewer
    </div>
</div>
</body>
</html>
"""

        report_dir = os.path.dirname(output_path)
        if report_dir:
            os.makedirs(report_dir, exist_ok=True)

        for p in valid_chart_paths:
            dst = os.path.join(report_dir, os.path.basename(p))
            if os.path.abspath(p) != os.path.abspath(dst):
                with open(p, "rb") as src_f, open(dst, "wb") as dst_f:
                    dst_f.write(src_f.read())

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)