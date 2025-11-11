import requests, os, random, json
from typing import Dict
from services.service import Service
from repos.repo import Repo
from constants import DB_NAME

repo = Repo(DB_NAME)     
service = Service(repo) 

async def get_cars() -> dict:
    return await service.get_all_cars()