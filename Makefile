build:
	docker build -t plant_water .

start:
	docker-compose up -d
	docker logs plant_water -f

down:
	docker-compose down