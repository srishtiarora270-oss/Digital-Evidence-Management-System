import csv
import os
from datetime import datetime


class ReportGenerator:

    def _ensure_directory(self, filename):
        directory = os.path.dirname(filename)
        if directory:
            os.makedirs(directory, exist_ok=True)

    def generate_txt_report(
            self,
            filename,
            data):

        self._ensure_directory(filename)
        with open(filename, "w", encoding="utf-8") as file:
            file.write(
                f"Report Generated: "
                f"{datetime.now()}\n\n"
            )
            for item in data:
                file.write(str(item))
                file.write("\n\n")

    def generate_csv_report(
            self,
            filename,
            data):

        if not data:
            return

        self._ensure_directory(filename)
        with open(
                filename,
                "w",
                newline="",
                encoding="utf-8"
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=data[0].keys()
            )

            writer.writeheader()
            writer.writerows(data)

    def generate_summary_report(self, filename, cases, evidence):
        self._ensure_directory(filename)

        closed_cases = [
            c for c in cases
            if c.get("investigation_status", "").lower() == "closed"
        ]
        active_cases = [
            c for c in cases
            if c.get("investigation_status", "").lower() != "closed"
        ]
        high_priority = [
            c for c in cases
            if c.get("priority_level", "").lower() in ("high", "urgent", "critical")
        ]

        evidence_by_type = {}
        evidence_by_status = {}

        for item in evidence:
            evidence_type = item.get("type", "Unknown")
            status = item.get("status", "Unknown")
            evidence_by_type[evidence_type] = evidence_by_type.get(evidence_type, 0) + 1
            evidence_by_status[status] = evidence_by_status.get(status, 0) + 1

        with open(filename, "w", encoding="utf-8") as file:
            file.write(f"Summary Report Generated: {datetime.now()}\n\n")
            file.write(f"Total Cases: {len(cases)}\n")
            file.write(f"Active Investigations: {len(active_cases)}\n")
            file.write(f"Closed Cases: {len(closed_cases)}\n")
            file.write(f"High Priority Cases: {len(high_priority)}\n\n")

            file.write("High Priority Case IDs:\n")
            for case in high_priority:
                file.write(
                    f"  - {case.get('case_id', 'Unknown')} : {case.get('crime_type', '')} "
                    f"({case.get('priority_level', '')})\n"
                )
            file.write("\n")

            file.write("Evidence Summary by Type:\n")
            for evidence_type, count in evidence_by_type.items():
                file.write(f"  - {evidence_type}: {count}\n")
            file.write("\n")

            file.write("Evidence Summary by Status:\n")
            for status, count in evidence_by_status.items():
                file.write(f"  - {status}: {count}\n")
