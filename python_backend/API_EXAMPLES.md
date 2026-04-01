# API Examples — Time Capsule Study Platform

Base URL: `http://localhost:8000`

---

## Auth

### Signup
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice", "email": "alice@example.com", "password": "secret123"}'
```

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "alice@example.com", "password": "secret123"}'
```
> Save the `access_token` from the response — you'll need it as a Bearer token.

### Get current user
```bash
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer <token>"
```

---

## Rooms

### Create a room
```bash
curl -X POST http://localhost:8000/api/rooms/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "CS Study Group", "description": "Algorithms and data structures"}'
```

### Join a room
```bash
curl -X POST http://localhost:8000/api/rooms/join \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"invite_code": "ABC12345"}'
```

### Get all my rooms
```bash
curl http://localhost:8000/api/rooms/ \
  -H "Authorization: Bearer <token>"
```

### Update a room
```bash
curl -X PUT http://localhost:8000/api/rooms/1 \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Room Name"}'
```

### Leave a room
```bash
curl -X DELETE http://localhost:8000/api/rooms/1/leave \
  -H "Authorization: Bearer <token>"
```

---

## Tasks

### Create a task
```bash
curl -X POST http://localhost:8000/api/rooms/1/tasks/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Read Chapter 5",
    "description": "Dynamic programming",
    "priority": "high",
    "due_date": "2026-04-10T23:59:00"
  }'
```

### Get all tasks in a room
```bash
curl http://localhost:8000/api/rooms/1/tasks/ \
  -H "Authorization: Bearer <token>"
```

### Update a task (e.g. mark done)
```bash
curl -X PUT http://localhost:8000/api/rooms/1/tasks/1 \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"status": "done"}'
```

### Delete a task
```bash
curl -X DELETE http://localhost:8000/api/rooms/1/tasks/1 \
  -H "Authorization: Bearer <token>"
```

---

## Interactive Docs
FastAPI auto-generates Swagger UI at: `http://localhost:8000/docs`
ReDoc is available at: `http://localhost:8000/redoc`
