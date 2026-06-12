"""
Database utility functions
"""
import aiosqlite
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional

DB_PATH = "data/productivity.db"

async def init_db():
    """Ma'lumotlar bazasini boshlash"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Foydalanuvchilar jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                created_at TEXT,
                timezone TEXT DEFAULT 'Asia/Tashkent',
                work_start_time TEXT DEFAULT '08:00',
                work_end_time TEXT DEFAULT '16:00'
            )
        """)
        
        # Vazifalar jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                task_name TEXT NOT NULL,
                category TEXT,
                priority INTEGER DEFAULT 1,
                duration_minutes INTEGER DEFAULT 60,
                active INTEGER DEFAULT 1,
                created_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)
        
        # Jadval (schedule) jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS schedule (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                task_id INTEGER,
                day_of_week INTEGER,
                start_time TEXT,
                end_time TEXT,
                active INTEGER DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (task_id) REFERENCES tasks (id)
            )
        """)
        
        # Bajarilgan vazifalar jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS completions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                task_id INTEGER,
                scheduled_time TEXT,
                completed_at TEXT,
                photo_path TEXT,
                notes TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (task_id) REFERENCES tasks (id)
            )
        """)
        
        # Haftalik testlar jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS weekly_tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                week_start TEXT,
                test_data TEXT,
                score INTEGER,
                completed_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)
        
        await db.commit()
    
    # Mavjud foydalanuvchilar uchun migration
    await migrate_existing_users()

async def add_user(user_id: int, username: str, full_name: str):
    """Yangi foydalanuvchi qo'shish"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR IGNORE INTO users (user_id, username, full_name, created_at)
            VALUES (?, ?, ?, ?)
        """, (user_id, username, full_name, datetime.now().isoformat()))
        await db.commit()

async def add_task(user_id: int, task_name: str, category: str, priority: int = 1, duration: int = 60):
    """Vazifa qo'shish"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO tasks (user_id, task_name, category, priority, duration_minutes, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, task_name, category, priority, duration, datetime.now().isoformat()))
        await db.commit()
        return cursor.lastrowid

async def get_user_tasks(user_id: int, active_only: bool = True) -> List[Dict]:
    """Foydalanuvchi vazifalarini olish"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        query = "SELECT * FROM tasks WHERE user_id = ?"
        if active_only:
            query += " AND active = 1"
        query += " ORDER BY priority DESC, category"
        
        async with db.execute(query, (user_id,)) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

async def add_schedule_item(user_id: int, task_id: int, day_of_week: int, start_time: str, end_time: str):
    """Jadvalga element qo'shish"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO schedule (user_id, task_id, day_of_week, start_time, end_time)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, task_id, day_of_week, start_time, end_time))
        await db.commit()

async def get_schedule(user_id: int, day_of_week: Optional[int] = None) -> List[Dict]:
    """Jadvalni olish"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        query = """
            SELECT s.*, t.task_name, t.category 
            FROM schedule s
            JOIN tasks t ON s.task_id = t.id
            WHERE s.user_id = ? AND s.active = 1
        """
        params = [user_id]
        
        if day_of_week is not None:
            query += " AND s.day_of_week = ?"
            params.append(day_of_week)
        
        query += " ORDER BY s.day_of_week, s.start_time"
        
        async with db.execute(query, params) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

async def mark_task_completed(user_id: int, task_id: int, scheduled_time: str, photo_path: Optional[str] = None, notes: Optional[str] = None):
    """Vazifani bajarilgan deb belgilash"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO completions (user_id, task_id, scheduled_time, completed_at, photo_path, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, task_id, scheduled_time, datetime.now().isoformat(), photo_path, notes))
        await db.commit()

async def get_weekly_stats(user_id: int, week_start: Optional[datetime] = None) -> Dict:
    """Haftalik statistika olish"""
    if week_start is None:
        week_start = datetime.now() - timedelta(days=datetime.now().weekday())
    
    week_end = week_start + timedelta(days=7)
    
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        # Jami rejalashtirilgan vazifalar
        async with db.execute("""
            SELECT COUNT(*) as total
            FROM schedule s
            WHERE s.user_id = ? AND s.active = 1
        """, (user_id,)) as cursor:
            row = await cursor.fetchone()
            total_scheduled = row['total'] * 7  # Haftalik
        
        # Bajarilgan vazifalar
        async with db.execute("""
            SELECT COUNT(*) as completed
            FROM completions
            WHERE user_id = ? 
            AND datetime(completed_at) >= datetime(?)
            AND datetime(completed_at) < datetime(?)
        """, (user_id, week_start.isoformat(), week_end.isoformat())) as cursor:
            row = await cursor.fetchone()
            completed = row['completed']
        
        # Kategoriya bo'yicha
        async with db.execute("""
            SELECT t.category, COUNT(*) as count
            FROM completions c
            JOIN tasks t ON c.task_id = t.id
            WHERE c.user_id = ?
            AND datetime(c.completed_at) >= datetime(?)
            AND datetime(c.completed_at) < datetime(?)
            GROUP BY t.category
        """, (user_id, week_start.isoformat(), week_end.isoformat())) as cursor:
            rows = await cursor.fetchall()
            by_category = {row['category']: row['count'] for row in rows}
        
        return {
            'total_scheduled': total_scheduled,
            'completed': completed,
            'completion_rate': (completed / total_scheduled * 100) if total_scheduled > 0 else 0,
            'by_category': by_category
        }

