from datetime import datetime


def _parse_date(value):
    try:
        return datetime.strptime(value.strip(), "%d-%m-%Y").date()
    except Exception:
        return None


def filter_cases(
        cases,
        crime_type=None,
        officer=None,
        status=None,
        priority=None,
        date_from=None,
        date_to=None):

    filtered = cases

    if crime_type:
        filtered = [
            c for c in filtered
            if c.get("crime_type", "").lower() == crime_type.lower()
        ]

    if officer:
        filtered = [
            c for c in filtered
            if c.get("officer_assigned", "").lower() == officer.lower()
        ]

    if status:
        filtered = [
            c for c in filtered
            if c.get("investigation_status", "").lower() == status.lower()
        ]

    if priority:
        filtered = [
            c for c in filtered
            if c.get("priority_level", "").lower() == priority.lower()
        ]

    if date_from:
        start_date = _parse_date(date_from)
        if start_date:
            filtered = [
                c for c in filtered
                if _parse_date(c.get("date_of_incident", ""))
                and _parse_date(c.get("date_of_incident", "")) >= start_date
            ]

    if date_to:
        end_date = _parse_date(date_to)
        if end_date:
            filtered = [
                c for c in filtered
                if _parse_date(c.get("date_of_incident", ""))
                and _parse_date(c.get("date_of_incident", "")) <= end_date
            ]

    return filtered


def calculate_analytics(cases, evidence):
    total_cases = len(cases)
    closed_cases = [c for c in cases if c.get("investigation_status", "").lower() == "closed"]
    active_cases = [c for c in cases if c.get("investigation_status", "").lower() != "closed"]
    high_priority = [c for c in cases if c.get("priority_level", "").lower() in ("high", "urgent", "critical")]

    today = datetime.now().date()
    open_case_ages = []
    stale_cases = []
    for c in active_cases:
        incident_date = _parse_date(c.get("date_of_incident", ""))
        if incident_date:
            age = (today - incident_date).days
            open_case_ages.append(age)
            if age >= 60:
                stale_cases.append(c)

    avg_open_age = sum(open_case_ages) / len(open_case_ages) if open_case_ages else 0

    evidence_type_counts = {}
    evidence_by_case = {}
    evidence_status_counts = {}
    for item in evidence:
        evidence_type = item.get("type", "Unknown")
        evidence_type_counts[evidence_type] = evidence_type_counts.get(evidence_type, 0) + 1
        case_id = item.get("case_id", "Unknown")
        evidence_by_case[case_id] = evidence_by_case.get(case_id, 0) + 1
        evidence_status = item.get("status", "Unknown")
        evidence_status_counts[evidence_status] = evidence_status_counts.get(evidence_status, 0) + 1

    return {
        "total_cases": total_cases,
        "active_cases": len(active_cases),
        "closed_cases": len(closed_cases),
        "high_priority_cases": len(high_priority),
        "avg_open_case_age": avg_open_age,
        "stale_cases": stale_cases,
        "evidence_type_counts": evidence_type_counts,
        "evidence_status_counts": evidence_status_counts,
        "evidence_by_case": evidence_by_case,
    }
