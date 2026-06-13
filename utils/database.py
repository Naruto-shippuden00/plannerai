"""
Database utility functions
"""
import aiosqlite
import json
import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

DB_PATH = "data/productivity.db"
TASHKENT_TZ = ZoneInfo("Asia/Tashkent")

async def init_db():
    """Ma'lumotlar bazasini boshlash"""
    # Data papkasini yaratish
    import os
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/photos", exist_ok=True)
    os.makedirs("data/focus_photos", exist_ok=True)
    os.makedirs("data/charts", exist_ok=True)
    
    async with aiosqlite.connect(DB_PATH) as db:
        # Foydalanuvchilar jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                created_at TEXT NOT NULL,
                timezone TEXT DEFAULT 'Asia/Tashkent',
                work_start_time TEXT DEFAULT '08:00',
                work_end_time TEXT DEFAULT '16:00',
                notification_enabled INTEGER DEFAULT 1,
                motivation_enabled INTEGER DEFAULT 1,
                language TEXT DEFAULT 'uz'
            )
        """)
        
        # Index qo'shish
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_created 
            ON users(created_at)
        """)
        
        # Vazifalar jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                task_name TEXT NOT NULL,
                category TEXT NOT NULL,
                priority INTEGER DEFAULT 1,
                duration_minutes INTEGER DEFAULT 60,
                active INTEGER DEFAULT 1,
                completed INTEGER DEFAULT 0,
                completed_at TEXT,
                times_completed INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
            )
        """)
        
        # Index qo'shish
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_tasks_user 
            ON tasks(user_id, active)
        """)
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_tasks_completed 
            ON tasks(user_id, completed)
        """)
        
        # Jadval (schedule) jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS schedule (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                task_id INTEGER NOT NULL,
                day_of_week INTEGER NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                active INTEGER DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE,
                FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE
            )
        """)
        
        # Index qo'shish
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_schedule_user_day 
            ON schedule(user_id, day_of_week, active)
        """)
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_schedule_task 
            ON schedule(task_id)
        """)
        
        # Bajarilgan vazifalar jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS completions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                task_id INTEGER NOT NULL,
                scheduled_time TEXT NOT NULL,
                completed_at TEXT NOT NULL,
                photo_path TEXT,
                notes TEXT,
                focus_session_id INTEGER,
                rating INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE,
                FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE,
                FOREIGN KEY (focus_session_id) REFERENCES focus_sessions (id) ON DELETE SET NULL
            )
        """)
        
        # Index qo'shish
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_completions_user_date 
            ON completions(user_id, completed_at)
        """)
        
        # Focus sessions - vazifa davomida fokus seanslarini kuzatish
        await db.execute("""
            CREATE TABLE IF NOT EXISTS focus_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                task_id INTEGER NOT NULL,
                schedule_id INTEGER,
                session_start TEXT NOT NULL,
                session_end TEXT,
                planned_duration INTEGER NOT NULL,
                actual_duration INTEGER,
                photos_submitted INTEGER DEFAULT 0,
                status TEXT DEFAULT 'active',
                completed INTEGER DEFAULT 0,
                quality_score INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE,
                FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE,
                FOREIGN KEY (schedule_id) REFERENCES schedule (id) ON DELETE SET NULL
            )
        """)
        
        # Index qo'shish
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_focus_user_status 
            ON focus_sessions(user_id, status)
        """)
        
        # Focus photos - vazifa davomida yuborilgan rasmlar
        await db.execute("""
            CREATE TABLE IF NOT EXISTS focus_photos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                focus_session_id INTEGER NOT NULL,
                photo_path TEXT NOT NULL,
                submitted_at TEXT NOT NULL,
                verified INTEGER DEFAULT 0,
                ai_verified INTEGER DEFAULT 0,
                verification_score REAL DEFAULT 0.0,
                FOREIGN KEY (focus_session_id) REFERENCES focus_sessions (id) ON DELETE CASCADE
            )
        """)
        
        # Index qo'shish
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_focus_photos_session 
            ON focus_photos(focus_session_id)
        """)
        
        # Punishments - jazo tizimi
        await db.execute("""
            CREATE TABLE IF NOT EXISTS punishments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                task_id INTEGER,
                focus_session_id INTEGER,
                punishment_type TEXT NOT NULL,
                reason TEXT NOT NULL,
                applied_at TEXT NOT NULL,
                completed INTEGER DEFAULT 0,
                completed_at TEXT,
                severity TEXT DEFAULT 'medium',
                FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE,
                FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE SET NULL,
                FOREIGN KEY (focus_session_id) REFERENCES focus_sessions (id) ON DELETE SET NULL
            )
        """)
        
        # Index qo'shish
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_punishments_user_completed 
            ON punishments(user_id, completed)
        """)
        
        # Camera permissions - kamera ruxsatlari
        await db.execute("""
            CREATE TABLE IF NOT EXISTS camera_permissions (
                user_id INTEGER PRIMARY KEY,
                permission_granted INTEGER DEFAULT 0,
                granted_at TEXT,
                revoked_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
            )
        """)
        
        # Haftalik testlar jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS weekly_tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                week_start TEXT NOT NULL,
                category TEXT NOT NULL,
                test_data TEXT NOT NULL,
                score INTEGER DEFAULT 0,
                max_score INTEGER DEFAULT 100,
                completed_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
            )
        """)
        
        # Index qo'shish
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_weekly_tests_user 
            ON weekly_tests(user_id, week_start)
        """)
        
        # User statistics - foydalanuvchi statistikasi (cache)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS user_statistics (
                user_id INTEGER PRIMARY KEY,
                total_tasks INTEGER DEFAULT 0,
                completed_tasks INTEGER DEFAULT 0,
                total_focus_time INTEGER DEFAULT 0,
                streak_days INTEGER DEFAULT 0,
                last_activity TEXT,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
            )
        """)
        
        # Achievements - yutuqlar tizimi
        await db.execute("""
            CREATE TABLE IF NOT EXISTS achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                achievement_type TEXT NOT NULL,
                achievement_name TEXT NOT NULL,
                earned_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
            )
        """)
        
        # Index qo'shish
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_achievements_user 
            ON achievements(user_id)
        """)
        
        await db.commit()
    
    # Mavjud foydalanuvchilar uchun migration
    await migrate_existing_users()
    
    logger.info("✅ Database initialized successfully with all tables and indexes")

async def add_user(user_id: int, username: str, full_name: str):
    """Yangi foydalanuvchi qo'shish"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR IGNORE INTO users (user_id, username, full_name, created_at)
            VALUES (?, ?, ?, ?)
        """, (user_id, username, full_name, datetime.now(TASHKENT_TZ).isoformat()))
        await db.commit()

async def add_task(user_id: int, task_name: str, category: str, priority: int = 1, duration: int = 60):
    """Vazifa qo'shish"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO tasks (user_id, task_name, category, priority, duration_minutes, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, task_name, category, priority, duration, datetime.now(TASHKENT_TZ).isoformat()))
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
        """, (user_id, task_id, scheduled_time, datetime.now(TASHKENT_TZ).isoformat(), photo_path, notes))
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
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            # Users jadvali uchun ustunlar
            async with db.execute("PRAGMA table_info(users)") as cursor:
                columns = await cursor.fetchall()
                column_names = [col[1] for col in columns]
                
                migrations = []
                
                # Agar yangi ustunlar yo'q bo'lsa, qo'shamiz
                if 'work_start_time' not in column_names:
                    migrations.append("ALTER TABLE users ADD COLUMN work_start_time TEXT DEFAULT '08:00'")
                
                if 'work_end_time' not in column_names:
                    migrations.append("ALTER TABLE users ADD COLUMN work_end_time TEXT DEFAULT '16:00'")
                
                if 'notification_enabled' not in column_names:
                    migrations.append("ALTER TABLE users ADD COLUMN notification_enabled INTEGER DEFAULT 1")
                
                if 'motivation_enabled' not in column_names:
                    migrations.append("ALTER TABLE users ADD COLUMN motivation_enabled INTEGER DEFAULT 1")
                
                if 'language' not in column_names:
                    migrations.append("ALTER TABLE users ADD COLUMN language TEXT DEFAULT 'uz'")
                
                for migration in migrations:
                    await db.execute(migration)
                    logger.info(f"Migration executed: {migration}")
            
            # Tasks jadvali uchun ustunlar
            async with db.execute("PRAGMA table_info(tasks)") as cursor:
                columns = await cursor.fetchall()
                column_names = [col[1] for col in columns]
                
                migrations = []
                
                if 'completed' not in column_names:
                    migrations.append("ALTER TABLE tasks ADD COLUMN completed INTEGER DEFAULT 0")
                
                if 'completed_at' not in column_names:
                    migrations.append("ALTER TABLE tasks ADD COLUMN completed_at TEXT")
                
                if 'times_completed' not in column_names:
                    migrations.append("ALTER TABLE tasks ADD COLUMN times_completed INTEGER DEFAULT 0")
                
                for migration in migrations:
                    await db.execute(migration)
                    logger.info(f"Migration executed: {migration}")
            
            # Completions jadvali uchun ustunlar
            async with db.execute("PRAGMA table_info(completions)") as cursor:
                columns = await cursor.fetchall()
                column_names = [col[1] for col in columns]
                
                migrations = []
                
                if 'focus_session_id' not in column_names:
                    migrations.append("ALTER TABLE completions ADD COLUMN focus_session_id INTEGER")
                
                if 'rating' not in column_names:
                    migrations.append("ALTER TABLE completions ADD COLUMN rating INTEGER DEFAULT 0")
                
                for migration in migrations:
                    await db.execute(migration)
                    logger.info(f"Migration executed: {migration}")
            
            # Focus sessions uchun ustunlar
            async with db.execute("PRAGMA table_info(focus_sessions)") as cursor:
                columns = await cursor.fetchall()
                column_names = [col[1] for col in columns]
                
                migrations = []
                
                if 'quality_score' not in column_names:
                    migrations.append("ALTER TABLE focus_sessions ADD COLUMN quality_score INTEGER DEFAULT 0")
                
                for migration in migrations:
                    await db.execute(migration)
                    logger.info(f"Migration executed: {migration}")
            
            # Focus photos uchun ustunlar
            async with db.execute("PRAGMA table_info(focus_photos)") as cursor:
                columns = await cursor.fetchall()
                column_names = [col[1] for col in columns]
                
                migrations = []
                
                if 'ai_verified' not in column_names:
                    migrations.append("ALTER TABLE focus_photos ADD COLUMN ai_verified INTEGER DEFAULT 0")
                
                if 'verification_score' not in column_names:
                    migrations.append("ALTER TABLE focus_photos ADD COLUMN verification_score REAL DEFAULT 0.0")
                
                for migration in migrations:
                    await db.execute(migration)
                    logger.info(f"Migration executed: {migration}")
            
            # Punishments uchun ustunlar
            async with db.execute("PRAGMA table_info(punishments)") as cursor:
                columns = await cursor.fetchall()
                column_names = [col[1] for col in columns]
                
                migrations = []
                
                if 'completed_at' not in column_names:
                    migrations.append("ALTER TABLE punishments ADD COLUMN completed_at TEXT")
                
                if 'severity' not in column_names:
                    migrations.append("ALTER TABLE punishments ADD COLUMN severity TEXT DEFAULT 'medium'")
                
                for migration in migrations:
                    await db.execute(migration)
                    logger.info(f"Migration executed: {migration}")
            
            # Camera permissions uchun ustunlar
            async with db.execute("PRAGMA table_info(camera_permissions)") as cursor:
                columns = await cursor.fetchall()
                column_names = [col[1] for col in columns]
                
                migrations = []
                
                if 'revoked_at' not in column_names:
                    migrations.append("ALTER TABLE camera_permissions ADD COLUMN revoked_at TEXT")
                
                for migration in migrations:
                    await db.execute(migration)
                    logger.info(f"Migration executed: {migration}")
            
            # Weekly tests uchun ustunlar
            async with db.execute("PRAGMA table_info(weekly_tests)") as cursor:
                columns = await cursor.fetchall()
                column_names = [col[1] for col in columns]
                
                migrations = []
                
                if 'category' not in column_names:
                    migrations.append("ALTER TABLE weekly_tests ADD COLUMN category TEXT DEFAULT 'General'")
                
                if 'max_score' not in column_names:
                    migrations.append("ALTER TABLE weekly_tests ADD COLUMN max_score INTEGER DEFAULT 100")
                
                for migration in migrations:
                    await db.execute(migration)
                    logger.info(f"Migration executed: {migration}")
            
            await db.commit()
            logger.info("✅ Database migration completed successfully")
            
    except Exception as e:
        logger.error(f"❌ Database migration error: {e}", exc_info=True)

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
            SELECT s.id, s.task_id, s.start_time, s.end_time, t.task_name, t.category
            FROM schedule s
            LEFT JOIN tasks t ON s.task_id = t.id
            WHERE s.user_id = ? AND s.day_of_week = ? AND s.active = 1
            ORDER BY s.start_time
        """, (user_id, day_of_week)) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

