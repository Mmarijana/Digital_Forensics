class RiskEngine:

    @staticmethod
    def analyze_logins_ai(logins):
        suspicious = []
        known_locations = set()
        known_ips = set()

        for login in logins:
            reasons = []
            loc = login.get("location", "N/A")
            ip = login.get("ip", "N/A")

            if loc not in known_locations:
                reasons.append("New location")

            if ip not in known_ips:
                reasons.append("New IP address")

            if reasons:
                suspicious.append({
                    "date": login.get("date", "N/A"),
                    "location": loc,
                    "ip": ip,
                    "reasons": reasons
                })

            known_locations.add(loc)
            known_ips.add(ip)

        return suspicious

    @staticmethod
    def calculate_risk_score(logins):
        known_locations = set()
        known_ips = set()

        scored = []
        total_score = 0

        for idx, login in enumerate(logins):
            score = 0
            reasons = []

            loc = login.get("location", "N/A")
            ip = login.get("ip", "N/A")

            if idx == 0:
                score += 10
                reasons.append("First record (+10)")

            if loc not in known_locations:
                score += 40
                reasons.append("New location (+40)")

            if ip not in known_ips:
                score += 20
                reasons.append("New IP (+20)")

            if score >= 70:
                level = "HIGH"
            elif score >= 40:
                level = "MEDIUM"
            else:
                level = "LOW"

            scored.append({
                "date": login.get("date", "N/A"),
                "location": loc,
                "ip": ip,
                "score": score,
                "level": level,
                "reasons": reasons
            })

            total_score += score
            known_locations.add(loc)
            known_ips.add(ip)

        if total_score >= 200:
            account_level = "HIGH"
        elif total_score >= 120:
            account_level = "MEDIUM"
        else:
            account_level = "LOW"

        return scored, total_score, account_level
