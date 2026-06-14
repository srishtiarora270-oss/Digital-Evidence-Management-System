import os
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from datetime import datetime

from case_manager import CaseManager
from evidence_manager import EvidenceManager
from report_generator import ReportGenerator
from utils import calculate_analytics, filter_cases

USER_CREDENTIALS = {
    "admin": {"password": "admin123", "role": "Admin"},
    "officer": {"password": "officer123", "role": "Officer"},
}


class DEMSApp:
    def __init__(self):
        self.case_manager = CaseManager()
        self.evidence_manager = EvidenceManager()
        self.report_generator = ReportGenerator()
        self.user_name = None
        self.user_role = None

        self.root = tk.Tk()
        self.root.title("Digital Evidence Management System")
        self.root.geometry("1100x650")
        self.root.minsize(950, 550)
        self.root.configure(bg="#f4f7fb")

        self.style = ttk.Style(self.root)
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass

        self.style.configure("Header.TLabel", background="#2c3e50", foreground="white", font=("Segoe UI", 18, "bold"))
        self.style.configure("SubHeader.TLabel", background="#2c3e50", foreground="#d1d9e6", font=("Segoe UI", 10))
        self.style.configure("Accent.TLabelframe", background="#e8eef7", bordercolor="#6d84b4")
        self.style.configure("Accent.TLabelframe.Label", background="#5b7fa8", foreground="white", font=("Segoe UI", 10, "bold"))
        self.style.configure("Accent.TButton", background="#4a72c8", foreground="white", font=("Segoe UI", 10, "bold"))
        self.style.map("Accent.TButton", background=[("active", "#3b61a8")])
        self.style.configure("Treeview.Heading", background="#4a72c8", foreground="white", font=("Segoe UI", 9, "bold"))
        self.style.configure("Treeview", background="#f6f8fc", fieldbackground="#f6f8fc", rowheight=26, font=("Segoe UI", 9))
        self.style.map("Treeview", background=[("selected", "#cbd4f5")])

        self.login_frame = None
        self.main_frame = ttk.Frame(self.root)
        self.create_login_view()

    def create_login_view(self):
        self.login_frame = ttk.Frame(self.root)
        self.login_frame.pack(fill="both", expand=True, padx=30, pady=40)

        title_label = ttk.Label(self.login_frame, text="DEMS Role-Based Access", font=("Segoe UI", 18, "bold"))
        title_label.pack(pady=(10, 20))

        form_frame = ttk.LabelFrame(self.login_frame, text="Login", style="Accent.TLabelframe")
        form_frame.pack(padx=20, pady=10, fill="x")

        username_label = ttk.Label(form_frame, text="Username:")
        username_label.grid(row=0, column=0, sticky="w", padx=10, pady=8)
        self.username_entry = ttk.Entry(form_frame, width=28)
        self.username_entry.grid(row=0, column=1, padx=10, pady=8)

        password_label = ttk.Label(form_frame, text="Password:")
        password_label.grid(row=1, column=0, sticky="w", padx=10, pady=8)
        self.password_entry = ttk.Entry(form_frame, width=28, show="*")
        self.password_entry.grid(row=1, column=1, padx=10, pady=8)

        role_label = ttk.Label(form_frame, text="Role:")
        role_label.grid(row=2, column=0, sticky="w", padx=10, pady=8)
        self.role_combo = ttk.Combobox(form_frame, values=["Admin", "Officer"], state="readonly", width=26)
        self.role_combo.grid(row=2, column=1, padx=10, pady=8)
        self.role_combo.set("")

        self.username_entry.bind("<KeyRelease>", self.update_role_from_username)

        login_button = ttk.Button(form_frame, text="Login", command=self.handle_login, style="Accent.TButton")
        login_button.grid(row=3, column=0, columnspan=2, pady=14)

        note_label = ttk.Label(self.login_frame, text="Use admin/admin123 or officer/officer123", foreground="#666666")
        note_label.pack(pady=6)

    def handle_login(self):
        username = self.username_entry.get().strip().lower()
        password = self.password_entry.get().strip()
        role = self.role_combo.get()

        user = USER_CREDENTIALS.get(username)
        if not user or user["password"] != password or user["role"] != role:
            messagebox.showerror("Login Failed", "Invalid username, password, or role.")
            return

        self.user_name = username.title()
        self.user_role = role
        self.login_frame.destroy()
        self.create_widgets()
        self.apply_role_permissions()
        self.main_frame.pack(fill="both", expand=True)
        self.refresh_case_list()
        self.refresh_evidence_list()
        self.refresh_dashboard()

    def update_role_from_username(self, event=None):
        username = self.username_entry.get().strip().lower()
        user = USER_CREDENTIALS.get(username)
        if user:
            self.role_combo.set(user["role"])

    def create_widgets(self):
        top_banner = tk.Frame(self.main_frame, bg="#2c3e50", height=100)
        top_banner.pack(fill="x", side="top")

        logo_canvas = tk.Canvas(top_banner, width=90, height=90, bg="#2c3e50", highlightthickness=0)
        logo_canvas.pack(side="left", padx=20, pady=5)
        logo_canvas.create_oval(10, 10, 80, 80, fill="#4a72c8", outline="")
        logo_canvas.create_text(45, 45, text="DE", fill="white", font=("Segoe UI", 16, "bold"))

        title_frame = tk.Frame(top_banner, bg="#2c3e50")
        title_frame.pack(fill="y", side="left", padx=8, pady=10)

        title_label = ttk.Label(title_frame, text="Digital Evidence Management System", style="Header.TLabel")
        title_label.pack(anchor="w")
        subtitle_label = ttk.Label(title_frame, text="Manage cases, evidence, analytics, and secure reports.", style="SubHeader.TLabel")
        subtitle_label.pack(anchor="w", pady=4)

        self.user_info_label = ttk.Label(title_frame, text=f"Logged in as: {self.user_name} ({self.user_role})", style="SubHeader.TLabel")
        self.user_info_label.pack(anchor="w", pady=4)

        notebook = ttk.Notebook(self.main_frame)
        notebook.pack(fill="both", expand=True, padx=10, pady=(10, 10))
        self.notebook = notebook

        self.case_frame = ttk.Frame(notebook)
        self.evidence_frame = ttk.Frame(notebook)
        self.report_frame = ttk.Frame(notebook)
        self.dashboard_frame = ttk.Frame(notebook)

        notebook.add(self.case_frame, text="Cases")
        notebook.add(self.evidence_frame, text="Evidence")
        notebook.add(self.report_frame, text="Reports")
        notebook.add(self.dashboard_frame, text="Dashboard")

        self.build_case_tab()
        self.build_evidence_tab()
        self.build_report_tab()
        self.build_dashboard_tab()

    def build_case_tab(self):
        left_frame = ttk.Frame(self.case_frame)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        right_frame = ttk.Frame(self.case_frame)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.case_frame.columnconfigure(0, weight=2)
        self.case_frame.columnconfigure(1, weight=3)
        self.case_frame.rowconfigure(0, weight=1)

        form_frame = ttk.LabelFrame(left_frame, text="Case Details", style="Accent.TLabelframe")
        form_frame.pack(fill="x", expand=False)

        labels = [
            "Case ID", "Crime Type", "Location", "Date (DD-MM-YYYY)",
            "Officer", "Suspect", "Evidence Type", "Evidence Description",
            "Status", "Priority"
        ]

        self.case_entries = {}
        for index, label_text in enumerate(labels):
            label = ttk.Label(form_frame, text=label_text)
            label.grid(row=index, column=0, sticky="w", pady=4, padx=4)

            entry = ttk.Entry(form_frame, width=32)
            entry.grid(row=index, column=1, sticky="ew", pady=4, padx=4)
            self.case_entries[label_text] = entry

        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill="x", pady=12)

        self.add_case_button = ttk.Button(button_frame, text="Add Case", command=self.handle_add_case, style="Accent.TButton")
        self.add_case_button.grid(row=0, column=0, padx=6, pady=4)

        self.delete_case_button = ttk.Button(button_frame, text="Delete Case", command=self.handle_delete_case, style="Accent.TButton")
        self.delete_case_button.grid(row=0, column=1, padx=6, pady=4)

        update_frame = ttk.LabelFrame(left_frame, text="Update Status", style="Accent.TLabelframe")
        update_frame.pack(fill="x", pady=8)

        self.update_case_id_entry = ttk.Entry(update_frame, width=20)
        self.update_case_id_entry.grid(row=0, column=0, padx=4, pady=4)
        self.update_case_id_entry.insert(0, "Case ID")

        self.update_status_entry = ttk.Entry(update_frame, width=20)
        self.update_status_entry.grid(row=0, column=1, padx=4, pady=4)
        self.update_status_entry.insert(0, "New Status")

        self.update_case_button = ttk.Button(update_frame, text="Update", command=self.handle_update_status, style="Accent.TButton")
        self.update_case_button.grid(row=0, column=2, padx=4, pady=4)

        search_frame = ttk.LabelFrame(left_frame, text="Search Case", style="Accent.TLabelframe")
        search_frame.pack(fill="x", pady=8)

        self.search_case_id_entry = ttk.Entry(search_frame, width=24)
        self.search_case_id_entry.grid(row=0, column=0, padx=4, pady=4)
        self.search_case_id_entry.insert(0, "Case ID")

        self.search_button = ttk.Button(search_frame, text="Search", command=self.handle_search_case, style="Accent.TButton")
        self.search_button.grid(row=0, column=1, padx=4, pady=4)

        self.clear_filter_button = ttk.Button(search_frame, text="Clear Filter", command=self.clear_case_filters, style="Accent.TButton")
        self.clear_filter_button.grid(row=0, column=2, padx=4, pady=4)

        filter_frame = ttk.LabelFrame(left_frame, text="Filter Cases", style="Accent.TLabelframe")
        filter_frame.pack(fill="x", pady=8)

        self.filter_crime_type_entry = ttk.Entry(filter_frame, width=18)
        self.filter_crime_type_entry.grid(row=0, column=0, padx=4, pady=4)
        self.filter_crime_type_entry.insert(0, "Crime Type")

        self.filter_officer_entry = ttk.Entry(filter_frame, width=18)
        self.filter_officer_entry.grid(row=0, column=1, padx=4, pady=4)
        self.filter_officer_entry.insert(0, "Officer")

        self.filter_status_entry = ttk.Entry(filter_frame, width=18)
        self.filter_status_entry.grid(row=1, column=0, padx=4, pady=4)
        self.filter_status_entry.insert(0, "Status")

        self.filter_priority_entry = ttk.Entry(filter_frame, width=18)
        self.filter_priority_entry.grid(row=1, column=1, padx=4, pady=4)
        self.filter_priority_entry.insert(0, "Priority")

        self.filter_date_from_entry = ttk.Entry(filter_frame, width=18)
        self.filter_date_from_entry.grid(row=2, column=0, padx=4, pady=4)
        self.filter_date_from_entry.insert(0, "Date From")

        self.filter_date_to_entry = ttk.Entry(filter_frame, width=18)
        self.filter_date_to_entry.grid(row=2, column=1, padx=4, pady=4)
        self.filter_date_to_entry.insert(0, "Date To")

        self.filter_button = ttk.Button(filter_frame, text="Apply Filter", command=self.handle_filter_cases, style="Accent.TButton")
        self.filter_button.grid(row=3, column=0, padx=4, pady=6)

        self.filter_clear_button = ttk.Button(filter_frame, text="Clear Filters", command=self.clear_case_filters, style="Accent.TButton")
        self.filter_clear_button.grid(row=3, column=1, padx=4, pady=6)

        self.case_tree = ttk.Treeview(
            right_frame,
            columns=(
                "case_id", "crime_type", "location", "date", "officer",
                "suspect", "evidence_type", "description", "status", "priority"
            ),
            show="headings",
            selectmode="browse"
        )

        self.case_tree.heading("case_id", text="Case ID")
        self.case_tree.heading("crime_type", text="Crime Type")
        self.case_tree.heading("location", text="Location")
        self.case_tree.heading("date", text="Date")
        self.case_tree.heading("officer", text="Officer")
        self.case_tree.heading("suspect", text="Suspect")
        self.case_tree.heading("evidence_type", text="Evidence Type")
        self.case_tree.heading("description", text="Evidence Description")
        self.case_tree.heading("status", text="Status")
        self.case_tree.heading("priority", text="Priority")

        self.case_tree.column("case_id", width=90, anchor="center")
        self.case_tree.column("crime_type", width=110, anchor="center")
        self.case_tree.column("location", width=120, anchor="center")
        self.case_tree.column("date", width=100, anchor="center")
        self.case_tree.column("officer", width=120, anchor="center")
        self.case_tree.column("suspect", width=120, anchor="center")
        self.case_tree.column("evidence_type", width=110, anchor="center")
        self.case_tree.column("description", width=180, anchor="w")
        self.case_tree.column("status", width=100, anchor="center")
        self.case_tree.column("priority", width=100, anchor="center")

        self.case_tree.bind("<Double-1>", self.populate_case_form)

        scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=self.case_tree.yview)
        self.case_tree.configure(yscroll=scrollbar.set)
        self.case_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def build_evidence_tab(self):
        top_frame = ttk.LabelFrame(self.evidence_frame, text="Evidence Entry", style="Accent.TLabelframe")
        top_frame.pack(fill="x", padx=10, pady=10)

        fields = ["Evidence ID", "Case ID", "Evidence Type", "Description", "Status"]
        self.evidence_entries = {}

        for index, label_text in enumerate(fields):
            label = ttk.Label(top_frame, text=label_text)
            label.grid(row=index, column=0, sticky="w", padx=6, pady=4)

            entry = ttk.Entry(top_frame, width=36)
            entry.grid(row=index, column=1, sticky="ew", padx=6, pady=4)
            self.evidence_entries[label_text] = entry

        add_button = ttk.Button(top_frame, text="Add Evidence", command=self.handle_add_evidence, style="Accent.TButton")
        add_button.grid(row=len(fields), column=0, columnspan=2, pady=8)

        search_frame = ttk.Frame(self.evidence_frame)
        search_frame.pack(fill="x", padx=10, pady=4)

        self.search_evidence_case_id = ttk.Entry(search_frame, width=24)
        self.search_evidence_case_id.grid(row=0, column=0, padx=4, pady=4)
        self.search_evidence_case_id.insert(0, "Case ID")

        show_button = ttk.Button(search_frame, text="Show Evidence for Case", command=self.handle_show_case_evidence, style="Accent.TButton")
        show_button.grid(row=0, column=1, padx=4, pady=4)

        clear_button = ttk.Button(search_frame, text="Show All Evidence", command=self.refresh_evidence_list, style="Accent.TButton")
        clear_button.grid(row=0, column=2, padx=4, pady=4)

        action_frame = ttk.LabelFrame(self.evidence_frame, text="Evidence Actions", style="Accent.TLabelframe")
        action_frame.pack(fill="x", padx=10, pady=8)

        self.update_evidence_id_entry = ttk.Entry(action_frame, width=24)
        self.update_evidence_id_entry.grid(row=0, column=0, padx=4, pady=4)
        self.update_evidence_id_entry.insert(0, "Evidence ID")

        self.update_evidence_status_entry = ttk.Entry(action_frame, width=24)
        self.update_evidence_status_entry.grid(row=0, column=1, padx=4, pady=4)
        self.update_evidence_status_entry.insert(0, "New Status")

        self.update_evidence_button = ttk.Button(action_frame, text="Update Status", command=self.handle_update_evidence_status, style="Accent.TButton")
        self.update_evidence_button.grid(row=0, column=2, padx=4, pady=4)

        self.delete_evidence_button = ttk.Button(action_frame, text="Delete Evidence", command=self.handle_delete_evidence, style="Accent.TButton")
        self.delete_evidence_button.grid(row=0, column=3, padx=4, pady=4)

        table_frame = ttk.Frame(self.evidence_frame)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.evidence_tree = ttk.Treeview(
            table_frame,
            columns=("evidence_id", "case_id", "type", "description", "status"),
            show="headings",
            selectmode="browse"
        )
        self.evidence_tree.heading("evidence_id", text="Evidence ID")
        self.evidence_tree.heading("case_id", text="Case ID")
        self.evidence_tree.heading("type", text="Type")
        self.evidence_tree.heading("description", text="Description")
        self.evidence_tree.heading("status", text="Status")

        self.evidence_tree.column("evidence_id", width=120, anchor="center")
        self.evidence_tree.column("case_id", width=120, anchor="center")
        self.evidence_tree.column("type", width=140, anchor="center")
        self.evidence_tree.column("description", width=360, anchor="w")
        self.evidence_tree.column("status", width=120, anchor="center")

        evidence_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.evidence_tree.yview)
        self.evidence_tree.configure(yscroll=evidence_scroll.set)
        self.evidence_tree.pack(side="left", fill="both", expand=True)
        self.evidence_tree.bind("<Double-1>", self.populate_evidence_form)
        evidence_scroll.pack(side="right", fill="y")

    def build_report_tab(self):
        frame = ttk.Frame(self.report_frame)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        label = ttk.Label(
            frame,
            text="Generate encrypted report files and summary analytics.",
            font=(None, 12)
        )
        label.pack(pady=12)

        self.generate_report_button = ttk.Button(frame, text="Generate Reports", command=self.handle_generate_reports, style="Accent.TButton")
        self.generate_report_button.pack(pady=10)

        self.report_status_label = ttk.Label(frame, text="Reports will be saved under ./reports", foreground="green")
        self.report_status_label.pack(pady=6)

    def build_dashboard_tab(self):
        frame = ttk.Frame(self.dashboard_frame)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        stats_frame = ttk.LabelFrame(frame, text="Investigation Analytics", style="Accent.TLabelframe")
        stats_frame.pack(fill="x", padx=10, pady=10)

        self.analytics_labels = {}
        fields = [
            ("Total Cases", "total_cases"),
            ("Active Cases", "active_cases"),
            ("Closed Cases", "closed_cases"),
            ("High Priority", "high_priority_cases"),
            ("Avg Open Case Age (days)", "avg_open_case_age"),
            ("Stale Open Cases", "stale_case_count"),
        ]

        for index, (label_text, key) in enumerate(fields):
            label = ttk.Label(stats_frame, text=f"{label_text}:", font=("Segoe UI", 10, "bold"))
            label.grid(row=index, column=0, sticky="w", padx=10, pady=6)
            value_label = ttk.Label(stats_frame, text="0", font=("Segoe UI", 10))
            value_label.grid(row=index, column=1, sticky="w", padx=10, pady=6)
            self.analytics_labels[key] = value_label

        chart_frame = ttk.LabelFrame(frame, text="Dashboard Charts", style="Accent.TLabelframe")
        chart_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.dashboard_canvas = tk.Canvas(chart_frame, bg="#ffffff", height=320)
        self.dashboard_canvas.pack(fill="both", expand=True, padx=10, pady=10)

        details_frame = ttk.LabelFrame(frame, text="Stale Cases", style="Accent.TLabelframe")
        details_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.stale_cases_text = tk.Text(details_frame, height=6, wrap="word", background="#f6f8fc", borderwidth=0)
        self.stale_cases_text.pack(fill="both", expand=True, padx=10, pady=10)
        self.stale_cases_text.configure(state="disabled")

    def apply_role_permissions(self):
        if self.user_role == "Officer":
            self.delete_case_button.state(["disabled"])
            self.delete_evidence_button.state(["disabled"])
            self.generate_report_button.state(["disabled"])
            self.filter_button.state(["!disabled"])
            self.search_button.state(["!disabled"])
        else:
            self.delete_case_button.state(["!disabled"])
            self.delete_evidence_button.state(["!disabled"])
            self.generate_report_button.state(["!disabled"])

    def clear_placeholder(self, event):
        widget = event.widget
        current = widget.get()
        if current in ["Case ID", "New Status", "Crime Type", "Officer", "Status", "Priority", "Date From", "Date To", "Evidence ID", "Description", "Evidence Type"]:
            widget.delete(0, tk.END)

    def populate_case_form(self, event=None):
        selected = self.case_tree.selection()
        if not selected:
            return

        values = self.case_tree.item(selected[0], "values")
        keys = [
            "Case ID", "Crime Type", "Location", "Date (DD-MM-YYYY)",
            "Officer", "Suspect", "Evidence Type", "Evidence Description",
            "Status", "Priority"
        ]

        for key, value in zip(keys, values):
            self.case_entries[key].delete(0, tk.END)
            self.case_entries[key].insert(0, value or "")

        self.search_case_id_entry.delete(0, tk.END)
        self.search_case_id_entry.insert(0, values[0])
        self.update_case_id_entry.delete(0, tk.END)
        self.update_case_id_entry.insert(0, values[0])

    def populate_evidence_form(self, event=None):
        selected = self.evidence_tree.selection()
        if not selected:
            return

        values = self.evidence_tree.item(selected[0], "values")
        evidence_id = values[0] if len(values) > 0 else ""
        status = values[4] if len(values) > 4 else ""

        self.update_evidence_id_entry.delete(0, tk.END)
        self.update_evidence_id_entry.insert(0, evidence_id)
        self.update_evidence_status_entry.delete(0, tk.END)
        self.update_evidence_status_entry.insert(0, status)

    def collect_case_data(self):
        return {
            "case_id": self.case_entries["Case ID"].get().strip(),
            "crime_type": self.case_entries["Crime Type"].get().strip(),
            "crime_location": self.case_entries["Location"].get().strip(),
            "date_of_incident": self.case_entries["Date (DD-MM-YYYY)"].get().strip(),
            "officer_assigned": self.case_entries["Officer"].get().strip(),
            "suspect_name": self.case_entries["Suspect"].get().strip(),
            "evidence_type": self.case_entries["Evidence Type"].get().strip(),
            "evidence_description": self.case_entries["Evidence Description"].get().strip(),
            "investigation_status": self.case_entries["Status"].get().strip(),
            "priority_level": self.case_entries["Priority"].get().strip(),
        }

    def handle_add_case(self):
        case = self.collect_case_data()
        if not case["case_id"]:
            messagebox.showwarning("Validation", "Case ID is required.")
            return

        try:
            self.case_manager.add_case(case)
            self.refresh_case_list()
            self.refresh_dashboard()
            messagebox.showinfo("Success", "Case added successfully.")
            self.clear_case_form()
        except ValueError as exc:
            messagebox.showerror("Error", str(exc))
        except Exception as exc:
            messagebox.showerror("Error", f"Unable to add case: {exc}")

    def handle_delete_case(self):
        if self.user_role != "Admin":
            messagebox.showwarning("Permission Denied", "Only admin users can delete cases.")
            return

        case_id = self.update_case_id_entry.get().strip()
        if not case_id or case_id == "Case ID":
            selected = self.case_tree.selection()
            if selected:
                case_id = self.case_tree.item(selected[0], "values")[0]

        if not case_id:
            messagebox.showwarning("Validation", "Select or enter a valid Case ID to delete.")
            return

        confirm = messagebox.askyesno("Confirm Delete", f"Delete case {case_id}? This cannot be undone.")
        if not confirm:
            return

        self.case_manager.delete_case(case_id)
        self.refresh_case_list()
        self.refresh_dashboard()
        messagebox.showinfo("Deleted", "Case deleted successfully.")

    def handle_update_status(self):
        case_id = self.update_case_id_entry.get().strip()
        status = self.update_status_entry.get().strip()

        if not case_id or case_id == "Case ID":
            messagebox.showwarning("Validation", "Enter the Case ID to update.")
            return

        if not status or status == "New Status":
            messagebox.showwarning("Validation", "Enter a new status.")
            return

        success = self.case_manager.update_status(case_id, status)
        if success:
            self.refresh_case_list()
            self.refresh_dashboard()
            messagebox.showinfo("Success", "Case status updated.")
        else:
            messagebox.showwarning("Not Found", "Case ID not found.")

    def handle_search_case(self):
        case_id = self.search_case_id_entry.get().strip()
        if not case_id or case_id == "Case ID":
            messagebox.showwarning("Validation", "Enter a Case ID to search.")
            return

        case = self.case_manager.search_case(case_id)
        if not case:
            messagebox.showinfo("Search Result", "No case found with that ID.")
            return

        self.refresh_case_list([case])

    def handle_filter_cases(self):
        crime_type = self.filter_crime_type_entry.get().strip()
        officer = self.filter_officer_entry.get().strip()
        status = self.filter_status_entry.get().strip()
        priority = self.filter_priority_entry.get().strip()
        date_from = self.filter_date_from_entry.get().strip()
        date_to = self.filter_date_to_entry.get().strip()

        crime_type = "" if crime_type == "Crime Type" else crime_type
        officer = "" if officer == "Officer" else officer
        status = "" if status == "Status" else status
        priority = "" if priority == "Priority" else priority
        date_from = "" if date_from == "Date From" else date_from
        date_to = "" if date_to == "Date To" else date_to

        cases = filter_cases(
            self.case_manager.view_all_cases(),
            crime_type=crime_type,
            officer=officer,
            status=status,
            priority=priority,
            date_from=date_from,
            date_to=date_to
        )

        if not cases:
            messagebox.showinfo("No Results", "No cases matched the filter criteria.")

        self.refresh_case_list(cases)

    def clear_case_filters(self):
        for entry in [
            self.search_case_id_entry,
            self.filter_crime_type_entry,
            self.filter_officer_entry,
            self.filter_status_entry,
            self.filter_priority_entry,
            self.filter_date_from_entry,
            self.filter_date_to_entry,
        ]:
            entry.delete(0, tk.END)

        self.refresh_case_list()

    def handle_add_evidence(self):
        evidence = {
            "evidence_id": self.evidence_entries["Evidence ID"].get().strip(),
            "case_id": self.evidence_entries["Case ID"].get().strip(),
            "type": self.evidence_entries["Evidence Type"].get().strip(),
            "description": self.evidence_entries["Description"].get().strip(),
            "status": self.evidence_entries["Status"].get().strip(),
        }

        if not evidence["evidence_id"] or not evidence["case_id"]:
            messagebox.showwarning("Validation", "Evidence ID and Case ID are required.")
            return

        self.evidence_manager.add_evidence(evidence)
        self.refresh_evidence_list()
        self.refresh_dashboard()
        messagebox.showinfo("Success", "Evidence added successfully.")
        self.clear_evidence_form()

    def handle_show_case_evidence(self):
        case_id = self.search_evidence_case_id.get().strip()
        if not case_id or case_id == "Case ID":
            messagebox.showwarning("Validation", "Enter a Case ID to filter evidence.")
            return

        evidence_data = self.evidence_manager.get_case_evidence(case_id)
        if not evidence_data:
            messagebox.showinfo("No Evidence", "No evidence found for that case.")
            return

        self.refresh_evidence_list(evidence_data)

    def handle_update_evidence_status(self):
        evidence_id = self.update_evidence_id_entry.get().strip()
        status = self.update_evidence_status_entry.get().strip()

        if not evidence_id or evidence_id == "Evidence ID":
            messagebox.showwarning("Validation", "Enter the Evidence ID to update.")
            return

        if not status or status == "New Status":
            messagebox.showwarning("Validation", "Enter a new evidence status.")
            return

        success = self.evidence_manager.update_evidence_status(evidence_id, status)
        if success:
            self.refresh_evidence_list()
            self.refresh_dashboard()
            messagebox.showinfo("Success", "Evidence status updated.")
        else:
            messagebox.showwarning("Not Found", "Evidence ID not found.")

    def handle_delete_evidence(self):
        if self.user_role != "Admin":
            messagebox.showwarning("Permission Denied", "Only admin users can delete evidence.")
            return

        evidence_id = self.update_evidence_id_entry.get().strip()
        if not evidence_id or evidence_id == "Evidence ID":
            selected = self.evidence_tree.selection()
            if selected:
                evidence_id = self.evidence_tree.item(selected[0], "values")[0]

        if not evidence_id:
            messagebox.showwarning("Validation", "Select or enter a valid Evidence ID to delete.")
            return

        confirm = messagebox.askyesno("Confirm Delete", f"Delete evidence {evidence_id}? This cannot be undone.")
        if not confirm:
            return

        self.evidence_manager.delete_evidence(evidence_id)
        self.refresh_evidence_list()
        self.refresh_dashboard()
        messagebox.showinfo("Deleted", "Evidence deleted successfully.")

    def handle_generate_reports(self):
        if self.user_role != "Admin":
            messagebox.showwarning("Permission Denied", "Only admin users can generate reports.")
            return

        report_dir = "reports"
        os.makedirs(report_dir, exist_ok=True)

        cases = self.case_manager.view_all_cases()
        self.report_generator.generate_txt_report(
            os.path.join(report_dir, "case_report.txt"), cases
        )
        self.report_generator.generate_csv_report(
            os.path.join(report_dir, "case_report.csv"), cases
        )
        self.report_generator.generate_summary_report(
            os.path.join(report_dir, "case_summary.txt"), cases, self.evidence_manager.evidence
        )

        self.report_status_label.config(text="Reports generated in ./reports", foreground="blue")
        messagebox.showinfo("Reports", "Reports generated successfully.")

    def refresh_case_list(self, cases=None):
        for row in self.case_tree.get_children():
            self.case_tree.delete(row)

        cases = cases if cases is not None else self.case_manager.view_all_cases()
        for case in cases:
            self.case_tree.insert(
                "",
                "end",
                values=(
                    case.get("case_id", ""),
                    case.get("crime_type", ""),
                    case.get("crime_location", ""),
                    case.get("date_of_incident", ""),
                    case.get("officer_assigned", ""),
                    case.get("suspect_name", ""),
                    case.get("evidence_type", ""),
                    case.get("evidence_description", ""),
                    case.get("investigation_status", ""),
                    case.get("priority_level", ""),
                )
            )

    def refresh_evidence_list(self, evidence=None):
        for row in self.evidence_tree.get_children():
            self.evidence_tree.delete(row)

        evidence_data = evidence if evidence is not None else self.evidence_manager.evidence
        for item in evidence_data:
            self.evidence_tree.insert(
                "",
                "end",
                values=(
                    item.get("evidence_id", ""),
                    item.get("case_id", ""),
                    item.get("type", ""),
                    item.get("description", ""),
                    item.get("status", ""),
                )
            )

    def refresh_dashboard(self):
        analytics = calculate_analytics(self.case_manager.view_all_cases(), self.evidence_manager.evidence)
        self.analytics_labels["total_cases"].config(text=str(analytics["total_cases"]))
        self.analytics_labels["active_cases"].config(text=str(analytics["active_cases"]))
        self.analytics_labels["closed_cases"].config(text=str(analytics["closed_cases"]))
        self.analytics_labels["high_priority_cases"].config(text=str(analytics["high_priority_cases"]))
        self.analytics_labels["avg_open_case_age"].config(text=f"{analytics['avg_open_case_age']:.1f}")
        self.analytics_labels["stale_case_count"].config(text=str(len(analytics["stale_cases"])))

        self.draw_dashboard_chart(analytics)

        self.stale_cases_text.configure(state="normal")
        self.stale_cases_text.delete("1.0", tk.END)
        if analytics["stale_cases"]:
            for case in analytics["stale_cases"]:
                self.stale_cases_text.insert(tk.END, f"Case {case.get('case_id', 'Unknown')} - {case.get('crime_type', '')} ({case.get('date_of_incident', '')})\n")
        else:
            self.stale_cases_text.insert(tk.END, "No stale open cases detected.")
        self.stale_cases_text.configure(state="disabled")

    def draw_dashboard_chart(self, analytics):
        self.dashboard_canvas.delete("all")
        width = int(self.dashboard_canvas.winfo_width() or 760)
        height = int(self.dashboard_canvas.winfo_height() or 320)

        top_margin = 20
        bar_height = 24
        gap = 16
        left_margin = 140
        max_width = width - left_margin - 40

        status_counts = {
            "Active": analytics["active_cases"],
            "Closed": analytics["closed_cases"],
            "High Priority": analytics["high_priority_cases"],
        }

        max_value = max(status_counts.values() or [1])
        self.dashboard_canvas.create_text(20, top_margin - 10, anchor="w", text="Case Status", font=("Segoe UI", 10, "bold"))
        for index, (label, value) in enumerate(status_counts.items()):
            y = top_margin + index * (bar_height + gap)
            bar_length = int((value / max_value) * max_width) if max_value else 0
            self.dashboard_canvas.create_text(10, y + bar_height / 2, anchor="w", text=f"{label}")
            self.dashboard_canvas.create_rectangle(left_margin, y, left_margin + bar_length, y + bar_height, fill="#4a72c8", outline="")
            self.dashboard_canvas.create_text(left_margin + bar_length + 10, y + bar_height / 2, anchor="w", text=str(value))

        type_counts = analytics["evidence_type_counts"]
        if type_counts:
            start_y = top_margin + len(status_counts) * (bar_height + gap) + 30
            self.dashboard_canvas.create_text(20, start_y - 10, anchor="w", text="Evidence Types", font=("Segoe UI", 10, "bold"))
            max_type_value = max(type_counts.values())
            for index, (etype, count) in enumerate(type_counts.items()):
                y = start_y + index * (bar_height + gap)
                bar_length = int((count / max_type_value) * max_width) if max_type_value else 0
                self.dashboard_canvas.create_text(10, y + bar_height / 2, anchor="w", text=f"{etype}")
                self.dashboard_canvas.create_rectangle(left_margin, y, left_margin + bar_length, y + bar_height, fill="#6d84b4", outline="")
                self.dashboard_canvas.create_text(left_margin + bar_length + 10, y + bar_height / 2, anchor="w", text=str(count))

    def clear_case_form(self):
        for entry in self.case_entries.values():
            entry.delete(0, tk.END)

    def clear_evidence_form(self):
        for entry in self.evidence_entries.values():
            entry.delete(0, tk.END)

    def run(self):
        self.root.mainloop()


def run_app():
    app = DEMSApp()
    app.run()
