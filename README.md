# 🐛 Issues & Insights Tracker (Mini SaaS)

[![Build](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/Adarshkumar03/mini-saas/actions)
[![License](https://img.shields.io/github/license/Adarshkumar03/mini-saas.svg)](LICENSE)
[![Stack](https://img.shields.io/badge/stack-FastAPI%20%7C%20SvelteKit%20%7C%20PostgreSQL-blueviolet)](#)

A lightweight SaaS portal for clients to submit feedback (bugs, invoices, files) and convert it into structured data for insights.

---

## 🚀 Features

- 🔐 Authentication (Register/Login)
- 👤 Role-Based Access Control (RBAC)
- 🐞 Submit & track issues with file attachments
- 📊 Dashboard for feedback insights
- 🐳 One-command Dockerized deployment

---

## ⚙️ Tech Stack

| Layer      | Technology         |
|------------|--------------------|
| Frontend   | SvelteKit          |
| Backend    | FastAPI            |
| Database   | PostgreSQL         |
| Auth       | Cookie/Session or JWT (based on impl) |
| DevOps     | Docker + Docker Compose |

---

## 📦 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Adarshkumar03/mini-saas.git
cd mini-saas
```

### 2. Set Environment Variables

Create a `.env` file in the backend with:

```env
# backend/.env

DATABASE_URL="postgresql://postgres:password@db:5432/mini_saas"
SECRET_KEY="your_secret_key_here"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
```
Create a `.env` file in the frontend with:

```env
# frontend/.env

VITE_PUBLIC_API_BASE_URL="http://localhost:8000"
```

> Update credentials as per your local setup.

3. **Docker Compose Setup**

Ensure you have Docker and Docker Compose installed. The project comes with

`docker-compose.example.yml` 
`frontend/Dockerfile.example`
`backend/Dockerfile.example`
files to set up the environment, change the names to `docker-compose.yml`, `Dockerfile`, and `Dockerfile` respectively.

### 4. Start the App

```bash
cd docker
docker compose up --build -d
```

This will launch:

- FastAPI backend on `http://localhost:8000`
- SvelteKit frontend on `http://localhost:3000`
- PostgreSQL database

---

## 🌐 Usage

Once up:

- Access frontend: [http://localhost:3000](http://localhost:3000)
- Backend API docs: [http://localhost:8000/api/docs](http://localhost:8000/api/docs)

---

## 📚 API Overview

| Endpoint              | Method | Description            |
|-----------------------|--------|------------------------|
| `api/v1/auth/register`      | POST   | Register a new user    |
| `api/v1/auth/login`         | POST   | Login and get token    |
| `api/v1/issues/`            | GET    | List all issues        |
| `api/v1/issues/`            | POST   | Submit a new issue     |
| `api/v1/users/me`           | GET    | Get current user info  |

> See full OpenAPI docs at `/docs`

---

## 🧪 Testing

```bash
# Backend (FastAPI)
cd docker
docker-compose exec backend sh -c "PYTHONPATH=. pytest --cov=app"

# Frontend (SvelteKit + Playwright)
cd frontend
npx playwright test
```

---

## 🧑‍💻 Contributing

Contributions are welcome!

1. Fork the repository
2. Create a new branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Add feature"`
4. Push and open a PR

---
