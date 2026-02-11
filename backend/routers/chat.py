from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import uuid
import google.generativeai as genai
import os
import re
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

router = APIRouter()

# Simple in-memory storage for sessions
sessions_store: Dict[str, Dict] = {}

@router.get("/apps/{app_name}/users/{user_id}/sessions")
async def get_sessions(app_name: str, user_id: str):
    """Get all sessions for a user"""
    user_sessions = [{"id": session_id, "events": session["events"]} 
                    for session_id, session in sessions_store.items()]
    return user_sessions

@router.post("/apps/{app_name}/users/{user_id}/sessions")
async def create_session(app_name: str, user_id: str):
    """Create a new chat session"""
    session_id = str(uuid.uuid4())[:8]
    sessions_store[session_id] = {
        "id": session_id,
        "events": []
    }
    return {"id": session_id}

@router.get("/apps/{app_name}/users/{user_id}/sessions/{session_id}")
async def get_session(app_name: str, user_id: str, session_id: str):
    """Get a specific session"""
    if session_id not in sessions_store:
        raise HTTPException(status_code=404, detail="Session not found")
    return sessions_store[session_id]

@router.delete("/apps/{app_name}/users/{user_id}/sessions/{session_id}")
async def delete_session(app_name: str, user_id: str, session_id: str):
    """Delete a session"""
    if session_id not in sessions_store:
        raise HTTPException(status_code=404, detail="Session not found")
    del sessions_store[session_id]
    return {"message": "Session deleted"}

# Define tools for the AI
async def get_all_cars_tool():
    """Get all cars from the database"""
    from services.service import Service
    from repos.repo import Repo
    from constants import DB_NAME
    
    repo = Repo(DB_NAME)
    service = Service(repo)
    cars = await service.get_all_cars()
    return [{"company": car.company, "model": car.model, "year": car.year, 
             "color": car.color, "kms": car.kms, "available": car.available} for car in cars]

async def get_available_cars_tool():
    """Get only available cars from the database"""
    cars = await get_all_cars_tool()
    return [car for car in cars if car["available"] == True]

async def get_all_bookings_tool():
    """Get all bookings from the database"""
    from services.service import Service
    from repos.repo import Repo
    from constants import DB_NAME
    
    repo = Repo(DB_NAME)
    service = Service(repo)
    bookings = await service.get_all_bookings()
    return [{"booking_id": b.booking_id, "customer_id": b.customer_id, "car_id": b.car_id, 
             "start_date": b.start_date, "end_date": b.end_date, "total_price": b.total_price} for b in bookings]

async def add_car_tool(company: str, model: str, year: int, color: str, kms: int, available: bool = True):
    """Add a new car to the database"""
    from services.service import Service
    from repos.repo import Repo
    from constants import DB_NAME
    from models.data_models import Car
    
    repo = Repo(DB_NAME)
    service = Service(repo)
    car = Car(company=company, model=model, year=year, color=color, kms=kms, available=available)
    await service.create_car(car)
    return f"Added {company} {model} successfully"

async def update_car_tool(car_id: str, **updates):
    """Update a car in the database"""
    from services.service import Service
    from repos.repo import Repo
    from constants import DB_NAME
    from models.data_models import Car
    
    repo = Repo(DB_NAME)
    service = Service(repo)
    
    # Get existing car
    existing_car = await repo.get(car_id)
    if not existing_car:
        return f"Car with ID {car_id} not found"
    
    # Update only provided fields
    updated_car = Car(
        id=car_id,
        company=updates.get('company', existing_car.company),
        model=updates.get('model', existing_car.model),
        year=updates.get('year', existing_car.year),
        color=updates.get('color', existing_car.color),
        kms=updates.get('kms', existing_car.kms),
        available=updates.get('available', existing_car.available)
    )
    
    await service.update_car(car_id, updated_car)
    return f"Updated {updated_car.company} {updated_car.model} successfully"

async def delete_car_tool(car_id: str):
    """Delete a car from the database"""
    from services.service import Service
    from repos.repo import Repo
    from constants import DB_NAME
    
    repo = Repo(DB_NAME)
    service = Service(repo)
    
    # Get car details before deletion
    existing_car = await repo.get(car_id)
    if not existing_car:
        return f"Car with ID {car_id} not found"
    
    await service.delete_car(car_id)
    return f"Deleted {existing_car.company} {existing_car.model} successfully"