# ============== FOCUS SESSION FUNCTIONS ==============

async def create_focus_session(user_id: int, task_id: int, schedule_id: int, planned_duration: int) -> int:
    """Yangi focus session yaratish"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO focus_sessions 
            (user_id, task_id, schedule_id, session_start, planned_duration, status)
            VALUES (?, ?, ?, ?, ?, 'active')
        """, (user_id, task_id, schedule_id, datetime.now(TASHKENT_TZ).isoformat(), planned_duration))
        await db.commit()
        return cursor.lastrowid

async def get_active_focus_session(user_id: int) -> Optional[Dict]:
    """
    Foydalanuvchining aktiv focus sessionini olish
    
    FIX: Task ma'lumotlarini xavfsiz olish
    """
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT fs.*, 
                   COALESCE(t.task_name, 'Unknown Task') as task_name, 
                   COALESCE(t.category, 'Unknown') as category
            FROM focus_sessions fs
            LEFT JOIN tasks t ON fs.task_id = t.id
            WHERE fs.user_id = ? AND fs.status = 'active'
            ORDER BY fs.session_start DESC
            LIMIT 1
        """, (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                result = dict(row)
                logger.debug(f"Active session found: user={user_id}, session={result.get('id')}, task={result.get('task_name')}")
                return result
            else:
                logger.debug(f"No active session for user {user_id}")
                return None

async def end_focus_session(session_id: int, completed: bool = True):
    """Focus sessionni yakunlash"""
    async with aiosqlite.connect(DB_PATH) as db:
        session_end = datetime.now(TASHKENT_TZ).isoformat()
        
        # Session boshlanish vaqtini olish
        async with db.execute(
            "SELECT session_start FROM focus_sessions WHERE id = ?", 
            (session_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                start_time = datetime.fromisoformat(row[0])
                # Agar timezone yo'q bo'lsa qo'shamiz
                if start_time.tzinfo is None:
                    start_time = start_time.replace(tzinfo=TASHKENT_TZ)
                
                end_time = datetime.now(TASHKENT_TZ)
                actual_duration = int((end_time - start_time).total_seconds() / 60)
                
                await db.execute("""
                    UPDATE focus_sessions 
                    SET session_end = ?, actual_duration = ?, status = 'completed', completed = ?
                    WHERE id = ?
                """, (session_end, actual_duration, 1 if completed else 0, session_id))
                await db.commit()

async def add_focus_photo(session_id: int, photo_path: str) -> int:
    """Focus session uchun rasm qo'shish"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO focus_photos (focus_session_id, photo_path, submitted_at)
            VALUES (?, ?, ?)
        """, (session_id, photo_path, datetime.now(TASHKENT_TZ).isoformat()))
        
        # Photos_submitted sonini oshirish
        await db.execute("""
            UPDATE focus_sessions 
            SET photos_submitted = photos_submitted + 1
            WHERE id = ?
        """, (session_id,))
        
        await db.commit()
        return cursor.lastrowid

async def get_focus_session_photos(session_id: int) -> List[Dict]:
    """Focus session rasmlari"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT * FROM focus_photos 
            WHERE focus_session_id = ?
            ORDER BY submitted_at
        """, (session_id,)) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

# ============== PUNISHMENT FUNCTIONS ==============

async def add_punishment(user_id: int, task_id: int, session_id: int, punishment_type: str, reason: str):
    """Jazo qo'shish"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO punishments 
            (user_id, task_id, focus_session_id, punishment_type, reason, applied_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, task_id, session_id, punishment_type, reason, datetime.now(TASHKENT_TZ).isoformat()))
        await db.commit()

