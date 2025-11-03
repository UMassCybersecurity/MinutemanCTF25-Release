FROM node:18-slim

# Don’t download Chromium twice
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true

# Install Chromium and its dependencies
RUN apt-get update && apt-get install -y \
    chromium \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libxss1 \
    libgtk-3-0 \
    xdg-utils \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY package.json .
RUN npm install --production
COPY . .

CMD ["node", "bot.js"]