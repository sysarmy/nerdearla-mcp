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


def _extract_text_from_object(obj: Any) -> str:
    """
    Recursively extract text from nested objects.
    
    Args:
        obj: Object to extract text from (dict, list, or primitive)

    Returns:
        String representation of all text content
    """
    text_parts = []
    
    if isinstance(obj, dict):
        for value in obj.values():
            text_parts.append(_extract_text_from_object(value))
    elif isinstance(obj, list):
        for item in obj:
            text_parts.append(_extract_text_from_object(item))
    elif obj is not None:
        text_parts.append(str(obj))
    
    return " ".join(text_parts)


@mcp.tool()
async def get_speakers(
    q: Annotated[str | None, "Optional search query to filter speakers across all fields (case-insensitive)"] = None,
) -> List[Dict[str, Any]]:
    """
    Get information about Nerdearla speakers.
    """
    try:
        # Fetch speakers from API
        speakers = await fetch_speakers_from_api()
        
        # Apply search filter if provided
        if q:
            # Create regex pattern for whole word matching (case-insensitive)
            query_pattern = re.compile(r'\b' + re.escape(q) + r'\b', re.IGNORECASE)
            
            speakers = [
                speaker for speaker in speakers
                if query_pattern.search(_extract_text_from_object(speaker))
            ]
        
        return speakers
    
    except Exception as e:
        return [{"error": f"Failed to fetch speakers: {str(e)}"}]


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
