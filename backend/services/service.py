from typing import List
from fastapi import HTTPException
from models.data_models import Car, Booking
from repos.repo import Repo
from models.update_history import UpdateHistory
from datetime import datetime

class Repo:
    def __init__(self, session):
        self.session = session

    async def init_db(self):
        # Optional: initialize or verify DB connection
        pass

    # Other methods: get, insert, update, delete, list...

    async def add_update_log(self, car_id: str, updated_by: str, changes: dict) -> bool:
        try:
            for field, (old_value, new_value) in changes.items():
                log_entry = UpdateHistory(
                    car_id=car_id,
                    field=field,
                    old_value=str(old_value),
                    new_value=str(new_value),
                    updated_by=updated_by,
                    timestamp=datetime.utcnow()
                )
                self.session.add(log_entry)
            await self.session.commit()
            return True
        except Exception as e:
            await self.session.rollback()
            print(f"Error logging update history: {e}")
            return False

class Service:
    def __init__(self, repo: Repo):
        self.repo = repo

    async def create_car(self, car: Car):
        await self.repo.init_db()
        if isinstance(car, dict):
            car = Car(**car)
        existing = await self.repo.get(car.id)
        if existing:
            raise HTTPException(status_code=409, detail="Car already exists")
        await self.repo.insert(car)
        return car

    async def get_all_cars(self) -> List[Car]:
        await self.repo.init_db()
        return await self.repo.list()

    async def update_car(self, car_id: str, car: Car) -> Car:
        await self.repo.init_db()
        if isinstance(car, dict):
            car = Car(**car)
        
        # Get the old car data before updating
        old_car = await self.repo.get(car_id)
        if not old_car:
            raise HTTPException(status_code=404, detail="Car not found to update")
        
        car.id = car_id  
        updated = await self.repo.update(car)
        if not updated:
            raise HTTPException(status_code=404, detail="Car not found to update")
        
        # Log the changes automatically
        changes = {}
        if old_car.company != car.company:
            changes['company'] = (old_car.company, car.company)
        if old_car.model != car.model:
            changes['model'] = (old_car.model, car.model)
        if old_car.kms != car.kms:
            changes['kms'] = (old_car.kms, car.kms)
        if old_car.year != car.year:
            changes['year'] = (old_car.year, car.year)
        if old_car.color != car.color:
            changes['color'] = (old_car.color, car.color)
        if old_car.available != car.available:
            changes['available'] = (old_car.available, car.available)
        
        if changes:
            await self.repo.add_update_log(car_id, "system", changes)
        
        return car

    async def delete_car(self, car_id: str):
        await self.repo.init_db()
        deleted_count = await self.repo.delete(car_id)
        if deleted_count == 0:
            raise HTTPException(status_code=404, detail="Car not found to delete")
        return {"message": f"Car with id {car_id} deleted successfully"}

    async def log_update_history(self, car_id: str, updated_by: str, changes: dict):
        await self.repo.init_db()
        success = await self.repo.add_update_log(
            car_id=car_id,
            updated_by=updated_by,
            changes=changes
        )
        if not success:
            raise HTTPException(status_code=500, detail="Failed to log update history")
        return {"message": f"Update history logged for car {car_id}"}

    async def get_last_updated_car(self):
        """Get the car record that was last updated with update details"""
        await self.repo.init_db()
        return await self.repo.get_last_updated_car()

    async def create_booking(self, booking: Booking):
        await self.repo.init_db()
        if isinstance(booking, dict):
            booking = Booking(**booking)
        await self.repo.insert_booking(booking)
        return booking

    async def get_customer_with_most_rentals(self):
        await self.repo.init_db()
        return await self.repo.get_customer_with_most_rentals()

    async def get_most_rented_model(self):
        await self.repo.init_db()
        return await self.repo.get_most_rented_model()
    
    async def get_all_bookings(self) -> List[Booking]:
        await self.repo.init_db()
        return await self.repo.list_bookings()
