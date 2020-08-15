build:
	@docker build -t plant_water .

up:
	@docker-compose up -d

down:
	@docker-compose down

test:
	@pytest