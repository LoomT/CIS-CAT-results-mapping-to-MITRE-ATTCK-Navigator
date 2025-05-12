# Build the Angular-based ATT&CK Navigator see https://github.com/mitre-attack/attack-navigator/blob/master/Dockerfile
FROM node:18 AS navigator-builder
ENV NODE_OPTIONS=--openssl-legacy-provider

COPY ./attack-navigator /build/attack-navigator/

WORKDIR /build/attack-navigator/nav-app

RUN npm ci

# production build (requires these two extra flags; see Navigator README)
# Also add --deploy-url /attack-navigator/ angular option so paths are relative to /attack-navigator/
# The --base-href is required for the assets/config.json fetch which does not adhere to the --deploy-url
RUN npm run build -- --deploy-url /attack-navigator/ --base-href /attack-navigator/  \
      --configuration production --aot=false --build-optimizer=false

FROM node:22-alpine AS build-step
WORKDIR /app
ENV PATH=/app/node_modules/.bin:$PATH
COPY client/package.json client/vite.config.js client/index.html ./
COPY ./client/src ./src
COPY ./client/public ./public
RUN npm install
RUN npm run build

FROM python:3.13-slim
WORKDIR /app

# Copy the attack-navigator files
# Copy earlier since this is unlikely to change
COPY --from=navigator-builder /build/attack-navigator/nav-app/dist/ ./static/attack-navigator

# Copy requirements first to leverage Docker cache
COPY api/requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of the application
COPY api .

ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV FLASK_STATIC_FOLDER=static

# Copy the built React files after building the backend.
# This way we don't have to rebuild the API when we only change the frontend
COPY --from=build-step /app/dist ./static

EXPOSE 5000

#CMD ["flask", "run", "--no-debugger", "--host=0.0.0.0"]
CMD ["gunicorn", "-b", ":5000", "app:app"]