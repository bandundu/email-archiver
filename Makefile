.PHONY: generate-key build run clean

generate-key:
	@echo "Generating Fernet key..."
	@python3 -c "from cryptography.fernet import Fernet; key = Fernet.generate_key().decode(); print(f'SECRET_KEY={key}')" > .env
	@echo "Fernet key generated and stored in .env file."

build:
	docker-compose up --build

run:
	docker-compose up

clean:
	docker-compose down
	rm -f .env
