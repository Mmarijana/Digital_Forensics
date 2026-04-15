from collections import defaultdict
from datetime import datetime


class TimelineEngine:
    """
    Timeline engine je čist 'backend' sloj:
    - gradi listu događaja (events)
    - filtrira po risk nivou
    - pretražuje po tekstu
    - grupiše po danu
    """

    @staticmethod
    def build_events(logins, messages_summary, risk_engine, ml_detector):
        events = []

        suspicious = risk_engine.analyze_logins_ai(logins)
        suspicious_keys = set((s.get("date", ""), s.get("ip", ""), s.get("location", "")) for s in suspicious)

        scored, total_score, account_level = risk_engine.calculate_risk_score(logins)

        ml_results = ml_detector.detect(logins) if ml_detector is not None else []
        ml_keys = set((r["date"], r["ip"], r["location"]) for r in ml_results if r.get("ml_pred") == -1)

        for s in scored:
            date_str = s.get("date", "")
            try:
                dt = datetime.strptime(date_str, "%Y-%m-%d")
            except Exception:
                dt = datetime.min

            key = (s.get("date", ""), s.get("ip", ""), s.get("location", ""))
            is_suspicious = key in suspicious_keys
            is_ml_anomaly = key in ml_keys

            flag_parts = ["⚠️" if is_suspicious else "✅"]
            if is_ml_anomaly:
                flag_parts.append("🧠")
            flag = "".join(flag_parts)

            text = (
                f"{flag} {s['date']}  LOGIN  {s['location']}  IP:{s['ip']}  "
                f"RISK:{s['level']}({s['score']})"
            )

            events.append({
                "dt": dt,
                "day": dt.date() if dt != datetime.min else None,
                "level": s["level"],
                "text": text
            })

        # summary event
        m = messages_summary or {}
        summary_text = (
            f"ℹ️ SUMMARY  Conversations:{m.get('total_conversations', 0)}  "
            f"Messages:{m.get('total_messages', 0)}  "
            f"AccountRisk:{account_level} (TotalScore:{total_score})"
        )
        events.append({
            "dt": datetime.max,
            "day": None,
            "level": "INFO",
            "text": summary_text
        })

        events.sort(key=lambda e: e["dt"])
        return events

    @staticmethod
    def filter_events(events, risk_filter="ALL", query=""):
        rf = (risk_filter or "ALL").strip().upper()
        if rf in ("HIGH", "MEDIUM", "LOW"):
            events = [e for e in events if e.get("level") == rf or e.get("level") == "INFO"]

        q = (query or "").strip().lower()
        if q:
            events = [e for e in events if q in (e.get("text", "").lower())]

        return events

    @staticmethod
    def group_by_day(events):
        grouped = defaultdict(list)
        for e in events:
            k = e["day"] if e["day"] is not None else "OTHER"
            grouped[k].append(e)

        keys = sorted([k for k in grouped.keys() if k != "OTHER"])
        if "OTHER" in grouped:
            keys.append("OTHER")

        return keys, grouped
