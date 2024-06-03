import sqlite3


class JsCodeInjections:
    def __init__(self, db_name="db/variations.db"):
        self.db_name = db_name
        self._create_table()

    def _create_table(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS js_code_injections (
                    id INTEGER PRIMARY KEY,
                    snippet TEXT
                )
            """)
            conn.commit()

    def add_injection(self, snippet):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO js_code_injections (snippet) VALUES (?)", (snippet,))
            conn.commit()
            return cursor.lastrowid

    def get_injection_by_id(self, snippet_id):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, snippet FROM js_code_injections WHERE id = ?", (snippet_id,))
            return cursor.fetchone()

    def update_injection(self, snippet_id, snippet):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE js_code_injections SET snippet = ? WHERE id = ?", (snippet, snippet_id))
            conn.commit()

    def delete_injection(self, snippet_id):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM js_code_injections WHERE id = ?", (snippet_id,))
            conn.commit()

    def get_all_injections(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, snippet FROM js_code_injections")
            return cursor.fetchall()

    def delete_all_injections(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM js_code_injections")
            conn.commit()

# Usage example:
if __name__ == "__main__":
    db = JsCodeInjections()

    # Insert a new record
    # record_id = db.add_injection("console.log('Hello, world!');")
    # print(f"Inserted record with ID: {record_id}")

    # # Retrieve a record by ID
    # record = db.get_injection_by_id(record_id)
    # print(record)
    #
    # # Update a record
    # db.update_injection(record_id, "console.log('Updated code');")

    # Get all records
    all_records = db.get_all_injections()
    print(all_records)
    #
    # # Delete a record
    # db.delete_injection(record_id)
