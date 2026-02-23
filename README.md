# Pariksha365 Test Series Platform - Deployment Guide

This full-stack Pariksha365 platform acts as a production-grade skeleton, with a FastAPI backend, React+Vite frontend, and an Expo React Native mobile app.

## Prerequisites
- Docker & Docker Compose (Optional for backend deployment)
- Node.js 18+
- Python 3.11+
- PostgreSQL server

## 1. Backend Setup

1. **Install dependencies**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Environment Variables**:
   Copy the `backend/.env.example` file to `backend/.env` and update the database URL and Stripe secrets.

3. **Database Migrations**:
   Assuming PostgreSQL is running via your `DATABASE_URL`, execute:
   ```bash
   alembic revision --autogenerate -m "Initial schema"
   alembic upgrade head
   ```

4. **Run Locally**:
   ```bash
   uvicorn app.main:app --reload
   ```

## 2. Web Frontend Setup

1. **Install dependencies**:
   ```bash
   cd frontend-web
   npm install
   ```
2. **Setup Tailwind & Start**:
   The `tailwind.config.js` is set.
   ```bash
   npm run dev
   ```

## 3. Mobile Frontend Setup (Expo)

1. **Install dependencies**:
   ```bash
   cd frontend-mobile
   npm install
   ```

2. **Run App**:
   ```bash
   npx expo start
   ```

## Deployment Info
- Ensure all CORS mappings match your production GUI domains.
- Setup a reverse proxy like Nginx mapping `/api/v1` to the FastAPI instances.
- For Docker deployment, use `docker build -t pariksha365-backend ./backend` and map `.env` correctly into the container.