async def get_user_punishments(user_id: int, completed: Optional[bool] = None) -> List[Dict]:
    """Foydalanuvchi jazolarini olish"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        query = """
            SELECT p.*, t.task_name
            FROM punishments p
            LEFT JOIN tasks t ON p.task_id = t.id
            WHERE p.user_id = ?
        """
        params = [user_id]
        
        if completed is not None:
            query += " AND p.completed = ?"
            params.append(1 if completed else 0)
        
        query += " ORDER BY p.applied_at DESC"
        
        async with db.execute(query, params) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

async def mark_punishment_completed(punishment_id: int):
    """Jazoni bajarilgan deb belgilash"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE punishments SET completed = 1 WHERE id = ?
        """, (punishment_id,))
        await db.commit()

# ============== CAMERA PERMISSION ==============

async def set_camera_permission(user_id: int, granted: bool):
    """Kamera ruxsatini saqlash"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR REPLACE INTO camera_permissions 
            (user_id, permission_granted, granted_at)
            VALUES (?, ?, ?)
        """, (user_id, 1 if granted else 0, datetime.now(TASHKENT_TZ).isoformat()))
        await db.commit()

async def get_camera_permission(user_id: int) -> bool:
    """Kamera ruxsatini tekshirish"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT permission_granted FROM camera_permissions WHERE user_id = ?
        """, (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] == 1 if row else False

# ============== TASK COMPLETION UPDATE ==============

async def mark_task_as_completed(task_id: int):
    """Vazifani bajarilgan deb belgilash (o'chirmasdan)"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE tasks 
            SET completed = 1, completed_at = ?, times_completed = times_completed + 1
            WHERE id = ?
        """, (datetime.now(TASHKENT_TZ).isoformat(), task_id))
        await db.commit()

async def unmark_task_completion(task_id: int):
    """Vazifani qayta faol qilish"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE tasks 
            SET completed = 0, completed_at = NULL
            WHERE id = ?
        """, (task_id,))
        await db.commit()

async def get_completed_tasks(user_id: int) -> List[Dict]:
    """Bajarilgan vazifalarni olish"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT * FROM tasks 
            WHERE user_id = ? AND completed = 1 AND active = 1
            ORDER BY completed_at DESC
        """, (user_id,)) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

async def delete_task_by_name(user_id: int, task_name: str) -> bool:
    """Vazifani nomi bo'yicha o'chirish"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            UPDATE tasks 
            SET active = 0
            WHERE user_id = ? AND LOWER(task_name) LIKE LOWER(?) AND active = 1
        """, (user_id, f"%{task_name}%"))
        await db.commit()
        return cursor.rowcount > 0

async def get_task_by_name(user_id: int, task_name: str) -> Optional[Dict]:
    """Vazifani nomi bo'yicha topish"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT * FROM tasks 
            WHERE user_id = ? AND LOWER(task_name) LIKE LOWER(?) AND active = 1
            LIMIT 1
        """, (user_id, f"%{task_name}%")) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

async def get_task_by_id(task_id: int) -> Optional[Dict]:
    """Vazifani ID bo'yicha topish"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT * FROM tasks WHERE id = ?
        """, (task_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

# ============== ACHIEVEMENTS & STATISTICS ==============

async def add_achievement(user_id: int, achievement_type: str, achievement_name: str):
    """Yutuq qo'shish"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Oldin bor-yo'qligini tekshirish
        async with db.execute("""
            SELECT id FROM achievements 
            WHERE user_id = ? AND achievement_type = ?
        """, (user_id, achievement_type)) as cursor:
            existing = await cursor.fetchone()
        
        if not existing:
            await db.execute("""
                INSERT INTO achievements (user_id, achievement_type, achievement_name, earned_at)
                VALUES (?, ?, ?, ?)
            """, (user_id, achievement_type, achievement_name, datetime.now(TASHKENT_TZ).isoformat()))
            await db.commit()
            logger.info(f"Achievement '{achievement_name}' added for user {user_id}")
            return True
        return False

async def get_user_achievements(user_id: int) -> List[Dict]:
    """Foydalanuvchi yutuqlarini olish"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT * FROM achievements 
            WHERE user_id = ?
            ORDER BY earned_at DESC
        """, (user_id,)) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

