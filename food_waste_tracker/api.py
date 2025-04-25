import os
import json
import pandas as pd
from datetime import datetime
import streamlit as st
from anthropic import Anthropic
from chatbot import get_chatbot_response
from food_waste_data import initialize_data, add_waste_entry, get_stats
from database import unit_to_kg

"""
This module provides API functions for interacting with the Food Waste Tracker.
It will be integrated into the Streamlit app rather than running as a separate service.
"""

def process_chat_api(message, waste_data):
    """
    API function for chatbot interaction
    
    Args:
        message (str): User message
        waste_data (pd.DataFrame): The waste data
        
    Returns:
        dict: Response containing chatbot's answer
    """
    try:
        if not message:
            return {"error": "Missing 'message' field"}
        
        # Get response from the chatbot
        response = get_chatbot_response(message, waste_data)
        
        return {"response": response}
    
    except Exception as e:
        return {"error": str(e)}

def process_add_waste_api(data, waste_data):
    """
    API function to add a waste entry
    
    Args:
        data (dict): Waste entry data with fields:
            - food_item (str): Name of the food item
            - category (str): Food category
            - quantity (float): Amount wasted
            - unit (str): Unit of measurement
            - date (str): Date in YYYY-MM-DD format
            - reason (str): Reason for waste
            - notes (str, optional): Additional notes
        waste_data (pd.DataFrame): The waste data
        
    Returns:
        dict: Success status and message
    """
    try:
        # Validate required fields
        required_fields = ['food_item', 'category', 'quantity', 'unit', 'date', 'reason']
        for field in required_fields:
            if field not in data:
                return {"error": f"Missing required field: {field}"}
        
        # Parse date
        try:
            date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        except ValueError:
            return {"error": "Invalid date format. Use YYYY-MM-DD"}
        
        # Add waste entry
        add_waste_entry(
            waste_data,
            data['food_item'],
            data['category'],
            float(data['quantity']),
            data['unit'],
            date,
            data['reason'],
            data.get('notes', '')  # Optional field
        )
        
        return {
            "success": True,
            "message": "Waste entry added successfully"
        }
    
    except Exception as e:
        return {"error": str(e)}

def process_stats_api(period, waste_data):
    """
    API function to get food waste statistics
    
    Args:
        period (str): Time period ("7days", "30days", "month", "year", "all")
        waste_data (pd.DataFrame): The waste data
        
    Returns:
        dict: Statistics about food waste
    """
    try:
        # Filter data based on period
        today = pd.Timestamp(datetime.now().date())
        
        if period == '7days':
            filtered_data = waste_data[waste_data['date'] >= (today - pd.Timedelta(days=7))]
        elif period == '30days':
            filtered_data = waste_data[waste_data['date'] >= (today - pd.Timedelta(days=30))]
        elif period == 'month':
            current_month = today.month
            current_year = today.year
            filtered_data = waste_data[
                (waste_data['date'].dt.month == current_month) & 
                (waste_data['date'].dt.year == current_year)
            ]
        elif period == 'year':
            current_year = today.year
            filtered_data = waste_data[waste_data['date'].dt.year == current_year]
        else:  # 'all' or any invalid value
            filtered_data = waste_data
        
        # If no data available
        if len(filtered_data) == 0:
            return {
                "total_waste_kg": 0,
                "avg_daily_waste_kg": 0,
                "most_wasted_category": "None",
                "waste_by_category": {},
                "waste_by_reason": {}
            }
        
        # Calculate statistics
        total_waste_kg, avg_daily_waste_kg, most_wasted_category = get_stats(filtered_data)
        
        # Get waste by category
        category_waste = filtered_data.groupby('category')['quantity_kg'].sum()
        waste_by_category = category_waste.to_dict()
        
        # Get waste by reason
        reason_waste = filtered_data.groupby('reason')['quantity_kg'].sum()
        waste_by_reason = reason_waste.to_dict()
        
        return {
            "total_waste_kg": float(total_waste_kg),
            "avg_daily_waste_kg": float(avg_daily_waste_kg),
            "most_wasted_category": most_wasted_category,
            "waste_by_category": {k: float(v) for k, v in waste_by_category.items()},
            "waste_by_reason": {k: float(v) for k, v in waste_by_reason.items()}
        }
    
    except Exception as e:
        return {"error": str(e)}

