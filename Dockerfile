FROM python:3.9

WORKDIR /app

# Install backend dependencies
COPY requirements.txt .
RUN apt-get update && apt-get install -y --no-install-recommends build-essential libssl-dev libffi-dev python3-dev cargo
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Install frontend dependencies
WORKDIR /app/frontend/briefbox-front
COPY frontend/briefbox-front/package*.json ./
RUN apt-get update && apt-get install -y --no-install-recommends nodejs npm
RUN npm install

# Copy the rest of the application code
WORKDIR /app
COPY . .

# Expose ports for backend and frontend
EXPOSE 5000 3000

# Start the backend and frontend
CMD ["sh", "-c", "python app.py & cd frontend/briefbox-front && npm start"]