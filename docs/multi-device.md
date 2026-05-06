# Multi-Device Unification Architecture

## Core Problem

用户有 Mac、iPhone、iPad、Apple Watch、Web 等多个终端，要求：
1. **任意端发起对话**，其它端可接续
2. **状态实时同步**（读/写/通知状态）
3. **端侧能力适配**（Watch 轻量交互 vs Desktop 全功能）
4. **离线可用** + **在线同步**

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     Unified Session Layer                     │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │                    Session ID: uuid                       │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │ │
│  │  │ Messages │  │ Context  │  │ Memory   │  │ Devices  │ │ │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │ │
│  └──────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
         ▲              │              │              ▲
         │  WebSocket   │   REST API   │   Push       │
         ▼              ▼              ▼              ▼
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│   Web    │  │   Mac    │  │  iPhone  │  │  Watch   │
│ (Next.js)│  │  (Swift) │  │ (Swift)  │  │(watchOS) │
└──────────┘  └──────────┘  └──────────┘  └──────────┘
```

## Key Design Decisions

### 1. Session-Centric (not device-centric)

Instead of per-device conversations, use **one unified session**:

```python
Session = {
    "id": "uuid",
    "user_id": "uuid",
    "active_devices": ["mac", "iphone", "watch"],
    "context": {
        "current_agent": "conversation",
        "last_message_ts": "...",
        "active_device": "mac",  # which device has focus
    },
    "messages": [...],
}
```

- User speaks on iPhone → message appended to session → Mac/iPad/Watch receive via WebSocket
- Any device can "take over" by sending focus event
- Read receipts sync across devices

### 2. Event Bus (Redis Pub/Sub)

Each device subscribes to its user's event channel:

```
Channel: user:{user_id}:events
Events:
  - message.new         # new message in session
  - message.read        # read receipt
  - device.focus        # which device is active
  - device.status       # online/offline/battery
  - agent.state         # agent thinking/done/waiting
  - notification.push   # push notification request
```

```python
class EventBus:
    async def publish(self, user_id: str, event: dict): ...
    async def subscribe(self, user_id: str, handler): ...
```

Devices that are offline get push notifications as fallback.

### 3. Device Registry with Capabilities

```python
Device = {
    "id": "uuid",
    "user_id": "uuid",
    "name": "My MacBook Pro",
    "type": "desktop",          # desktop | phone | tablet | watch | web
    "platform": "macos",        # macos | ios | watchos | web
    "capabilities": {
        "input": ["text", "voice", "image"],
        "output": ["text", "image", "audio", "haptic"],
        "compute": "edge",     # none | edge | cloud
        "display": "large",    # none | small | medium | large
        "sensors": ["location", "motion", "health"],
    },
    "status": {
        "online": True,
        "battery": 85,
        "focus": False,        # user actively using this device
    },
    "last_seen": "2025-05-06T10:00:00Z",
}
```

### 4. Adaptive Response (per device capability)

Agent generates response, then adapts for each target device:

```python
async def deliver_to_device(device: Device, response: AgentResponse):
    if device.type == "watch":
        # Strip to 3 lines max, no images
        return WatchFormat(response.summary(max_chars=120))
    elif device.type == "phone":
        # Full text, notifications on response
        return PhoneFormat(response)
    elif device.type == "desktop":
        # Full rich rendering (markdown, images, graphs)
        return DesktopFormat(response)
```

### 5. Offline-First with Sync

Each device maintains local state (SQLite + ChromaDB):
- Writes go to local first (optimistic), then sync
- Sync protocol: CRDT-based last-writer-wins with vector clock
- Conflict resolution: latest timestamp wins, but divergences are flagged

```
Device Offline:  write → local DB → queue sync
Device Online:   push local changes → pull remote changes → merge → notify
```

### 6. Cross-Device Handoff

User on iPhone: "帮我查一下邮件里说的会议时间"
→ iPhone agent starts processing
→ User switches to Mac
→ Notification on Mac: "Continue on this device?"
→ Mac picks up same session, sees agent is "thinking" with a partial response

```python
# handoff protocol
{
    "type": "device.handoff",
    "from_device": "iphone-1",
    "to_device": "mac-1",
    "session_id": "uuid",
    "state_snapshot": { ... }  # frozen agent state
}
```

## Data Flow Example

```
User (iPhone): "明天天气怎么样？"

1. iPhone → API → EventBus: { type: "message.new", ... }
2. Session created/located, routed to KnowledgeAgent
3. KnowledgeAgent calls MCP tool web_search()
4. Agent streams response
5. EventBus emits:
   - message.chunk → target all online devices
   - message.done  → notify all devices
6. Mac receives chunks → renders in real-time
7. Watch receives summary notification
8. When user reads on Mac → EventBus: message.read → iPhone clears notification
```

## Implementation Roadmap

| Phase | Feature | Tech |
|-------|---------|------|
| **P1** | Device Registry + Session | PostgreSQL + Redis |
| **P1** | Event Bus (Redis Pub/Sub) | redis-py |
| **P2** | WebSocket real-time sync | FastAPI WebSocket |
| **P2** | Device capability adaptation | Agent response formatters |
| **P3** | Offline-first (SQLite + CRDT) | SQLite + custom sync |
| **P3** | Push notifications | FCM/APNs bridge |
| **P4** | Cross-device handoff | State serialization |
| **P4** | Apple Watch native app | SwiftUI + WatchConnectivity |
