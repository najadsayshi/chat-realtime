# 💬 Real-Time Chat App (FastAPI + Redis + PostgreSQL + Vanilla JS)

## 🚀 Overview

A scalable real-time chat application built using FastAPI, WebSockets, PostgreSQL, and Redis Pub/Sub.
Features a premium Vanilla JS (Glassmorphism) frontend and supports multi-room messaging, authentication, persistence, and horizontal scaling.

---

## ⚡ Features

* 🔌 Real-time messaging using WebSockets
* 🏠 Multi-room chat support
* 🔐 JWT-based authentication
* 🧱 PostgreSQL for message storage
* ⚡ Redis Pub/Sub for scalable message broadcasting
* 📜 Message history API with pagination
* 🧩 Event-driven architecture (JOIN_ROOM, LEAVE_ROOM, MESSAGE)
* 🎨 Premium glassmorphism frontend (Vanilla HTML/CSS/JS)

---

## 🧠 Architecture

Client (Vanilla JS) → WebSocket → FastAPI
      ↓
    Save Message (PostgreSQL)
      ↓
    Publish to Redis
      ↓
    Redis Pub/Sub
      ↓
    All servers receive message
      ↓
    Broadcast to room users

---

## 🛠️ Tech Stack

* FastAPI
* WebSockets
* SQLModel
* PostgreSQL (Neon)
* Redis
* JWT Authentication
* Vanilla HTML/CSS/JS (Frontend)

---

## 📡 API Endpoints

### 🔹 Get Messages

```http
GET /messages?room_id=1&limit=20&offset=0
```

---

## 🔌 WebSocket

### Connect:

```
ws://localhost:8000/ws?token=YOUR_JWT_TOKEN
```

### Events:

#### Join Room

```json
{
  "type": "JOIN_ROOM",
  "room_id": 1
}
```

#### Send Message

```json
{
  "type": "MESSAGE",
  "room_id": 1,
  "content": "Hello!"
}
```

---

## 🧱 Project Structure

```
app/
├── models/
├── routes/
├── websockets/
├── core/
├── auth/
├── main.py
```

### 🎨 Frontend Structure

```
frontend/
├── index.html
├── styles.css
└── app.js
```

---

## ▶️ Run Locally

```bash
# 1. Start the Backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 2. Open the Frontend

Simply open `frontend/index.html` in your favorite web browser!

---

## 💡 Future Improvements

* Typing indicators
* Read receipts
* File/image messages
* Role-based room access
* Deployment (Docker + Cloud)

---

## 🧠 Key Learnings

* Real-time communication with WebSockets
* Distributed systems using Redis
* Database design and persistence
* API pagination and optimization
* Backend system architecture

---

## 💯 Summary

A production-style real-time chat backend demonstrating scalable system design using modern backend technologies.
