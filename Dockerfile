FROM python:3.11-slim
WORKDIR /app
COPY backend/ ./backend/
COPY frontend/ ./frontend/
RUN cd backend && pip install -r requirements.txt
RUN cd frontend && npm install && npm run build
EXPOSE 8000
CMD ["python", "backend/server.py"
