import asyncio
import json
from fastapi import Request
from fastapi.responses import StreamingResponse
from db.redis_client import redis_client


async def event_stream(run_id: str, request: Request):
    """
    SSE stream for agent execution events.
    Polls Redis for new events and yields them.
    """
    last_index = 0
    
    while True:
        # Check if client disconnected
        if await request.is_disconnected():
            break
        
        # Get new events from Redis
        events = redis_client.get_events(run_id, since=last_index)
        
        for event in events:
            yield f"data: {json.dumps(event)}\n\n"
            last_index += 1
        
        # Check if run is done
        status = redis_client.get_status(run_id)
        if status in ("completed", "failed", "declined"):
            # Send final done event
            yield f"data: {json.dumps({'type': 'done', 'status': status, 'run_id': run_id})}\n\n"
            break
        
        await asyncio.sleep(0.5)  # Poll every 500ms