async def clear_schedule(user_id: int):
    """Jadvalni tozalash"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE schedule SET active = 0 WHERE user_id = ?", (user_id,))
        await db.commit()

async def delete_task(task_id: int):
    """Vazifani o'chirish"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE tasks SET active = 0 WHERE id = ?", (task_id,))
        await db.commit()

async def get_all_users() -> List[Dict]:
    """Barcha foydalanuvchilarni olish (Admin uchun)"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT user_id, username, full_name, created_at, timezone
            FROM users
            ORDER BY created_at DESC
        """) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

async def get_user_stats(user_id: int) -> Dict:
    """Foydalanuvchi statistikasi"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        # Jami vazifalar
        async with db.execute("""
            SELECT COUNT(*) as total FROM tasks WHERE user_id = ? AND active = 1
        """, (user_id,)) as cursor:
            row = await cursor.fetchone()
            total_tasks = row['total']
        
        # Bajarilgan vazifalar
        async with db.execute("""
            SELECT COUNT(*) as completed FROM completions WHERE user_id = ?
        """, (user_id,)) as cursor:
            row = await cursor.fetchone()
            completed = row['completed']
        
        return {
            'total_tasks': total_tasks,
            'completed': completed,
            'completion_rate': (completed / total_tasks * 100) if total_tasks > 0 else 0
        }

async def get_system_stats() -> Dict:
    """Tizim statistikasi (Admin uchun)"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        # Jami foydalanuvchilar
        async with db.execute("SELECT COUNT(*) as total FROM users") as cursor:
            row = await cursor.fetchone()
            total_users = row['total']
        
        # Jami vazifalar
        async with db.execute("SELECT COUNT(*) as total FROM tasks WHERE active = 1") as cursor:
            row = await cursor.fetchone()
            total_tasks = row['total']
        
        # Jami bajarilgan
        async with db.execute("SELECT COUNT(*) as total FROM completions") as cursor:
            row = await cursor.fetchone()
            total_completions = row['total']
        
        # Eng faol kategoriya
        async with db.execute("""
            SELECT category, COUNT(*) as count
            FROM tasks
            WHERE active = 1
            GROUP BY category
            ORDER BY count DESC
            LIMIT 1
        """) as cursor:
            row = await cursor.fetchone()
            top_category = dict(row) if row else {'category': 'N/A', 'count': 0}
        
        return {
            'total_users': total_users,
            'total_tasks': total_tasks,
            'total_completions': total_completions,
            'top_category': top_category
        }

async def get_user_settings(user_id: int) -> Dict:
    """Foydalanuvchi sozlamalarini olish"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT work_start_time, work_end_time, timezone
            FROM users
            WHERE user_id = ?
        """, (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return dict(row)
            return {
                'work_start_time': '08:00',
                'work_end_time': '16:00',
                'timezone': 'Asia/Tashkent'
            }

async def update_work_hours(user_id: int, start_time: str, end_time: str):
    """Foydalanuvchi ish vaqtini yangilash"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE users
            SET work_start_time = ?, work_end_time = ?
            WHERE user_id = ?
        """, (start_time, end_time, user_id))
        await db.commit()

async def migrate_existing_users():
    """Mavjud foydalanuvchilar uchun yangi ustunlarni qo'shish"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Ustunlar mavjudligini tekshirish
        async with db.execute("PRAGMA table_info(users)") as cursor:
            columns = await cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            # Agar yangi ustunlar yo'q bo'lsa, qo'shamiz
            if 'work_start_time' not in column_names:
                await db.execute("""
                    ALTER TABLE users ADD COLUMN work_start_time TEXT DEFAULT '08:00'
                """)
            
            if 'work_end_time' not in column_names:
                await db.execute("""
                    ALTER TABLE users ADD COLUMN work_end_time TEXT DEFAULT '16:00'
                """)
            
            await db.commit()

async def get_all_users() -> List[Dict]:
    """Barcha foydalanuvchilarni olish"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT user_id, username, full_name FROM users") as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

async def get_user_schedule_for_today(user_id: int, day_of_week: int) -> List[Dict]:
    """
    Foydalanuvchining bugungi jadvalini olish
    day_of_week: 0=Monday, 6=Sunday
    """
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT s.id, s.task_id, s.start_time, s.end_time, t.task_name
            FROM schedule s
            LEFT JOIN tasks t ON s.task_id = t.id
            WHERE s.user_id = ? AND s.day_of_week = ? AND s.active = 1
            ORDER BY s.start_time
        """, (user_id, day_of_week)) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