def process_entries_api(params, waste_data):
    """
    API function to get waste entries
    
    Args:
        params (dict): Query parameters:
            - limit (int): Number of entries to return
            - offset (int): Number of entries to skip
            - sort (str): Field to sort by
            - order (str): Sort order ("asc" or "desc")
        waste_data (pd.DataFrame): The waste data
        
    Returns:
        dict: Paginated list of waste entries
    """
    try:
        # Get query parameters
        limit = int(params.get('limit', 10))
        offset = int(params.get('offset', 0))
        sort_by = params.get('sort', 'date')
        order = params.get('order', 'desc')
        
        # Validate parameters
        if limit < 1 or limit > 100:
            limit = 10
        
        if offset < 0:
            offset = 0
        
        # Make sure sort_by field exists
        valid_sort_fields = waste_data.columns.tolist()
        if sort_by not in valid_sort_fields:
            sort_by = 'date'
        
        # Sort data
        ascending = (order.lower() == 'asc')
        sorted_data = waste_data.sort_values(by=sort_by, ascending=ascending)
        
        # Apply pagination
        paginated_data = sorted_data.iloc[offset:offset + limit]
        
        # Convert to list of dictionaries
        entries = []
        for _, row in paginated_data.iterrows():
            entry = {
                'id': int(row['id']) if 'id' in row else None,
                'food_item': row['food_item'],
                'category': row['category'],
                'quantity': float(row['quantity']),
                'unit': row['unit'],
                'quantity_kg': float(row['quantity_kg']),
                'date': row['date'].strftime('%Y-%m-%d'),
                'reason': row['reason'],
                'notes': row['notes'] if 'notes' in row else ''
            }
            entries.append(entry)
        
        return {
            "total": len(waste_data),
            "entries": entries
        }
    
    except Exception as e:
        return {"error": str(e)}

def process_anthropic_api(message, waste_data=None):
    """
    API function to get a response from Anthropic Claude
    
    Args:
        message (str): User message
        waste_data (pd.DataFrame, optional): The waste data. Defaults to None.
        
    Returns:
        dict: Response from Claude
    """
    try:
        # Check if API key is available
        anthropic_api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not anthropic_api_key:
            return {
                "error": "ANTHROPIC_API_KEY is not set. Please set up your API key in the environment variables."
            }
        
        # Initialize Anthropic client
        client = Anthropic(api_key=anthropic_api_key)
        
        # Get waste data context if available
        data_context = ""
        if waste_data is not None and not waste_data.empty:
            total_waste_kg, avg_daily_waste_kg, most_wasted_category = get_stats(waste_data)
            
            data_context = f"""
Current Food Waste Statistics:
- Total Waste: {total_waste_kg:.2f} kg
- Average Daily Waste: {avg_daily_waste_kg:.2f} kg
- Most Wasted Category: {most_wasted_category}
"""
            
            # Add sample of recent entries
            if len(waste_data) > 0:
                recent_entries = waste_data.sort_values('date', ascending=False).head(3)
                data_context += "\nMost Recent Entries:\n"
                for _, row in recent_entries.iterrows():
                    data_context += f"- {row['food_item']} ({row['category']}): {row['quantity']} {row['unit']} on {row['date'].strftime('%Y-%m-%d')}\n"
        
        # Prepare the prompt
        system_prompt = """You are an AI assistant specialized in food waste reduction and management, but you can also answer general questions on any topic. 
You have access to the user's food waste tracking data from their Food Waste Tracker application.
When the user asks about food waste, provide helpful, informative responses about reducing food waste, understanding waste patterns, 
and adopting sustainable practices. When the user asks general questions unrelated to food waste, provide helpful and accurate information on those topics as well.
Be concise but thorough in your responses.
"""

        # Get response from Claude
        # the newest Anthropic model is "claude-3-5-sonnet-20241022" which was released October 22, 2024
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": f"{data_context}\n\nUser question: {message}"
                }
            ]
        )
        
        response_text = message.content[0].text
        
        return {
            "response": response_text
        }
    
    except Exception as e:
        return {"error": str(e)}