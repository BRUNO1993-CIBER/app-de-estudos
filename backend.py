import sqlite3
from datetime import date
from typing import Optional, List

DB_NAME = "study_plans_v2.db"
POMODORO_DURATION_SECONDS = 25 * 60 

SUBJECTS_LIST = [
    "Matemática", 
    "História",    
    "Física",      
    "Geografia",   
    "Química",      
    "Biologia",    
    "Filosofia",    
    "Sociologia",  
    "Português",    
    "Redação"      
]

class StudyRepository:
    def __init__(self, db_name: str):
        self.db_name = db_name
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_name)

    def _init_db(self):
        sql = """
        CREATE TABLE IF NOT EXISTS daily_study (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            study_date TEXT NOT NULL,
            subject_name TEXT NOT NULL,
            cycles_completed INTEGER DEFAULT 0,
            total_seconds INTEGER DEFAULT 0,
            status TEXT DEFAULT 'PENDING' 
        );
        """
        with self._get_connection() as conn:
            conn.execute(sql)

    def ensure_daily_plan_exists(self, subjects: List[str]):
        today = date.today().isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM daily_study WHERE study_date = ?", (today,))
            count = cursor.fetchone()[0]
            
            if count == 0:
                for subject in subjects:
                    cursor.execute("""
                        INSERT INTO daily_study (study_date, subject_name, status)
                        VALUES (?, ?, 'PENDING')
                    """, (today, subject))

    def get_current_subject(self) -> Optional[dict]:
        today = date.today().isoformat()
        sql = """
            SELECT id, subject_name, cycles_completed, status 
            FROM daily_study 
            WHERE study_date = ? AND status != 'FINISHED'
            ORDER BY id ASC
            LIMIT 1
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (today,))
            row = cursor.fetchone()
            
            if row:
                return {
                    "id": row[0],
                    "name": row[1],
                    "cycles": row[2],
                    "status": row[3]
                }
            return None

    def record_cycle(self, row_id: int, duration: int):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT cycles_completed FROM daily_study WHERE id = ?", (row_id,))
            current_cycles = cursor.fetchone()[0]
            new_cycles = current_cycles + 1
            
            new_status = 'COMPLETED' if new_cycles >= 4 else 'IN_PROGRESS'

            cursor.execute("""
                UPDATE daily_study 
                SET cycles_completed = ?, 
                    total_seconds = total_seconds + ?,
                    status = CASE WHEN status != 'FINISHED' THEN ? ELSE status END
                WHERE id = ?
            """, (new_cycles, duration, new_status, row_id))

    def mark_as_finished(self, row_id: int):
        with self._get_connection() as conn:
            conn.execute("UPDATE daily_study SET status = 'FINISHED' WHERE id = ?", (row_id,))

    def get_all_stats(self):
        sql = """
            SELECT study_date, subject_name, cycles_completed, total_seconds, status
            FROM daily_study
            WHERE total_seconds > 0
            ORDER BY study_date DESC, id ASC
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql)
            return cursor.fetchall()