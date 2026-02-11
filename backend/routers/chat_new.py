from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

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

@router.post("/run_sse")
async def chat_with_ai(payload: Dict[str, Any]):
    """Handle chat messages with Google ADK Agent"""
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
        
        # Use Gemini-powered Agent with Tools
        try:
            import google.generativeai as genai
            
            # Configure Gemini
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
            model = genai.GenerativeModel('gemini-1.5-flash-latest')
            
            # Check if user wants specific tool functionality first
            user_lower = user_text.lower()
            
            if "show" in user_lower and "car" in user_lower:
                from agent.tools import get_cars
                cars = await get_cars()
                if cars:
                    car_list = "\n".join([f"• {car.company} {car.model} ({car.year}) - {car.color}, {car.kms} km" for car in cars])
                    response_text = f"🚗 **Cars in System:**\n\n{car_list}"
                else:
                    response_text = "No cars found."
            
            elif "create" in user_lower and "booking" in user_lower:
                # Interactive booking with Gemini
                from agent.tools import get_cars
                cars = await get_cars()
                if cars:
                    car_list = "\n".join([f"{i+1}. {car.company} {car.model} ({car.year}) - {car.color}" for i, car in enumerate(cars)])
                    
                    prompt = f"""You are a car rental booking assistant. The user wants to create a booking.
                    
Available cars:
{car_list}
                    
User said: "{user_text}"
                    
Please ask the user for the following booking details in a friendly way:
1. Which car they want (by number)
2. Start date (YYYY-MM-DD format)
3. End date (YYYY-MM-DD format) 
4. Customer ID (optional, default 101)
                    
Be conversational and helpful. Don't create the booking yet, just ask for details."""
                    
                    response = model.generate_content(prompt)
                    response_text = response.text
                else:
                    response_text = "No cars available for booking."
            
            elif "customer" in user_lower and "most" in user_lower:
                from agent.tools import get_customer_with_most_rentals
                result = await get_customer_with_most_rentals()
                response_text = f"🏆 **Top Customer:**\n\n{result}"
            
            elif "most rented" in user_lower:
                from agent.tools import get_most_rented_model
                result = await get_most_rented_model()
                response_text = f"🚗 **Most Rented:**\n\n{result}"
            
            else:
                # Use Gemini for general conversation
                prompt = f"""You are a helpful car management assistant. You can help with:
- Showing cars: "show cars"
- Creating bookings: "create booking" 
- Analytics: "customer most" or "most rented"
                
User said: "{user_text}"
                
Respond helpfully and guide them to use the available features."""
                
                response = model.generate_content(prompt)
                response_text = response.text
            
        except Exception as agent_error:
            response_text = f"🤖 **Agent Error:**\n\n{str(agent_error)}"
        
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