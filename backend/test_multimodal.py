#!/usr/bin/env python3
"""
Test script for multi-modal functionality with bookings
"""
import asyncio
from models.data_models import Car, Booking
from repos.repo import Repo
from services.service import Service
from constants import DB_NAME

async def setup_multimodal_data():
    """Setup test data for multi-modal functionality"""
    repo = Repo(DB_NAME)
    service = Service(repo)
    
    await repo.init_db()
    
    # Add test cars
    cars = [
        Car(company="Toyota", model="Camry", kms=50000, year=2020, color="Blue", available=True),
        Car(company="Honda", model="Civic", kms=30000, year=2021, color="Red", available=True),
        Car(company="Toyota", model="Corolla", kms=25000, year=2022, color="White", available=True)
    ]
    
    for car in cars:
        try:
            await service.create_car(car)
            print(f"✅ Created car: {car.company} {car.model}")
        except:
            print(f"Car {car.company} {car.model} already exists")
    
    # Get car IDs
    all_cars = await service.get_all_cars()
    car_ids = [car.id for car in all_cars]
    
    # Add test bookings
    bookings = [
        Booking(customer_id=101, car_id=car_ids[0], start_date="2024-01-01", end_date="2024-01-05", total_price=200.0),
        Booking(customer_id=102, car_id=car_ids[1], start_date="2024-01-10", end_date="2024-01-15", total_price=250.0),
        Booking(customer_id=101, car_id=car_ids[2], start_date="2024-01-20", end_date="2024-01-25", total_price=300.0),
        Booking(customer_id=103, car_id=car_ids[0], start_date="2024-02-01", end_date="2024-02-05", total_price=200.0),
        Booking(customer_id=101, car_id=car_ids[0], start_date="2024-02-10", end_date="2024-02-15", total_price=250.0)
    ]
    
    for booking in bookings:
        await service.create_booking(booking)
        print(f"✅ Created booking: Customer {booking.customer_id} -> Car {booking.car_id}")
    
    # Test analytics
    print("\n🔍 Multi-modal Analytics:")
    print("=" * 40)
    
    most_rentals = await service.get_customer_with_most_rentals()
    print(f"Customer with most rentals: {most_rentals}")
    
    most_rented_model = await service.get_most_rented_model()
    print(f"Most rented model: {most_rented_model}")
    
    print("\n✅ Multi-modal setup complete!")
    print("You can now ask:")
    print("- 'Which customer has rented the most cars?'")
    print("- 'Which model is rented most often?'")

if __name__ == "__main__":
    asyncio.run(setup_multimodal_data())