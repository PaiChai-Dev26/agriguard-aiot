from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.app.ws.manager import control_room_manager

router = APIRouter()


@router.websocket("/ws/control-room")
async def control_room(websocket: WebSocket) -> None:
    await control_room_manager.connect(websocket)
    await websocket.send_json(
        {
            "type": "control_room.connected",
            "connectionCount": control_room_manager.connection_count,
        }
    )
    try:
        while True:
            message = await websocket.receive_json()
            if message.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        control_room_manager.disconnect(websocket)

