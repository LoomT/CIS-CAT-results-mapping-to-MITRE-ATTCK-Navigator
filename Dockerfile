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

# Copy the built React files
COPY --from=build-step /app/dist ./static

# Copy requirements first to leverage Docker cache
COPY api/requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of the application
COPY api .

ENV FLASK_APP=app.py
ENV FLASK_ENV=production

EXPOSE 5000

#CMD ["flask", "run", "--no-debugger", "--host=0.0.0.0"]
CMD ["gunicorn", "-b", ":5000", "app:app"]