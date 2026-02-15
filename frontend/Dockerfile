FROM node:20-alpine
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install
COPY . .
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV PORT=3000
ENV HOSTNAME=0.0.0.0
RUN npm run build
RUN mkdir -p .next/standalone/.next && cp -r .next/static .next/standalone/.next/static && cp -r public .next/standalone/public
CMD ["node", ".next/standalone/server.js"]