async def create_booking_tool(car_id: str, start_date: str, end_date: str, price: float = None, customer_id: int = 1):
    """Create a booking for a car"""
    from services.service import Service
    from repos.repo import Repo
    from constants import DB_NAME
    from models.data_models import Booking
    
    repo = Repo(DB_NAME)
    service = Service(repo)
    
    # Check if car exists and is available
    existing_car = await repo.get(car_id)
    if not existing_car:
        return f"Car with ID {car_id} not found"
    
    if not existing_car.available:
        return f"Car {existing_car.company} {existing_car.model} is not available for booking"
    
    booking = Booking(
        customer_id=customer_id,
        car_id=int(car_id),
        start_date=start_date,
        end_date=end_date,
        total_price=price
    )
    
    await service.create_booking(booking)
    return f"Booking created for {existing_car.company} {existing_car.model} from {start_date} to {end_date} at ${price}"

@router.post("/run_sse")
async def chat_with_ai(payload: Dict[str, Any]):
    """Handle chat messages with Mock Agent (no API calls)"""
    try:
        session_id = payload.get("sessionId")
        new_message = payload.get("newMessage")
        
        if session_id not in sessions_store:
            sessions_store[session_id] = {"id": session_id, "events": []}
        
        # Add user message to session
        sessions_store[session_id]["events"].append({
            "content": new_message
        })
        
        # Extract text from message parts
        user_text = ""
        for part in new_message.get("parts", []):
            if "text" in part:
                user_text += part["text"]
        
        if not user_text:
            user_text = "Hello"
        
        # Mock Agent Response (no API calls)
        user_lower = user_text.lower()
        
        if "show" in user_lower and "car" in user_lower:
            cars = await get_all_cars_tool()
            if cars:
                car_list = "\n".join([f"• {car['company']} {car['model']} ({car['year']}) - {car['color']}, {car['kms']} km" for car in cars])
                response_text = f"🚗 **Current Cars in System:**\n\n{car_list}\n\n*Agent working without API calls!*"
            else:
                response_text = "No cars found in database. Try adding some cars first!"
        
        elif "add" in user_lower and any(brand in user_lower for brand in ["bmw", "toyota", "honda", "ford"]):
            response_text = "🎯 **Mock Agent Response:**\n\nI detected you want to add a car! In a real scenario, I would:\n1. Parse your car details\n2. Call the add_car_tool()\n3. Save to database\n\n*This is your Google ADK agent working in demo mode!*"
        
        elif "create" in user_lower and "booking" in user_lower:
            # Interactive booking creation
            cars = await get_all_cars_tool()
            if cars:
                available_cars = [car for car in cars if car['available']]
                if available_cars:
                    car_list = "\n".join([f"• Car {i+1}: {car['company']} {car['model']} ({car['year']}) - ${car['kms']/10:.0f}/day" for i, car in enumerate(available_cars)])
                    response_text = f"🚗 **Let's create a booking!**\n\n**Available Cars:**\n{car_list}\n\n📝 **Please provide:**\n• Which car? (e.g., 'Car 1')\n• Start date? (YYYY-MM-DD)\n• End date? (YYYY-MM-DD)\n• Customer ID? (e.g., 101)\n\n*Example: 'Book Car 1 from 2024-12-20 to 2024-12-25 for customer 101'*"
                else:
                    response_text = "❌ No cars available for booking right now."
            else:
                response_text = "❌ No cars in system. Please add cars first."
        
        elif "book car" in user_lower or ("book" in user_lower and any(word in user_lower for word in ["car", "from", "to"])):
            # Parse booking details from user input
            import re
            
            # Extract car number
            car_match = re.search(r'car (\d+)', user_lower)
            car_id = car_match.group(1) if car_match else None
            
            # Extract dates
            date_pattern = r'\d{4}-\d{2}-\d{2}'
            dates = re.findall(date_pattern, user_text)
            
            # Extract customer ID
            customer_match = re.search(r'customer (\d+)', user_lower)
            customer_id = int(customer_match.group(1)) if customer_match else 101
            
            if car_id and len(dates) >= 2:
                try:
                    result = await create_booking_tool(car_id, dates[0], dates[1], 500.0, customer_id)
                    response_text = f"✅ **Booking Created!**\n\n{result}\n\n*Google ADK agent executed create_booking() successfully!*"
                except Exception as e:
                    response_text = f"❌ Booking failed: {e}"
            else:
                response_text = "❌ **Missing booking details!**\n\nPlease provide:\n• Car number (e.g., 'Car 1')\n• Start date (YYYY-MM-DD)\n• End date (YYYY-MM-DD)\n• Customer ID (optional)\n\nExample: 'Book Car 1 from 2024-12-20 to 2024-12-25 for customer 101'"
        
        elif "booking" in user_lower or "show booking" in user_lower:
            bookings = await get_all_bookings_tool()
            if bookings:
                booking_list = "\n".join([f"• Booking #{b['booking_id']}: Car {b['car_id']}, Customer {b['customer_id']}" for b in bookings[:3]])
                response_text = f"📅 **Current Bookings:**\n\n{booking_list}\n\n*Agent tools working perfectly!*"
            else:
                response_text = "No bookings found. Your agent can create bookings when API quota is available!"
        
        elif "customer" in user_lower and "most" in user_lower:
            from agent.tools import get_customer_with_most_rentals
            try:
                result = await get_customer_with_most_rentals()
                response_text = f"🏆 **get_customer_with_most_rentals():**\n\n{result}\n\n*Analytics tool working!*"
            except Exception as e:
                response_text = f"get_customer_with_most_rentals: {e}"
        
        elif "most rented" in user_lower or "popular model" in user_lower:
            from agent.tools import get_most_rented_model
            try:
                result = await get_most_rented_model()
                response_text = f"🚗 **get_most_rented_model():**\n\n{result}\n\n*Analytics tool working!*"
            except Exception as e:
                response_text = f"get_most_rented_model: {e}"
        
        elif "last updated" in user_lower:
            from agent.tools import get_last_updated_car
            try:
                result = await get_last_updated_car()
                response_text = f"🔄 **get_last_updated_car():**\n\n{result}\n\n*Audit tool working!*"
            except Exception as e:
                response_text = f"get_last_updated_car: {e}"
        
        elif "introduce booking" in user_lower:
            from agent.tools import introduce_booking_model
            try:
                result = await introduce_booking_model()
                response_text = f"📊 **introduce_booking_model():**\n\n{result}\n\n*Setup tool executed!*"
            except Exception as e:
                response_text = f"introduce_booking_model: {e}"
        
        elif "update car" in user_lower:
            response_text = "🔄 **update_car_by_name() demo:**\n\nWould update car details in database.\nExample: Update car 1 color to red\n\n*Tool ready for real updates!*"
        
        elif "delete car" in user_lower:
            response_text = "🗑️ **delete_car_by_name() demo:**\n\nWould delete specified car from database.\nExample: Delete car with ID 1\n\n*Tool ready for real deletions!*"
        
        elif "log update" in user_lower:
            response_text = "📝 **log_update() demo:**\n\nWould log update history for car changes.\nExample: Log update for car 1 by user admin\n\n*Audit tool ready!*"
        
        elif "hello" in user_lower or "hi" in user_lower or "help" in user_lower:
            response_text = "👋 **Google ADK Agent - All 9 Tools Available:**\n\n🚗 **Car Tools:**\n• 'show cars' - get_cars()\n• 'update car' - update_car_by_name()\n• 'delete car' - delete_car_by_name()\n\n📅 **Booking Tools:**\n• 'create booking' - create_booking()\n• 'show bookings' - view all bookings\n• 'introduce booking' - introduce_booking_model()\n\n📊 **Analytics Tools:**\n• 'customer most' - get_customer_with_most_rentals()\n• 'most rented' - get_most_rented_model()\n\n🔄 **Audit Tools:**\n• 'last updated' - get_last_updated_car()\n• 'log update' - log_update()\n\n*All 9 agent tools ready!*"
        
        else:
            response_text = f"🤖 **Agent Processing:** '{user_text}'\n\nTry: 'help' to see all 9 available tools\n\n*Google ADK agent system active!*"
        
        ai_response = {
            "role": "model",
            "parts": [{"text": response_text}]
        }
        
        # Add AI response to session
        sessions_store[session_id]["events"].append({
            "content": ai_response
        })
        
        return {"content": ai_response}
        
    except Exception as e:
        error_response = {"role": "model", "parts": [{"text": f"Sorry, I encountered an error: {str(e)}"}]}
        return {"content": error_response}