async def update_user_statistics(user_id: int):
    """Foydalanuvchi statistikasini yangilash (cache)"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Total tasks
        async with db.execute("""
            SELECT COUNT(*) as total FROM tasks WHERE user_id = ? AND active = 1
        """, (user_id,)) as cursor:
            row = await cursor.fetchone()
            total_tasks = row[0] if row else 0
        
        # Completed tasks
        async with db.execute("""
            SELECT COUNT(*) as completed FROM completions WHERE user_id = ?
        """, (user_id,)) as cursor:
            row = await cursor.fetchone()
            completed_tasks = row[0] if row else 0
        
        # Total focus time
        async with db.execute("""
            SELECT SUM(actual_duration) as total_time 
            FROM focus_sessions 
            WHERE user_id = ? AND completed = 1
        """, (user_id,)) as cursor:
            row = await cursor.fetchone()
            total_focus_time = row[0] if row and row[0] else 0
        
        # Streak calculation (kunlar ketma-ket)
        # Bu murakkab - keyingi versiyada qo'shamiz
        streak_days = 0
        
        # Update or insert
        await db.execute("""
            INSERT OR REPLACE INTO user_statistics 
            (user_id, total_tasks, completed_tasks, total_focus_time, streak_days, last_activity, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, total_tasks, completed_tasks, total_focus_time, streak_days, 
              datetime.now(TASHKENT_TZ).isoformat(), datetime.now(TASHKENT_TZ).isoformat()))
        await db.commit()

async def get_user_statistics_cached(user_id: int) -> Dict:
    """Cache'dan statistika olish"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT * FROM user_statistics WHERE user_id = ?
        """, (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return dict(row)
            else:
                # Agar yo'q bo'lsa, hozir hisoblash
                await update_user_statistics(user_id)
                # Qayta olish
                async with db.execute("""
                    SELECT * FROM user_statistics WHERE user_id = ?
                """, (user_id,)) as cursor2:
                    row2 = await cursor2.fetchone()
                    return dict(row2) if row2 else {}
