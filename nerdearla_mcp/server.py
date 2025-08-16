#!/usr/bin/env python3
"""
Nerdearla MCP Server

An MCP server that provides information about Nerdearla events, speakers, and sessions.
Uses FastMCP with streamable HTTP in stateless mode with JSON.
"""

from typing import Annotated, Any, Dict, List
from fastmcp import FastMCP
import httpx
import asyncio
import re
from datetime import datetime, date


# Sessionize API configuration
SESSIONIZE_API_PREFIX = "https://sessionize.com/api/v2"

# Events configuration - sorted by start_date descending (newest first)
EVENTS = {
    "dhvawevf": {
        "id": "dhvawevf",
        "name": "Nerdearla Buenos Aires 2025",
        "location": "Buenos Aires, Argentina", 
        "start_date": date(2025, 9, 24),
        "end_date": date(2025, 9, 28),
        "venue": {
            "name": "Ciudad Cultural Konex",
            "address": "Sarmiento 3131, C1196 Cdad. Autónoma de Buenos Aires",
            "google_maps_url": "https://maps.app.goo.gl/QE7Fs92tg3rQya9y6"
        }
    },
    "e0eiac8x": {
        "id": "e0eiac8x",
        "name": "Nerdearla Mexico 2024",
        "location": "Mexico City, Mexico",
        "start_date": date(2024, 11, 7),
        "end_date": date(2024, 11, 9),
        "venue": {
            "name": "Expo Reforma",
            "address": "Av. Morelos 67, Juárez, Cuauhtémoc, 06600 Mexico City, Mexico",
            "google_maps_url": "https://maps.app.goo.gl/nA1NWPHUNEUv9fJ26"
        }
    },
    "u4nsi3fc": {
        "id": "u4nsi3fc",
        "name": "Nerdearla Buenos Aires 2024",
        "location": "Buenos Aires, Argentina",
        "start_date": date(2024, 10, 15),
        "end_date": date(2024, 10, 18),
        "venue": {
            "name": "Ciudad Cultural Konex",
            "address": "Sarmiento 3131, C1196 Cdad. Autónoma de Buenos Aires",
            "google_maps_url": "https://maps.app.goo.gl/QE7Fs92tg3rQya9y6"
        }
    },
    "rqoad2w3": {
        "id": "rqoad2w3",
        "name": "Nerdearla Chile 2024",
        "location": "Santiago, Chile",
        "start_date": date(2024, 4, 11),
        "end_date": date(2024, 4, 13),
        "venue": {
            "name": "Centro Gabriela Mistral",
            "address": "Av. Alameda Libertador Bernardo O'Higgins 227, 8320275 Santiago, Región Metropolitana, Chile",
            "google_maps_url": "https://maps.app.goo.gl/LJaJVYKD8vvz5aYP8"
        }
    },
    "tb7c7u5l": {
        "id": "tb7c7u5l",
        "name": "Nerdearla Buenos Aires 2023",
        "location": "Buenos Aires, Argentina",
        "start_date": date(2023, 9, 26),
        "end_date": date(2023, 9, 30),
        "venue": {
            "name": "Ciudad Cultural Konex",
            "address": "Sarmiento 3131, C1196 Cdad. Autónoma de Buenos Aires",
            "google_maps_url": "https://maps.app.goo.gl/QE7Fs92tg3rQya9y6"
        }
    }
}


# Initialize FastMCP server
mcp = FastMCP("Nerdearla MCP Server")


def get_nearest_event() -> str:
    """
    Get the nearest event ID based on current date.
    
    Returns:
        Event ID of the nearest event (ongoing > future > past)
    """
    today = date.today()
    
    # Check for ongoing events first
    for event_id, event in EVENTS.items():
        if event["start_date"] <= today <= event["end_date"]:
            return event_id
    
    # If no ongoing event, find the nearest future event
    # Since events are pre-sorted by start_date descending, we iterate backwards
    for event_id, event in reversed(list(EVENTS.items())):
        if event["start_date"] > today:
            return event_id
    
    # If no future events, return the most recent past event
    # Since events are pre-sorted by start_date descending, the first past event is most recent
    for event_id, event in EVENTS.items():
        if event["end_date"] < today:
            return event_id
    
    # Fallback to first event if somehow no events match
    return list(EVENTS.keys())[0]


