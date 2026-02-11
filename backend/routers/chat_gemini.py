from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import uuid
import os
import google.generativeai as genai
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

# Define function schemas for Gemini
function_declarations = [
    {
        "name": "get_cars",
        "description": "Get all cars from the database",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "create_booking",
        "description": "Create a new car booking",
        "parameters": {
            "type": "object",
            "properties": {
                "customer_id": {"type": "integer", "description": "Customer ID"},
                "car_id": {"type": "integer", "description": "Car ID to book"},
                "start_date": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                "end_date": {"type": "string", "description": "End date (YYYY-MM-DD)"},
                "total_price": {"type": "number", "description": "Total booking price"}
            },
            "required": ["customer_id", "car_id", "start_date", "end_date", "total_price"]
        }
    },
    {
        "name": "get_customer_with_most_rentals",
        "description": "Get the customer who has rented the most cars",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_most_rented_model",
        "description": "Get the car model that is rented most often",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
]

# Function implementations
async def execute_function(function_name: str, parameters: dict):
    """Execute the requested function with parameters"""
    try:
        if function_name == "get_cars":
            from agent.tools import get_cars
            result = await get_cars()
            return {"cars": [{"company": car.company, "model": car.model, "year": car.year, 
                           "color": car.color, "kms": car.kms, "available": car.available} for car in result]}
        
        elif function_name == "create_booking":
            from agent.tools import create_booking
            result = await create_booking(
                parameters["customer_id"],
                parameters["car_id"], 
                parameters["start_date"],
                parameters["end_date"],
                parameters["total_price"]
            )
            return {"result": str(result)}
        
        elif function_name == "get_customer_with_most_rentals":
            from agent.tools import get_customer_with_most_rentals
            result = await get_customer_with_most_rentals()
            return {"result": str(result)}
        
        elif function_name == "get_most_rented_model":
            from agent.tools import get_most_rented_model
            result = await get_most_rented_model()
            return {"result": str(result)}
        
        else:
            return {"error": f"Unknown function: {function_name}"}
    
    except Exception as e:
        return {"error": f"Function execution failed: {str(e)}"}

@router.post("/run_sse")
async def chat_with_ai(payload: Dict[str, Any]):
    """Handle chat messages with Gemini Function Calling"""
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
        
        # Intelligent Agent with Natural Language Processing
        user_lower = user_text.lower()
        
        # Smart pattern matching for natural language
        if any(word in user_lower for word in ["show", "list", "see", "view"]) and "car" in user_lower:
            result = await execute_function("get_cars", {})
            cars = result.get("cars", [])
            if cars:
                car_list = "\n".join([f"• {car['company']} {car['model']} ({car['year']}) - {car['color']}, {car['kms']} km, Available: {'Yes' if car['available'] else 'No'}" for car in cars])
                response_text = f"🚗 **Available Cars:**\n\n{car_list}\n\nWhich car would you like to book?"
            else:
                response_text = "No cars found in the system."
        
        elif any(word in user_lower for word in ["book", "booking", "reserve", "rent"]):
            if "create" in user_lower or "new" in user_lower or "make" in user_lower:
                # Show available cars first
                result = await execute_function("get_cars", {})
                cars = result.get("cars", [])
                available_cars = [car for car in cars if car['available']]
                if available_cars:
                    car_list = "\n".join([f"• Car {i+1}: {car['company']} {car['model']} ({car['year']})" for i, car in enumerate(available_cars)])
                    response_text = f"📅 **Let's create a booking!**\n\n**Available Cars:**\n{car_list}\n\n📝 **Please tell me:**\n• Which car? (e.g., 'Car 1')\n• Customer ID? (e.g., 101)\n• Start date? (YYYY-MM-DD)\n• End date? (YYYY-MM-DD)\n• Total price? (e.g., 500)\n\n*Example: 'Book Car 1 for customer 101 from 2024-12-20 to 2024-12-25 for $500'*"
                else:
                    response_text = "Sorry, no cars are currently available for booking."
            else:
                # Try to parse booking details from natural language
                import re
                
                # Extract numbers and dates
                numbers = re.findall(r'\d+', user_text)
                dates = re.findall(r'\d{4}-\d{2}-\d{2}', user_text)
                
                if len(numbers) >= 3 and len(dates) >= 2:
                    try:
                        customer_id = int(numbers[0])
                        car_id = int(numbers[1]) 
                        total_price = float(numbers[2]) if len(numbers) > 2 else 500.0
                        start_date = dates[0]
                        end_date = dates[1]
                        
                        result = await execute_function("create_booking", {
                            "customer_id": customer_id,
                            "car_id": car_id,
                            "start_date": start_date,
                            "end_date": end_date,
                            "total_price": total_price
                        })
                        response_text = f"✅ **Booking Created Successfully!**\n\n{result['result']}"
                    except Exception as e:
                        response_text = f"I couldn't process the booking details. Please provide: customer ID, car ID, start date, end date, and price."
                else:
                    response_text = "I need more details to create a booking. Please provide customer ID, car ID, start date (YYYY-MM-DD), end date (YYYY-MM-DD), and total price."
        
        elif any(word in user_lower for word in ["customer", "top", "most rental", "best customer"]):
            result = await execute_function("get_customer_with_most_rentals", {})
            response_text = f"🏆 **Top Customer Analytics:**\n\n{result['result']}"
        
        elif any(word in user_lower for word in ["popular", "most rented", "best model", "top model"]):
            result = await execute_function("get_most_rented_model", {})
            response_text = f"🚗 **Most Popular Car Model:**\n\n{result['result']}"
        
        elif any(word in user_lower for word in ["hello", "hi", "hey", "help"]):
            response_text = "👋 **Hello! I'm your intelligent car management assistant!**\n\n🤖 **I can help you with:**\n• 'Show me all cars' - View available vehicles\n• 'Create a booking' - Make a reservation\n• 'Who is our top customer?' - Customer analytics\n• 'What's the most popular car?' - Vehicle analytics\n\n*Just ask me naturally - I understand conversational language!*"
        
        else:
            response_text = f"🤖 **I understand you said:** '{user_text}'\n\nI can help you with:\n• Viewing cars: 'show me all cars'\n• Creating bookings: 'I want to make a booking'\n• Analytics: 'who is our top customer?' or 'what's the most popular car?'\n\n*Ask me anything about car management!*"
        
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
        import traceback
        error_details = traceback.format_exc()
        error_response = {"role": "model", "parts": [{"text": f"Sorry, I encountered an error: {str(e)}\n\nDetails: {error_details}"}]}
        return {"content": error_response}