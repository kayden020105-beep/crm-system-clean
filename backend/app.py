import sqlite3
import uuid
import os
from datetime import datetime, timezone
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder="../frontend", static_url_path="")
CORS(app)

DB_PATH = os.environ.get("DB_PATH", "crm.db")


# ── DB bootstrap ─────────────────────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    with get_db() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS tickets (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id   TEXT    UNIQUE NOT NULL,
            customer_name  TEXT NOT NULL,
            customer_email TEXT NOT NULL,
            subject        TEXT NOT NULL,
            description    TEXT NOT NULL,
            priority       TEXT NOT NULL DEFAULT 'Medium',
            status         TEXT NOT NULL DEFAULT 'Open',
            created_at     TEXT NOT NULL,
            updated_at     TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS notes (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id  TEXT NOT NULL REFERENCES tickets(ticket_id),
            note_text  TEXT NOT NULL,
            author     TEXT NOT NULL DEFAULT 'Support Agent',
            created_at TEXT NOT NULL
        );
        """)
    print("✅ Database initialised")


def ticket_counter():
    """Returns next sequential ticket number."""
    with get_db() as conn:
        row = conn.execute("SELECT COUNT(*) as c FROM tickets").fetchone()
        return row["c"] + 1


# ── Helpers ──────────────────────────────────────────────────────────────────

def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def row_to_dict(row):
    return dict(row) if row else None


# ── API Routes ────────────────────────────────────────────────────────────────

@app.route("/api/tickets", methods=["POST"])
def create_ticket():
    data = request.get_json(force=True)
    required = ["customer_name", "customer_email", "subject", "description"]
    missing = [f for f in required if not data.get(f, "").strip()]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    n = ticket_counter()
    ticket_id = f"TKT-{n:04d}"
    ts = now_iso()

    with get_db() as conn:
        conn.execute(
            """INSERT INTO tickets
               (ticket_id, customer_name, customer_email, subject, description,
                priority, status, created_at, updated_at)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (
                ticket_id,
                data["customer_name"].strip(),
                data["customer_email"].strip().lower(),
                data["subject"].strip(),
                data["description"].strip(),
                data.get("priority", "Medium"),
                "Open",
                ts, ts,
            ),
        )
    return jsonify({"ticket_id": ticket_id, "created_at": ts}), 201


@app.route("/api/tickets", methods=["GET"])
def list_tickets():
    status = request.args.get("status", "").strip()
    search = request.args.get("search", "").strip()
    priority = request.args.get("priority", "").strip()

    query = "SELECT * FROM tickets WHERE 1=1"
    params = []

    if status:
        query += " AND status = ?"
        params.append(status)

    if priority:
        query += " AND priority = ?"
        params.append(priority)

    if search:
        like = f"%{search}%"
        query += """ AND (
            customer_name  LIKE ? OR
            customer_email LIKE ? OR
            ticket_id      LIKE ? OR
            subject        LIKE ? OR
            description    LIKE ?
        )"""
        params.extend([like, like, like, like, like])

    query += " ORDER BY created_at DESC"

    with get_db() as conn:
        rows = conn.execute(query, params).fetchall()

    return jsonify([row_to_dict(r) for r in rows])


@app.route("/api/tickets/<ticket_id>", methods=["GET"])
def get_ticket(ticket_id):
    with get_db() as conn:
        ticket = conn.execute(
            "SELECT * FROM tickets WHERE ticket_id = ?", (ticket_id,)
        ).fetchone()
        if not ticket:
            return jsonify({"error": "Ticket not found"}), 404

        notes = conn.execute(
            "SELECT * FROM notes WHERE ticket_id = ? ORDER BY created_at ASC",
            (ticket_id,),
        ).fetchall()

    result = row_to_dict(ticket)
    result["notes"] = [row_to_dict(n) for n in notes]
    return jsonify(result)


@app.route("/api/tickets/<ticket_id>", methods=["PUT"])
def update_ticket(ticket_id):
    data = request.get_json(force=True)
    ts = now_iso()

    with get_db() as conn:
        ticket = conn.execute(
            "SELECT id FROM tickets WHERE ticket_id = ?", (ticket_id,)
        ).fetchone()
        if not ticket:
            return jsonify({"error": "Ticket not found"}), 404

        # Build dynamic update
        updates = ["updated_at = ?"]
        params = [ts]

        if "status" in data:
            valid = ["Open", "In Progress", "Closed"]
            if data["status"] not in valid:
                return jsonify({"error": f"Status must be one of: {valid}"}), 400
            updates.append("status = ?")
            params.append(data["status"])

        if "priority" in data:
            updates.append("priority = ?")
            params.append(data["priority"])

        params.append(ticket_id)
        conn.execute(
            f"UPDATE tickets SET {', '.join(updates)} WHERE ticket_id = ?", params
        )

        # Add note if provided
        if data.get("note_text", "").strip():
            conn.execute(
                "INSERT INTO notes (ticket_id, note_text, author, created_at) VALUES (?,?,?,?)",
                (
                    ticket_id,
                    data["note_text"].strip(),
                    data.get("author", "Support Agent"),
                    ts,
                ),
            )

    return jsonify({"success": True, "updated_at": ts})


@app.route("/api/tickets/<ticket_id>", methods=["DELETE"])
def delete_ticket(ticket_id):
    with get_db() as conn:
        result = conn.execute(
            "DELETE FROM tickets WHERE ticket_id = ?", (ticket_id,)
        )
        if result.rowcount == 0:
            return jsonify({"error": "Ticket not found"}), 404
        conn.execute("DELETE FROM notes WHERE ticket_id = ?", (ticket_id,))
    return jsonify({"success": True})


@app.route("/api/stats", methods=["GET"])
def get_stats():
    with get_db() as conn:
        total = conn.execute("SELECT COUNT(*) as c FROM tickets").fetchone()["c"]
        open_ = conn.execute(
            "SELECT COUNT(*) as c FROM tickets WHERE status='Open'"
        ).fetchone()["c"]
        inprog = conn.execute(
            "SELECT COUNT(*) as c FROM tickets WHERE status='In Progress'"
        ).fetchone()["c"]
        closed = conn.execute(
            "SELECT COUNT(*) as c FROM tickets WHERE status='Closed'"
        ).fetchone()["c"]
        recent = conn.execute(
            "SELECT * FROM tickets ORDER BY created_at DESC LIMIT 5"
        ).fetchall()
    return jsonify(
        {
            "total": total,
            "open": open_,
            "in_progress": inprog,
            "closed": closed,
            "recent": [row_to_dict(r) for r in recent],
        }
    )


# ── Serve frontend ────────────────────────────────────────────────────────────

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_frontend(path):
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, "index.html")


# ── Entry ─────────────────────────────────────────────────────────────────────

# Move init_db() here so Gunicorn triggers it upon importing the app!
init_db()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 CRM server running on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
