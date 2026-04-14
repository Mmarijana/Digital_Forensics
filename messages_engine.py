import os
import json
import re
from collections import Counter, defaultdict
from datetime import datetime
from ml_engine import AIMessageAnalyzer


class MessageForensicsEngine:
    SUSPICIOUS_KEYWORDS = [
        "password", "passcode", "verification", "verify", "code",
        "login", "bank", "urgent", "immediately", "send money",
        "account blocked", "security alert", "otp", "confirm",
        "link", "click here"
    ]

    SHORTENER_DOMAINS = [
        "bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "is.gd", "buff.ly"
    ]

    URL_REGEX = re.compile(r"(https?://[^\s]+|www\.[^\s]+)", re.IGNORECASE)

    @staticmethod
    def analyze_from_archive(extract_path):
        inbox_path = os.path.join(extract_path, "messages", "inbox")

        if not os.path.exists(inbox_path):
            return {
                "mode": "messages folder not found",
                "threads": 0,
                "total_messages": 0,
                "top_contacts": [],
                "night_messages": 0,
                "duplicates_top": [],
                "keyword_hits": [],
                "suspicious_links": [],
                "burst_events": [],
                "message_risk": {"score": 0, "level": "LOW", "reasons": []},
                "flags": [],
                "notes": ["messages/inbox folder not found in archive"]
            }

        total_messages = 0
        thread_count = 0
        participant_counter = Counter()
        hour_counter = Counter()
        content_counter = Counter()
        keyword_counter = Counter()
        suspicious_links = []
        flags = []
        notes = []
        all_messages = []
        ai_messages = []
        # za burst detection po thread-u
        burst_events = []


        for root, _, files in os.walk(inbox_path):
            for file_name in files:
                if not file_name.endswith(".json"):
                    continue

                full_path = os.path.join(root, file_name)

                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                except Exception as e:
                    notes.append(f"Could not read {full_path}: {e}")
                    continue

                messages = data.get("messages", [])
                participants = data.get("participants", [])

                if messages:
                    thread_count += 1

                # top contacts
                for p in participants:
                    if p and p != "Unknown User":
                        participant_counter[p] += 1

                # sortiraj po vremenu za burst detection
                normalized_messages = []

                for msg in messages:
                    total_messages += 1

                    sender = msg.get("sender_name", "Unknown")
                    content = (msg.get("content") or "").strip()
                    ts_ms = msg.get("timestamp_ms")

                    # preskoči prazne poruke
                    if not content and not ts_ms:
                        continue

                    dt = None
                    if ts_ms:
                        try:
                            dt = datetime.fromtimestamp(ts_ms / 1000)
                            hour_counter[dt.hour] += 1
                        except Exception:
                            dt = None

                    if content:
                        # duplicate detection
                        normalized = " ".join(content.lower().split())
                        if normalized:
                            content_counter[normalized] += 1

                        # keyword hits
                        lowered = content.lower()
                        for kw in MessageForensicsEngine.SUSPICIOUS_KEYWORDS:
                            if kw in lowered:
                                keyword_counter[kw] += 1

                        # suspicious links
                        urls = MessageForensicsEngine.URL_REGEX.findall(content)
                        for url in urls:
                            lowered_url = url.lower()
                            is_short = any(domain in lowered_url for domain in MessageForensicsEngine.SHORTENER_DOMAINS)
                            suspicious_links.append({
                                "url": url,
                                "sender": sender,
                                "timestamp": dt.strftime("%Y-%m-%d %H:%M:%S") if dt else "N/A",
                                "is_shortener": is_short
                            })

                            if is_short:
                                flags.append(f"Shortened URL detected: {url}")

                    thread_contacts = [p for p in participants if p and p != "Unknown User"]
                    primary_contact = thread_contacts[0] if thread_contacts else sender

                    all_messages.append({
                        "sender": sender,
                        "contact": primary_contact,
                        "content": content,
                        "datetime": dt,
                        "timestamp_ms": ts_ms
                    })

                    ai_messages.append({
                        "sender": sender,
                        "content": content,
                        "datetime": dt
                    })

                    normalized_messages.append({
                        "sender": sender,
                        "content": content,
                        "dt": dt
                    })

                # burst detection: 10+ poruka u 2 minuta u okviru istog threada
                normalized_messages = [m for m in normalized_messages if m["dt"] is not None]
                normalized_messages.sort(key=lambda x: x["dt"])

                if len(normalized_messages) >= 10:
                    start = 0
                    for end in range(len(normalized_messages)):
                        while normalized_messages[end]["dt"] - normalized_messages[start]["dt"] > \
                                __import__("datetime").timedelta(minutes=2):
                            start += 1

                        window_size = end - start + 1
                        if window_size >= 10:
                            burst_events.append({
                                "start": normalized_messages[start]["dt"].strftime("%Y-%m-%d %H:%M:%S"),
                                "end": normalized_messages[end]["dt"].strftime("%Y-%m-%d %H:%M:%S"),
                                "count": window_size
                            })

        # noćna aktivnost
        night_messages = sum(hour_counter[h] for h in range(0, 6))

        # top contacts
        top_contacts = participant_counter.most_common(10)

        # duplicates
        duplicates_top = [
            (text, cnt) for text, cnt in content_counter.most_common(10)
            if cnt >= 3 and len(text) > 3
        ]

        # keywords
        keyword_hits = keyword_counter.most_common()

        # suspicious links top
        suspicious_links_top = suspicious_links[:20]

        # risk scoring
        score = 0
        reasons = []

        if night_messages >= 20:
            score += 20
            reasons.append(f"High night activity ({night_messages} messages between 00-05h)")

        if len(duplicates_top) >= 3:
            score += 20
            reasons.append("Multiple duplicated/repeated messages detected")

        if sum(keyword_counter.values()) >= 5:
            score += 25
            reasons.append("Suspicious keyword frequency is elevated")

        shortener_count = sum(1 for x in suspicious_links if x["is_shortener"])
        if shortener_count >= 2:
            score += 20
            reasons.append("Multiple shortened URLs detected")

        if burst_events:
            score += 20
            reasons.append("Burst messaging activity detected")

        if total_messages > 0 and night_messages / total_messages > 0.25:
            score += 10
            reasons.append("Night activity ratio is unusually high")

        if score >= 60:
            level = "HIGH"
        elif score >= 30:
            level = "MEDIUM"
        else:
            level = "LOW"

        # dodatni flagovi
        for text, cnt in duplicates_top[:5]:
            short = text[:100] + "..." if len(text) > 100 else text
            flags.append(f"Repeated message [{cnt}x]: {short}")

        for kw, cnt in keyword_hits[:10]:
            if cnt >= 2:
                flags.append(f"Keyword '{kw}' detected {cnt} times")

        ai_analysis = AIMessageAnalyzer.analyze_conversation(ai_messages)

        return {
            "mode": "parsed json threads",
            "threads": thread_count,
            "total_messages": total_messages,
            "top_contacts": top_contacts,
            "night_messages": night_messages,
            "duplicates_top": duplicates_top,
            "keyword_hits": keyword_hits,
            "suspicious_links": suspicious_links_top,
            "burst_events": burst_events[:10],
            "hour_activity": dict(hour_counter),
            "all_messages": all_messages,
            "ai_analysis": ai_analysis,
            "message_risk": {
                "score": score,
                "level": level,
                "reasons": reasons
            },
            "flags": flags[:20],
            "notes": notes
        }