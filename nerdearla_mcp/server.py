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


# Sessionize API configuration
SESSIONIZE_API_URL = "https://sessionize.com/api/v2/dhvawevf/view/Speakers"


# Initialize FastMCP server
mcp = FastMCP("Nerdearla MCP Server")


async def fetch_speakers_from_api() -> List[Dict[str, Any]]:
    """
    Fetch speakers data from Sessionize API.
    
    Returns:
        List of speaker data from the API
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(SESSIONIZE_API_URL)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"Failed to fetch speakers from API: {e}") from e



@mcp.tool()
async def get_speakers(
    q: Annotated[str | None, "Optional search query to filter speakers by name, bio, and tagline (case-insensitive)"] = None,
    only_top_speakers: Annotated[bool, "Whether to return only top speakers"] = False,
) -> List[Dict[str, Any]]:
    """
    Get information about Nerdearla speakers.
    """
    try:
        # Fetch speakers from API
        speakers = await fetch_speakers_from_api()
        
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
    speaker_id: Annotated[str, "Speaker ID to get detailed information for"]
) -> Dict[str, Any]:
    """
    Get detailed information about a specific Nerdearla speaker.
    """
    try:
        # Fetch speakers from API
        speakers = await fetch_speakers_from_api()
        
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
