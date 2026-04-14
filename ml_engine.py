import re
from collections import Counter


try:
    import numpy as np
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import OneHotEncoder
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


class MLAnomalyDetector:

    @staticmethod
    def detect(logins):

        if not SKLEARN_AVAILABLE:
            return []

        if not logins or len(logins) < 5:
            return []

        locations = [l.get("location", "N/A") for l in logins]
        ips = [l.get("ip", "N/A") for l in logins]

        X_cat = np.array(list(zip(locations, ips)), dtype=object)

        enc = OneHotEncoder(handle_unknown="ignore")
        X = enc.fit_transform(X_cat)

        model = IsolationForest(
            n_estimators=200,
            contamination=0.15,
            random_state=42
        )

        model.fit(X)

        preds = model.predict(X)
        scores = model.decision_function(X)

        results = []
        for i, login in enumerate(logins):
            results.append({
                "date": login.get("date", "N/A"),
                "location": login.get("location", "N/A"),
                "ip": login.get("ip", "N/A"),
                "ml_pred": int(preds[i]),
                "ml_score": float(scores[i])
            })

        return results

class AIMessageAnalyzer:
    CATEGORY_RULES = {
        "Urgency / Pressure": [
            "urgent", "immediately", "asap", "right now", "now", "hurry",
            "hitno", "odmah", "sto pre", "sad", "brzo"
        ],
        "Credential Request": [
            "password", "passcode", "verification code", "verification",
            "otp", "login", "sign in", "account code", "security code",
            "šifra", "kod", "lozinka", "prijava"
        ],
        "Fraud / Financial": [
            "bank", "card", "transfer", "send money", "payment", "account number",
            "iban", "invoice", "transaction", "uplati", "račun", "kartica", "novac"
        ],
        "Manipulation / Concealment": [
            "don't tell", "delete", "remove this", "keep secret", "hide this",
            "nemoj nikome", "obriši", "sakrij", "tajna", "ne govori"
        ],
        "Suspicious Link Sharing": [
            "click here", "open this link", "bit.ly", "tinyurl", "http://", "https://", "www."
        ],
        "Threat / Coercion": [
            "or else", "you must", "final warning", "last chance",
            "ili", "moraš", "poslednje upozorenje", "pretnja"
        ]
    }

    URL_REGEX = re.compile(r"(https?://[^\s]+|www\.[^\s]+)", re.IGNORECASE)

    @staticmethod
    def analyze_conversation(messages):
        """
        messages: list of dict objects, expected fields:
            {
                "sender": ...,
                "content": ...,
                "datetime": datetime_obj or None
            }
        """
        if not messages:
            return {
                "summary": "No messages available for AI analysis.",
                "categories": [],
                "risk": "LOW",
                "score": 0,
                "reasons": [],
                "flagged_messages": [],
                "stats": {}
            }

        category_hits = Counter()
        flagged_messages = []
        repeated_counter = Counter()
        total_messages = 0
        night_messages = 0
        links_found = 0
        short_messages = 0

        for msg in messages:
            content = (msg.get("content") or "").strip()
            dt = msg.get("datetime")
            sender = msg.get("sender", "Unknown")

            if not content:
                continue

            total_messages += 1

            if dt and 0 <= dt.hour <= 5:
                night_messages += 1

            lowered = content.lower()
            normalized = " ".join(lowered.split())
            repeated_counter[normalized] += 1

            if len(content.split()) <= 3:
                short_messages += 1

            matched_categories = []
            for category, keywords in AIMessageAnalyzer.CATEGORY_RULES.items():
                if any(keyword in lowered for keyword in keywords):
                    category_hits[category] += 1
                    matched_categories.append(category)

            urls = AIMessageAnalyzer.URL_REGEX.findall(content)
            if urls:
                links_found += len(urls)

            if matched_categories:
                flagged_messages.append({
                    "sender": sender,
                    "text": content,
                    "categories": matched_categories
                })

        repeated_msgs = [
            (text, count)
            for text, count in repeated_counter.items()
            if count >= 3 and len(text) > 3
        ]

        score = 0
        reasons = []

        if night_messages >= 5:
            score += 15
            reasons.append(f"Elevated night activity detected ({night_messages} messages between 00:00 and 05:59).")

        if repeated_msgs:
            score += 20
            reasons.append("Repeated message patterns detected, which may indicate spam, automation, or coercive repetition.")

        if links_found >= 2:
            score += 15
            reasons.append(f"Multiple links detected ({links_found}), which may indicate phishing or suspicious redirection.")

        if category_hits["Credential Request"] >= 1:
            score += 25
            reasons.append("Credential or verification-related language detected.")

        if category_hits["Fraud / Financial"] >= 1:
            score += 20
            reasons.append("Financially relevant language detected.")

        if category_hits["Manipulation / Concealment"] >= 1:
            score += 20
            reasons.append("Concealment or secrecy-related language detected.")

        if category_hits["Urgency / Pressure"] >= 2:
            score += 15
            reasons.append("Urgency / pressure language appears repeatedly.")

        if category_hits["Threat / Coercion"] >= 1:
            score += 20
            reasons.append("Threatening or coercive wording detected.")

        if total_messages > 0 and short_messages / total_messages > 0.45:
            score += 10
            reasons.append("Large proportion of very short messages detected, which may indicate repetitive prompting or automation.")

        if score >= 60:
            risk = "HIGH"
        elif score >= 30:
            risk = "MEDIUM"
        else:
            risk = "LOW"

        categories = [name for name, count in category_hits.most_common() if count > 0]

        summary = AIMessageAnalyzer._build_summary(
            total_messages=total_messages,
            night_messages=night_messages,
            repeated_msgs=repeated_msgs,
            links_found=links_found,
            categories=categories,
            risk=risk
        )

        return {
            "summary": summary,
            "categories": categories,
            "risk": risk,
            "score": score,
            "reasons": reasons,
            "flagged_messages": flagged_messages[:10],
            "stats": {
                "total_messages": total_messages,
                "night_messages": night_messages,
                "links_found": links_found,
                "repeated_patterns": len(repeated_msgs)
            }
        }

    @staticmethod
    def _build_summary(total_messages, night_messages, repeated_msgs, links_found, categories, risk):
        parts = []

        parts.append(f"The conversation analysis covered {total_messages} text messages.")

        if categories:
            parts.append("Detected semantic categories include: " + ", ".join(categories) + ".")

        if night_messages > 0:
            parts.append(f"{night_messages} messages were sent during night hours.")

        if repeated_msgs:
            parts.append("Repeated message patterns were identified, which may indicate spam, pressure tactics, or automation.")

        if links_found > 0:
            parts.append(f"{links_found} links were found in the conversation.")

        parts.append(f"Overall AI-assisted conversation risk was assessed as {risk}.")

        return " ".join(parts)
