FROM python:3.9

WORKDIR /app

COPY requirements.txt .

# Install Rust compiler for cryptography package
RUN apt-get update && apt-get install -y --no-install-recommends build-essential libssl-dev libffi-dev python3-dev cargo
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "app.py"]