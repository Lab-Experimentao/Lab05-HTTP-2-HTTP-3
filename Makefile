.PHONY: up down ps logs client server versions test

up:
	docker compose up -d --build

down:
	docker compose down

ps:
	docker compose ps

logs:
	docker compose logs -f

client:
	docker compose exec client bash

server:
	docker compose exec server sh

versions:
	docker compose exec -T server caddy version
	docker compose exec -T client google-chrome --version

test:
	docker compose port server 443
	docker compose port --protocol udp server 443
	docker compose exec -T client curl -skI --http2 --retry 5 --retry-connrefused https://caddy.test/
	docker compose exec -T client node smoke.js
	docker compose exec -T client tc qdisc replace dev eth0 root netem delay 50ms
	docker compose exec -T client ping -c 3 caddy.test
	docker compose exec -T client tc qdisc del dev eth0 root
	docker compose exec -T server tc qdisc replace dev eth0 root netem delay 50ms
	docker compose exec -T server tc qdisc del dev eth0 root
