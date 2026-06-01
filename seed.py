"""
seed.py — Populate the database with realistic demo data.
Run: python seed.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from backend.app import init_db, get_db, now_iso

TICKETS = [
    {
        "ticket_id": "TKT-0001",
        "customer_name": "Sarah Mitchell",
        "customer_email": "sarah.mitchell@techcorp.io",
        "subject": "Unable to login after password reset",
        "description": "I reset my password using the link sent to my email but after entering the new password I keep getting 'Invalid credentials' error. I've tried three different browsers and incognito mode. This has been going on since yesterday morning.",
        "priority": "High",
        "status": "Open",
    },
    {
        "ticket_id": "TKT-0002",
        "customer_name": "James Okafor",
        "customer_email": "j.okafor@enterprise.com",
        "subject": "Billing statement shows incorrect charge",
        "description": "My latest invoice shows $299 but my plan is $99/month. I was charged three times in the same billing period. Please review and issue a refund for the extra charges.",
        "priority": "High",
        "status": "In Progress",
    },
    {
        "ticket_id": "TKT-0003",
        "customer_name": "Priya Nair",
        "customer_email": "priya.nair@designstudio.co",
        "subject": "Feature request: dark mode for mobile app",
        "description": "The web app has a great dark mode but the mobile app (iOS) does not have this option. Many users in our team work late and the bright screen is uncomfortable. Would love to see this added in a future update.",
        "priority": "Low",
        "status": "Open",
    },
    {
        "ticket_id": "TKT-0004",
        "customer_name": "Marcus Lee",
        "customer_email": "marcus@startupxyz.com",
        "subject": "CSV export includes extra blank rows",
        "description": "When I export my data to CSV, there are empty rows inserted every 50 records. This breaks our downstream data pipeline. Happens consistently with both Chrome and Firefox on Windows 11.",
        "priority": "Medium",
        "status": "Closed",
    },
    {
        "ticket_id": "TKT-0005",
        "customer_name": "Elena Vasquez",
        "customer_email": "e.vasquez@globalretail.net",
        "subject": "API rate limit seems lower than documented",
        "description": "Our documentation says 1000 requests/minute but we're hitting 429 errors at around 400 req/min. We have a Business tier subscription. Can you confirm our rate limits and check if there's a configuration issue?",
        "priority": "Medium",
        "status": "In Progress",
    },
    {
        "ticket_id": "TKT-0006",
        "customer_name": "Tom Erikson",
        "customer_email": "tom.erikson@nordic.se",
        "subject": "Cannot upload files larger than 5MB",
        "description": "The system rejects any file over 5MB with a generic error message. Our plan allows up to 50MB uploads according to our contract. Need this resolved urgently as we have client deliverables pending.",
        "priority": "High",
        "status": "Open",
    },
]

NOTES = [
    ("TKT-0002", "Looked into the billing system — confirmed double charge occurred due to a failed payment retry on our end. Refund of $200 has been initiated and should reflect in 3-5 business days.", "Alice (Finance)"),
    ("TKT-0002", "Customer confirmed receipt of refund confirmation email. Keeping ticket In Progress until refund fully processes.", "Support Agent"),
    ("TKT-0004", "Issue was traced to a pagination bug in the export module. Deployed hotfix in v2.4.1. Customer confirmed the fix works.", "Dev Team"),
    ("TKT-0005", "Checked account — Business tier should have 1000 req/min. Found a misconfiguration on their account. Applied correct rate limit tier. Monitoring for 24hrs.", "Support Agent"),
]


def run():
    init_db()
    with get_db() as conn:
        # Clear existing data
        conn.execute("DELETE FROM notes")
        conn.execute("DELETE FROM tickets")

        ts = now_iso()
        for t in TICKETS:
            conn.execute(
                """INSERT INTO tickets
                   (ticket_id, customer_name, customer_email, subject, description,
                    priority, status, created_at, updated_at)
                   VALUES (?,?,?,?,?,?,?,?,?)""",
                (t["ticket_id"], t["customer_name"], t["customer_email"],
                 t["subject"], t["description"], t["priority"], t["status"], ts, ts)
            )

        for ticket_id, note_text, author in NOTES:
            conn.execute(
                "INSERT INTO notes (ticket_id, note_text, author, created_at) VALUES (?,?,?,?)",
                (ticket_id, note_text, author, ts)
            )

    print(f"✅ Seeded {len(TICKETS)} tickets and {len(NOTES)} notes")


if __name__ == "__main__":
    run()
