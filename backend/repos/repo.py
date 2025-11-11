import aiosqlite
from typing import List, Optional
from models.data_models import Car
from constants import DB_NAME, TABLE_NAME

class Repo:
    def __init__(self, db_path: str = DB_NAME):
        self.db_path = db_path

    async def init_db(self):
        """Initialize table if not exists."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(f"""
                CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        company VARCHAR(100),
                        model VARCHAR(100),
                        kms INTEGER,
                        year INTEGER,
                        color VARCHAR(100),
                        available BOOLEAN
                    )
            """)
            await db.commit()

    async def insert(self, car: Car):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(f"""
                INSERT INTO {TABLE_NAME} (company, model, kms, year, color, available)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                car.company,
                car.model,
                car.kms,
                car.year,
                car.color,
                car.available
            ))
            await db.commit()

    async def get(self, car_id: str) -> Optional[Car]:
        query = f"""
            SELECT id, company, model, kms, year, color, available
            FROM {TABLE_NAME} WHERE id = ?
        """
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(query, (car_id,))
            row = await cursor.fetchone()
            if row:
                return Car(
                    id=row[0],
                    company=row[1],
                    model=row[2],
                    kms=row[3],
                    year=row[4],
                    color=row[5],
                    available=row[6]
                )
            return None


    async def list(self) -> List[Car]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(f"SELECT id, company, model, kms, year, color, available FROM {TABLE_NAME}")
            rows = await cursor.fetchall()
            return [
                Car(
                    id=row[0],
                    company=row[1],
                    model=row[2],
                    kms=row[3],
                    year=row[4],
                    color=row[5],
                    available=row[6]
                )
                for row in rows
            ]


    async def delete(self, car_id: str) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(f"DELETE FROM {TABLE_NAME} WHERE id = ?", (car_id,))
            await db.commit()
            return cursor.rowcount

    async def update(self, car: Car) -> bool:
        async with aiosqlite.connect(self.db_path) as db:              
            cursor = await db.execute(f"""
                UPDATE {TABLE_NAME}
                SET company = ?, model = ?, kms = ?, year = ?, color = ?, available = ?
                WHERE id = ?
            """, (
                car.company,
                car.model,
                car.kms,
                car.year,
                car.color,
                car.available,
                car.id
            ))
            await db.commit()
            return cursor.rowcount > 0
