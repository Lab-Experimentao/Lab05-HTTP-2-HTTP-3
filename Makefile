.PHONY: up down ps logs client server versions test rede rede-limpar rede-status test-rede coleta piloto pagina poder

up:
	docker compose up -d --build --wait

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

# O caminho é relativo (../scripts) para o Git Bash do Windows não convertê-lo.
NO_SERVER = docker compose exec -T server sh ../scripts/rede.sh
NO_CLIENT = docker compose exec -T client sh ../scripts/rede.sh

# Ex.: make rede PERDA=2. A perda fica só no servidor; o atraso, nos dois lados.
rede:
	$(NO_SERVER) aplicar $(PERDA)
	$(NO_CLIENT) aplicar 0

rede-limpar:
	$(NO_SERVER) limpar
	$(NO_CLIENT) limpar

rede-status:
	$(NO_SERVER) status
	$(NO_CLIENT) status

test-rede: $(addprefix test-rede-,0 1 2 3 5)
	$(MAKE) --no-print-directory rede-limpar
	docker compose exec -T client ping -q -i 0.01 -c 100 caddy.test

test-rede-%:
	$(MAKE) --no-print-directory rede PERDA=$*
	docker compose exec -T client ping -q -i 0.01 -c 2000 caddy.test
	docker compose exec -T client node smoke.js

# Ex.: make coleta REPS=90 SAIDA=coleta.csv. Grava em dados/$(SAIDA), acrescentando linhas.
# Para cada nível: aplica a perda e mede REPS cargas de cada protocolo, em ordem aleatória.
REPS ?= 90
SAIDA ?= coleta.csv
SEMENTE ?= 42
PERDAS ?= 0 1 2 3 5

coleta:
	@for p in $(PERDAS); do \
		$(MAKE) --no-print-directory rede PERDA=$$p || exit 1; \
		docker compose exec -T client node medir.js --perda $$p --reps $(REPS) \
			--saida /dados/$(SAIDA) --semente $(SEMENTE) || exit 1; \
	done
	$(MAKE) --no-print-directory rede-limpar

piloto:
	$(MAKE) --no-print-directory coleta REPS=5 SAIDA=piloto.csv

pagina:
	python scripts/gerar_pagina.py

poder:
	python analise/testar.py
	python analise/poder.py
