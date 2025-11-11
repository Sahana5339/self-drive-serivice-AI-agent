from fastapi import APIRouter, status, Body
from typing import List
from models.data_models import Car
from services.service import Service
from repos.repo import Repo
from constants import DB_NAME
import logging

router = APIRouter()
repo = Repo(DB_NAME)
service = Service(repo)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_car(car: Car = Body(...)):
    """Create a new car record"""
    return await service.create_car(car)

@router.put("/{car_id}", status_code=status.HTTP_200_OK)
async def update_car(car_id: str, car: Car):
    """Update an existing car record"""
    return await service.update_car(car_id, car)

@router.delete("/{car_id}", status_code=status.HTTP_200_OK)
async def delete_car(car_id: str):
    """Delete a car record"""
    return await service.delete_car(car_id)

@router.get("/", response_model=List[Car])
async def get_all_cars():
    """Retrieve all cars"""
    return await service.get_all_cars()
