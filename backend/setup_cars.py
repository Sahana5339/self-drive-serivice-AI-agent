#!/usr/bin/env python3
import asyncio
from models.data_models import Car
from repos.repo import Repo
from services.service import Service
from constants import DB_NAME

async def setup_cars():
    repo = Repo(DB_NAME)
    service = Service(repo)
    
    await repo.init_db()
    
    cars = [
        Car(company="Toyota", model="Camry", kms=50000, year=2020, color="Blue", available=True),
        Car(company="Honda", model="Civic", kms=30000, year=2021, color="Red", available=True),
        Car(company="Toyota", model="Corolla", kms=25000, year=2022, color="White", available=True)
    ]
    
    for car in cars:
        try:
            await service.create_car(car)
            print(f"✅ Added: {car.company} {car.model}")
        except:
            print(f"Car {car.company} {car.model} already exists")
    
    print("✅ Cars setup complete!")

if __name__ == "__main__":
    asyncio.run(setup_cars())