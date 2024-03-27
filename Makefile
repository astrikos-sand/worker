include .env

build:
	docker compose up --build -d

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker logs -f astrikos_worker

shell:
	docker exec -it astrikos_worker bash