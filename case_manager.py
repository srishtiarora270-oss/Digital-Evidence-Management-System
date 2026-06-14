import json
import os

from storage_utils import load_encrypted_json, save_encrypted_json

CASE_FILE = "data/cases.json.enc"


class CaseManager:

    def __init__(self):
        self.cases = self.load_cases()

    def load_cases(self):
        if os.path.exists(CASE_FILE):
            try:
                return load_encrypted_json(CASE_FILE)
            except Exception:
                pass

        fallback_file = "data/cases.json"
        if os.path.exists(fallback_file):
            with open(fallback_file, "r", encoding="utf-8") as file:
                data = json.load(file)
            self.cases = data
            self.save_cases()
            return data

        return []

    def save_cases(self):
        os.makedirs(os.path.dirname(CASE_FILE), exist_ok=True)
        save_encrypted_json(CASE_FILE, self.cases)

    def add_case(self, case):

        for c in self.cases:
            if c["case_id"] == case["case_id"]:
                raise ValueError("Case ID already exists")

        self.cases.append(case)
        self.save_cases()

    def update_status(self, case_id, status):

        for case in self.cases:

            if case["case_id"] == case_id:
                case["investigation_status"] = status
                self.save_cases()
                return True

        return False

    def delete_case(self, case_id):

        self.cases = [
            c for c in self.cases
            if c["case_id"] != case_id
        ]

        self.save_cases()

    def view_all_cases(self):

        return self.cases

    def search_case(self, case_id):

        for case in self.cases:
            if case["case_id"] == case_id:
                return case

        return None