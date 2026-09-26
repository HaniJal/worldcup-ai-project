FROM node:20-alpine

WORKDIR /app

# Install dependencies first so they're cached until package files change
COPY package.json package-lock.json ./
RUN npm ci

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev"]
