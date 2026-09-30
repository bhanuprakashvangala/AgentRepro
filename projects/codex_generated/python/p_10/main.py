#!/usr/bin/env python3
"""FastAPI WebSocket dashboard broadcasting demo data to connected clients."""

from __future__ import annotations

import asyncio
import contextlib
import json
import random
import time
from pathlib import Path
from typing import List, Set

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI(title="Real-time Dashboard", version="1.0.0")

templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

_connected_clients: Set[WebSocket] = set()
_clients_lock = asyncio.Lock()


async def register_client(websocket: WebSocket) -> None:
    async with _clients_lock:
        _connected_clients.add(websocket)


async def unregister_client(websocket: WebSocket) -> None:
    async with _clients_lock:
        _connected_clients.discard(websocket)


async def broadcast(message: str) -> None:
    async with _clients_lock:
        targets: List[WebSocket] = list(_connected_clients)

    if not targets:
        return

    to_remove: List[WebSocket] = []
    for ws in targets:
        try:
            await ws.send_text(message)
        except Exception:
            to_remove.append(ws)

    for ws in to_remove:
        await unregister_client(ws)


async def data_producer() -> None:
    """Generate synthetic data points and broadcast them to all clients."""
    while True:
        payload = {
            "timestamp": time.time(),
            "value": round(random.uniform(-1, 1), 4),
        }
        await broadcast(json.dumps(payload))
        await asyncio.sleep(1.0)


@app.on_event("startup")
async def on_startup() -> None:
    app.state.data_task = asyncio.create_task(data_producer())


@app.on_event("shutdown")
async def on_shutdown() -> None:
    task = getattr(app.state, "data_task", None)
    if task:
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request})


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()
    await register_client(websocket)
    try:
        while True:
            # Keep the connection alive; echo back optional messages from clients.
            message = await websocket.receive_text()
            if message:
                await websocket.send_text(json.dumps({"echo": message}))
    except WebSocketDisconnect:
        await unregister_client(websocket)
    except Exception:
        await unregister_client(websocket)
        await websocket.close()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
