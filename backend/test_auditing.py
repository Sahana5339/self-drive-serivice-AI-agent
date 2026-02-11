#!/usr/bin/env python3
"""
Test script to demonstrate the auditing functionality
"""
import asyncio
import aiosqlite
from models.data_models import Car
from repos.repo import Repo
from services.service import Service
from constants import DB_NAME

async def setup_test_data():
    """Setup test data and demonstrate auditing"""
    repo = Repo(DB_NAME)
    service = Service(repo)
    
    # Initialize database
    await repo.init_db()
    
    # Add a test car
    test_car = Car(
        company="Toyota",
        model="Camry",
        kms=50000,
        year=2020,
        color="Blue",
        available=True
    )
    
    try:
        await service.create_car(test_car)
        print("✅ Test car created successfully")
    except Exception as e:
        print(f"Car might already exist: {e}")
    
    # Get all cars to find the ID
    cars = await service.get_all_cars()
    if cars:
        car_id = str(cars[0].id)
        print(f"📋 Found car with ID: {car_id}")
        
        # Update the car to create audit history
        updated_car = Car(
            company="Toyota",
            model="Camry",
            kms=55000,  # Changed
            year=2020,
            color="Red",  # Changed
            available=False  # Changed
        )
        
        await service.update_car(car_id, updated_car)
        print("✅ Car updated successfully - audit log should be created")
        
        # Test the auditing functionality
        result = await service.get_last_updated_car()
        print("\n🔍 Last Updated Car Audit Result:")
        print("=" * 50)
        
        if "message" in result and "No update history" in result["message"]:
            print("❌ No update history found")
        else:
            car_info = result.get("car", {})
            update_info = result.get("last_update", {})
            
            print(f"Car ID: {car_info.get('id')}")
            print(f"Company: {car_info.get('company')}")
            print(f"Model: {car_info.get('model')}")
            print(f"KMs: {car_info.get('kms')}")
            print(f"Year: {car_info.get('year')}")
            print(f"Color: {car_info.get('color')}")
            print(f"Available: {car_info.get('available')}")
            print("\nLast Update Details:")
            print(f"Field Changed: {update_info.get('field_changed')}")
            print(f"Old Value: {update_info.get('old_value')}")
            print(f"New Value: {update_info.get('new_value')}")
            print(f"Updated By: {update_info.get('updated_by')}")
            print(f"Timestamp: {update_info.get('timestamp')}")
    else:
        print("❌ No cars found in database")

if __name__ == "__main__":
    asyncio.run(setup_test_data())