import csv
import json
import time
import random
from pathlib import Path
from typing import List, Dict, Any
from app.core.config import TICKETS_CSV, ESCALATED_TICKETS_CSV, CHAT_HISTORY_JSON
from app.services.llm_helper import LLMHelper

class TicketHandler:
    """
    Manages support ticketing processes, writing structured tickets to CSV databases 
    (both data/tickets.csv and outputs/escalated_tickets.csv) and saving chat sessions 
    to outputs/chat_history.json.
    """
    def __init__(self):
        self.headers = [
            "Ticket ID", 
            "Name", 
            "Email", 
            "Ticket Title", 
            "Problem Summary", 
            "Priority", 
            "Recommended Team", 
            "Description", 
            "Status", 
            "Created At"
        ]
        self._ensure_files()

    def _ensure_files(self):
        for csv_path in [TICKETS_CSV, ESCALATED_TICKETS_CSV]:
            # If path exists, check if headers match
            should_recreate = False
            if csv_path.exists():
                try:
                    with open(csv_path, "r", encoding="utf-8") as f:
                        reader = csv.reader(f)
                        existing_headers = next(reader, [])
                        if len(existing_headers) != len(self.headers):
                            should_recreate = True
                except Exception:
                    should_recreate = True
            
            if should_recreate:
                try:
                    csv_path.unlink()
                except Exception:
                    pass

            if not csv_path.exists():
                csv_path.parent.mkdir(parents=True, exist_ok=True)
                with open(csv_path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(self.headers)

    def _get_ticket_count(self) -> int:
        try:
            with open(TICKETS_CSV, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                rows = list(reader)
                return max(0, len(rows) - 1)
        except Exception:
            return 0

    def get_all_tickets(self) -> List[Dict[str, Any]]:
        """Reads and parses the tickets from data/tickets.csv."""
        tickets = []
        if not TICKETS_CSV.exists():
            return tickets
            
        try:
            with open(TICKETS_CSV, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    tickets.append(dict(row))
        except Exception:
            pass
        return tickets

    def create_ticket(
        self,
        name: str,
        email: str,
        description: str,
        user_question: str,
        retrieved_context: List[Dict[str, Any]],
        llm_helper: LLMHelper
    ) -> Dict[str, Any]:
        """
        Creates a support ticket, generates AI title, summary, priority and recommended team,
        appends details to CSVs, and returns the ticket details.
        """
        # Generate the structured ticket fields via Gemini
        ticket_fields = llm_helper.generate_ticket_fields(user_question, retrieved_context)
        
        ticket_title = ticket_fields.get("ticket_title", f"Support Request: {user_question[:25]}...")
        problem_summary = ticket_fields.get("problem_summary", f"User question: {user_question}")
        priority = ticket_fields.get("priority", "Medium")
        recommended_team = ticket_fields.get("recommended_team", "Service Desk General Tier")
        
        ticket_count = self._get_ticket_count()
        ticket_num = 1000 + ticket_count + 1
        ticket_id = f"TKT-{ticket_num}"
        created_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        status = "Open"
        
        ticket_data = [
            ticket_id,
            name,
            email,
            ticket_title,
            problem_summary,
            priority,
            recommended_team,
            description,
            status,
            created_at
        ]
        
        # Write to both target CSV files
        for csv_path in [TICKETS_CSV, ESCALATED_TICKETS_CSV]:
            with open(csv_path, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(ticket_data)
                
        # Return a dictionary format
        return {
            "ticket_id": ticket_id,
            "name": name,
            "email": email,
            "ticket_title": ticket_title,
            "problem_summary": problem_summary,
            "priority": priority,
            "recommended_team": recommended_team,
            "description": description,
            "status": status,
            "created_at": created_at
        }

    @staticmethod
    def save_chat_history(conversation_history: List[Dict[str, Any]]):
        """Saves current conversation session to outputs/chat_history.json."""
        try:
            CHAT_HISTORY_JSON.parent.mkdir(parents=True, exist_ok=True)
            with open(CHAT_HISTORY_JSON, "w", encoding="utf-8") as f:
                json.dump(conversation_history, f, indent=4)
        except Exception:
            pass

    @staticmethod
    def get_chat_history() -> List[Dict[str, Any]]:
        """Reads conversation session from outputs/chat_history.json."""
        if not CHAT_HISTORY_JSON.exists():
            return []
        try:
            with open(CHAT_HISTORY_JSON, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def generate_random_tickets(self, n: int = 5) -> List[Dict[str, Any]]:
        """Generates random mock tickets and appends them to the DB."""
        first_names = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace"]
        last_names = ["Smith", "Jones", "Taylor", "Brown", "Williams", "Davis"]
        issues = [
            ("VPN not connecting", "Network Services"),
            ("Cannot login to Outlook", "Identity & Access Management"),
            ("Printer paper jam on floor 3", "Hardware Support"),
            ("Laptop battery dying quickly", "Hardware Support"),
            ("Need access to GitHub repo", "Identity & Access Management"),
            ("Wi-Fi keeps dropping at home", "Network Services")
        ]
        priorities = ["Low", "Medium", "High"]
        
        generated = []
        for _ in range(n):
            fname = random.choice(first_names)
            lname = random.choice(last_names)
            name = f"{fname} {lname}"
            email = f"{fname.lower()}.{lname.lower()}@company.com"
            issue, team = random.choice(issues)
            priority = random.choice(priorities)
            
            ticket_count = self._get_ticket_count()
            ticket_id = f"TKT-{1000 + ticket_count + 1}"
            created_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() - random.randint(0, 86400 * 7)))
            
            ticket_data = [
                ticket_id,
                name,
                email,
                f"Issue: {issue}",
                issue,
                priority,
                team,
                f"Automatically generated random ticket for {issue}.",
                "Open",
                created_at
            ]
            
            for csv_path in [TICKETS_CSV, ESCALATED_TICKETS_CSV]:
                with open(csv_path, "a", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(ticket_data)
                    
            generated.append({
                "ticket_id": ticket_id,
                "name": name,
                "email": email,
                "ticket_title": f"Issue: {issue}",
                "problem_summary": issue,
                "priority": priority,
                "recommended_team": team,
                "description": f"Automatically generated random ticket for {issue}.",
                "status": "Open",
                "created_at": created_at
            })
            
        return generated
