import requests, os, random, json
from typing import Dict
from services.service import Service
from repos.repo import Repo
from constants import DB_NAME
from models.data_models import Car

repo = Repo(DB_NAME)     
service = Service(repo) 

async def get_cars() -> dict:
    return await service.get_all_cars()

async def update_car_by_name(car_id: str, car: Car) -> dict:
    return await service.update_car(car_id, car)
    
async def delete_car_by_name(car_id:str) -> dict:
    return await service.delete_car(car_id)

async def log_update(car_id:str,updated_by:str,changes:dict) -> dict:
    return await service.log_update_history(car_id,updated_by,changes)

async def get_last_updated_car() -> dict:
    """Get the car record that was last updated"""
    return await service.get_last_updated_car()

async def create_booking(customer_id: int, car_id: int, start_date: str, end_date: str, total_price: float) -> dict:
    """Create a new booking"""
    from models.data_models import Booking
    booking = Booking(
        customer_id=customer_id,
        car_id=car_id,
        start_date=start_date,
        end_date=end_date,
        total_price=total_price
    )
    return await service.create_booking(booking)

async def get_customer_with_most_rentals() -> dict:
    """Get the customer who has rented the most cars"""
    return await service.get_customer_with_most_rentals()

async def get_most_rented_model() -> dict:
    """Get the car model that is rented most often"""
    return await service.get_most_rented_model()

async def introduce_booking_model() -> dict:
    """Introduce and set up the Booking model with sample data"""
    try:
        # Initialize database with booking table
        await repo.init_db()
        
        # Add sample bookings if none exist
        existing_customer = await service.get_customer_with_most_rentals()
        if "No bookings found" in str(existing_customer):
            # Get available cars
            cars = await service.get_all_cars()
            if cars:
                # Create sample bookings
                sample_bookings = [
                    {"customer_id": 101, "car_id": cars[0].id, "start_date": "2024-01-01", "end_date": "2024-01-05", "total_price": 200.0},
                    {"customer_id": 102, "car_id": cars[0].id if len(cars) > 0 else 1, "start_date": "2024-01-10", "end_date": "2024-01-15", "total_price": 250.0},
                    {"customer_id": 101, "car_id": cars[1].id if len(cars) > 1 else 1, "start_date": "2024-01-20", "end_date": "2024-01-25", "total_price": 300.0}
                ]
                
                for booking_data in sample_bookings:
                    await create_booking(**booking_data)
        
        return {
            "message": "Booking model introduced successfully!",
            "model_structure": {
                "booking_id": "Primary key (auto-generated)",
                "customer_id": "Integer - Customer identifier",
                "car_id": "Integer - Car identifier", 
                "start_date": "String - Rental start date",
                "end_date": "String - Rental end date",
                "total_price": "Float - Total rental price"
            },
            "status": "Ready for analytics queries"
        }
    except Exception as e:
        return {"error": f"Failed to introduce booking model: {str(e)}"}