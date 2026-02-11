import aiosqlite
from typing import List, Optional
from models.data_models import Car, Booking
from constants import DB_NAME, TABLE_NAME
from datetime import datetime

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
            await db.execute("""
                CREATE TABLE IF NOT EXISTS update_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                car_id INTEGER,
                field TEXT,
                old_value TEXT,
                new_value TEXT,
                updated_by TEXT,
                timestamp TEXT
                    )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS bookings (
                booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                car_id INTEGER,
                start_date TEXT,
                end_date TEXT,
                total_price REAL
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
    

    async def add_update_log(self, car_id: str, updated_by: str, changes: dict) -> bool:
        try:
            async with aiosqlite.connect(self.db_path) as db:
                for field, (old_value, new_value) in changes.items():
                    await db.execute("""
                        INSERT INTO update_history (car_id, field, old_value, new_value, updated_by, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        car_id,
                        field,
                        str(old_value),
                        str(new_value),
                        updated_by,
                        datetime.utcnow().isoformat()
                    ))
                await db.commit()
            return True
        except Exception as e:
            print(f"Error logging update history: {e}")
            return False

    async def get_last_updated_car(self) -> dict:
        """Get the car record that was last updated with update details"""
        async with aiosqlite.connect(self.db_path) as db:
            # Get the most recent update from history
            cursor = await db.execute("""
                SELECT car_id, field, old_value, new_value, updated_by, timestamp
                FROM update_history 
                ORDER BY timestamp DESC 
                LIMIT 1
            """)
            update_row = await cursor.fetchone()
            
            if not update_row:
                return {"message": "No update history found"}
            
            car_id, field, old_value, new_value, updated_by, timestamp = update_row
            
            # Get the current car details
            car = await self.get(car_id)
            if not car:
                return {"message": f"Car with ID {car_id} not found"}
            
            return {
                "car": {
                    "id": car.id,
                    "company": car.company,
                    "model": car.model,
                    "kms": car.kms,
                    "year": car.year,
                    "color": car.color,
                    "available": car.available
                },
                "last_update": {
                    "field_changed": field,
                    "old_value": old_value,
                    "new_value": new_value,
                    "updated_by": updated_by,
                    "timestamp": timestamp
                }
            }

    async def insert_booking(self, booking: Booking):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO bookings (customer_id, car_id, start_date, end_date, total_price)
                VALUES (?, ?, ?, ?, ?)
            """, (
                booking.customer_id,
                booking.car_id,
                booking.start_date,
                booking.end_date,
                booking.total_price
            ))
            await db.commit()

    async def get_customer_with_most_rentals(self) -> dict:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT customer_id, COUNT(*) as rental_count
                FROM bookings 
                GROUP BY customer_id 
                ORDER BY rental_count DESC 
                LIMIT 1
            """)
            row = await cursor.fetchone()
            if row:
                return {"customer_id": row[0], "rental_count": row[1]}
            return {"message": "No bookings found"}

    async def get_most_rented_model(self) -> dict:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(f"""
                SELECT c.model, COUNT(*) as rental_count
                FROM bookings b
                JOIN {TABLE_NAME} c ON b.car_id = c.id
                GROUP BY c.model 
                ORDER BY rental_count DESC 
                LIMIT 1
            """)
            row = await cursor.fetchone()
            if row:
                return {"model": row[0], "rental_count": row[1]}
            return {"message": "No bookings found"}
    
    async def list_bookings(self) -> List[Booking]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT booking_id, customer_id, car_id, start_date, end_date, total_price FROM bookings")
            rows = await cursor.fetchall()
            return [
                Booking(
                    booking_id=row[0],
                    customer_id=row[1],
                    car_id=row[2],
                    start_date=row[3],
                    end_date=row[4],
                    total_price=row[5]
                )
                for row in rows
            ]
