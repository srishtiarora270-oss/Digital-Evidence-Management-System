import json
import os

from storage_utils import load_encrypted_json, save_encrypted_json

EVIDENCE_FILE = "data/evidence.json.enc"


class EvidenceManager:

    def __init__(self):
        self.evidence = self.load_evidence()

    def load_evidence(self):
        if os.path.exists(EVIDENCE_FILE):
            try:
                return load_encrypted_json(EVIDENCE_FILE)
            except Exception:
                pass

        fallback_file = "data/evidence.json"
        if os.path.exists(fallback_file):
            with open(fallback_file, "r", encoding="utf-8") as file:
                data = json.load(file)
            self.evidence = data
            self.save_evidence()
            return data

        return []

    def save_evidence(self):
        os.makedirs(os.path.dirname(EVIDENCE_FILE), exist_ok=True)
        save_encrypted_json(EVIDENCE_FILE, self.evidence)

    def add_evidence(self, evidence):

        self.evidence.append(evidence)
        self.save_evidence()

    def update_evidence_status(
            self,
            evidence_id,
            status):

        for ev in self.evidence:

            if ev["evidence_id"] == evidence_id:
                ev["status"] = status
                self.save_evidence()
                return True

        return False

    def delete_evidence(self, evidence_id):
        self.evidence = [
            e for e in self.evidence
            if e["evidence_id"] != evidence_id
        ]
        self.save_evidence()

    def get_case_evidence(self, case_id):

        return [
            e for e in self.evidence
            if e["case_id"] == case_id
        ]