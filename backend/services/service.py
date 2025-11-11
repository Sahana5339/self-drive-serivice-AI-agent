from typing import List
from fastapi import HTTPException
from models.data_models import Car
from repos.repo import Repo

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
        car.id = car_id  
        updated = await self.repo.update(car)
        if not updated:
            raise HTTPException(status_code=404, detail="Car not found to update")
        return car

    async def delete_car(self, car_id: str):
        await self.repo.init_db()
        deleted_count = await self.repo.delete(car_id)
        if deleted_count == 0:
            raise HTTPException(status_code=404, detail="Car not found to delete")
        return {"message": f"Car with id {car_id} deleted successfully"}
