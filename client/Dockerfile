FROM node:24-bookworm-slim
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl iproute2 iputils-ping \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci \
    && npx playwright install --with-deps chrome \
    && apt-get clean && rm -rf /var/lib/apt/lists/*
COPY . .
CMD ["sleep", "infinity"]
