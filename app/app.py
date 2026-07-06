import os
import sqlite3
from flask import Flask, jsonify, request, g

app = Flask(__name__)

DB_PATH = os.environ.get("DB_PATH", "./data/tasks.db")


def get_db():
    if "db" not in g:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    with app.app_context():
        db = get_db()
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                done INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        db.commit()


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/tasks", methods=["GET"])
def list_tasks():
    db = get_db()
    rows = db.execute("SELECT id, title, done FROM tasks").fetchall()
    return jsonify([dict(row) for row in rows]), 200


@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json(silent=True) or {}
    title = data.get("title")
    if not title:
        return jsonify({"error": "title is required"}), 400
    db = get_db()
    cur = db.execute("INSERT INTO tasks (title, done) VALUES (?, 0)", (title,))
    db.commit()
    return jsonify({"id": cur.lastrowid, "title": title, "done": 0}), 201


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    db = get_db()
    db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    db.commit()
    return "", 204


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
else:
    init_db()
