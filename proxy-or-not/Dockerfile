# Use official Python image for FastAPI app
FROM python:3.11-slim as app
WORKDIR /app
RUN pip install fastapi uvicorn[standard]
COPY app.py ./
COPY ui/dist ./ui/dist

# Use official nginx image for proxy
FROM nginx:alpine
COPY --from=app /app /app
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80 for nginx
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