@mcp.tool()
async def list_events() -> List[Dict[str, Any]]:
    """
    Get all Nerdearla events (historical, present, and future).
    """
    today = date.today()
    events_list = []
    
    for event in EVENTS.values():
        event_data = {
            "id": event["id"],
            "name": event["name"],
            "location": event["location"],
            "start_date": event["start_date"].isoformat(),
            "end_date": event["end_date"].isoformat(),
            "venue": event["venue"],
            "status": "past" if event["end_date"] < today else 
                     "ongoing" if event["start_date"] <= today <= event["end_date"] else 
                     "future"
        }
        events_list.append(event_data)
    
    return events_list


async def fetch_speakers_from_api(event_id: str) -> List[Dict[str, Any]]:
    """
    Fetch speakers data from Sessionize API for a specific event.
    
    Args:
        event_id: Event ID to fetch speakers for
    
    Returns:
        List of speaker data from the API
    """
    speakers_url = f"{SESSIONIZE_API_PREFIX}/{event_id}/view/Speakers"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(speakers_url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"Failed to fetch speakers from API for event {event_id}: {e}") from e



@mcp.tool()
async def get_speakers(
    event_id: Annotated[str | None, "Event ID to get speakers for (defaults to nearest event)"] = None,
    q: Annotated[str | None, "Optional search query to filter speakers by name, bio, and tagline (case-insensitive)"] = None,
    only_top_speakers: Annotated[bool, "Whether to return only top speakers"] = False,
) -> List[Dict[str, Any]]:
    """
    Get information about Nerdearla speakers.
    """
    try:
        # Determine which event to use
        selected_event_id = event_id if event_id else get_nearest_event()
        
        # Validate event exists
        if selected_event_id not in EVENTS:
            return [{"error": f"Event '{selected_event_id}' not found"}]
        
        # Fetch speakers from API
        speakers = await fetch_speakers_from_api(selected_event_id)
        
        # Apply filters if provided
        if only_top_speakers:
            speakers = [
                speaker for speaker in speakers
                if speaker.get("isTopSpeaker", False) == True
            ]
        
        if q and q.lower() != "null":
            # Trim whitespace from query
            q = q.strip()
            
            # Skip if query becomes empty after trimming
            if q:
                # Create regex pattern for whole word matching (case-insensitive)
                query_pattern = re.compile(r'\b' + re.escape(q) + r'\b', re.IGNORECASE)
                
                speakers = [
                    speaker for speaker in speakers
                    if any(
                        query_pattern.search(str(speaker.get(field, "")))
                        for field in ["fullName", "bio", "tagLine"]
                    )
                ]
        
        # Return only essential fields to reduce response size
        return [
            {
                "id": speaker.get("id"),
                "fullName": speaker.get("fullName"),
                "isTopSpeaker": speaker.get("isTopSpeaker", False)
            }
            for speaker in speakers
        ]
    
    except Exception as e:
        return [{"error": f"Failed to fetch speakers: {str(e)}"}]


@mcp.tool()
async def get_speaker_details(
    speaker_id: Annotated[str, "Speaker ID to get detailed information for"],
    event_id: Annotated[str | None, "Event ID to get speaker details for (defaults to nearest event)"] = None,
) -> Dict[str, Any]:
    """
    Get detailed information about a specific Nerdearla speaker.
    """
    try:
        # Determine which event to use
        selected_event_id = event_id if event_id else get_nearest_event()
        
        # Validate event exists
        if selected_event_id not in EVENTS:
            return {"error": f"Event '{selected_event_id}' not found"}
        
        # Fetch speakers from API
        speakers = await fetch_speakers_from_api(selected_event_id)
        
        # Find the speaker by ID
        speaker = next((s for s in speakers if s.get("id") == speaker_id), None)
        
        if not speaker:
            return {"error": f"Speaker with ID '{speaker_id}' not found"}
        
        return speaker
    
    except Exception as e:
        return {"error": f"Failed to fetch speaker details: {str(e)}"}


def run_server():
    """Main entry point for the MCP server."""
    async def _run():
        await mcp.run_http_async(
            transport="streamable-http",
            host="0.0.0.0",
            port=8000,
            log_level="info",
            path="/mcp",
            stateless_http=True,
        )
    
    asyncio.run(_run())


if __name__ == "__main__":
    run_server()
