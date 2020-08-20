build:
	@docker build -t plant_water .

up:
	@docker-compose up -d

down:
	@docker-compose down

test: up
	@mypy src/
	@docker exec -it plant_water pytest