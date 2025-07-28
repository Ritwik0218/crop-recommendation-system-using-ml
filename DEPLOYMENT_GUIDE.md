# 🚀 Crop Recommendation System - Deployment Guide

This guide provides comprehensive instructions for deploying the Crop Recommendation System in various environments.

## 📋 Prerequisites

- Python 3.8+ installed
- Git (for cloning)
- Virtual environment support
- Web browser for testing

## 🛠️ Quick Start (Development)

### 1. Clone and Setup
```bash
git clone <https://github.com/Ritwik0218/crop-recommendation-system-using-ml.git>
cd Crop-Recommendation-System-Using-Machine-Learning-main
```

### 2. Run the Application
```bash
# Option 1: Use the automated script
./run.sh

# Option 2: Manual setup
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python validate_setup.py
python app.py
```

### 3. Access the Application
- Open your browser and go to: `http://localhost:5001`
- Health check endpoint: `http://localhost:5001/health`

## 🌐 Production Deployment

### Environment Configuration

#### Development Environment
```bash
export FLASK_ENV=development
export SECRET_KEY=dev-key-change-in-production
export HOST=127.0.0.1
export PORT=5001
```

#### Production Environment
```bash
export FLASK_ENV=production
export SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
export HOST=0.0.0.0
export PORT=5000
```

### 🐳 Docker Deployment

#### 1. Create Dockerfile
```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_ENV=production
ENV HOST=0.0.0.0
ENV PORT=5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

# Run the application
CMD ["python", "app.py"]
```

#### 2. Build and Run with Docker
```bash
# Build the image
docker build -t crop-recommendation-system .

# Run the container
docker run -d \
  --name crop-app \
  -p 5000:5000 \
  --restart unless-stopped \
  crop-recommendation-system

# Check logs
docker logs crop-app

# Stop the container
docker stop crop-app
```

#### 3. Docker Compose (Recommended)
Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  crop-app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=${SECRET_KEY:-your-secret-key-here}
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

# Optional: Add nginx reverse proxy
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - crop-app
    restart: unless-stopped
```

Run with Docker Compose:
```bash
docker-compose up -d
```

### 🦄 Gunicorn Production Server

#### 1. Install Gunicorn
```bash
pip install gunicorn
```

#### 2. Create Gunicorn Configuration
Create `gunicorn.conf.py`:
```python
# Gunicorn configuration file
bind = "0.0.0.0:5000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
```

#### 3. Run with Gunicorn
```bash
# Basic command
gunicorn --config gunicorn.conf.py app:app

# With environment variables
FLASK_ENV=production gunicorn --config gunicorn.conf.py app:app

# As a systemd service (create /etc/systemd/system/crop-app.service)
[Unit]
Description=Crop Recommendation System
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/your/app
Environment=FLASK_ENV=production
ExecStart=/path/to/venv/bin/gunicorn --config gunicorn.conf.py app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

### 🌐 Nginx Reverse Proxy

Create `/etc/nginx/sites-available/crop-app`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Static files (optional optimization)
    location /static {
        alias /path/to/your/app/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

Enable and restart Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/crop-app /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 📊 Monitoring and Health Checks

### Health Check Endpoint
The application provides a comprehensive health check at `/health`:

```json
{
    "status": "healthy",
    "models_loaded": true,
    "version": "2.0.0"
}
```

### Monitoring Script
Create `monitor.py`:
```python
#!/usr/bin/env python3
import requests
import time
import sys

def check_health(url="http://localhost:5000/health"):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'healthy':
                print(f"✅ Application is healthy - {data}")
                return True
        print(f"❌ Health check failed - Status: {response.status_code}")
        return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

if __name__ == "__main__":
    while True:
        if not check_health():
            sys.exit(1)
        time.sleep(30)  # Check every 30 seconds
```

## 🔧 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Find process using the port
   lsof -i :5001
   
   # Kill the process
   kill -9 <PID>
   
   # Or use a different port
   PORT=5002 python app.py
   ```

2. **Model Loading Warnings**
   - Scikit-learn version mismatches are common but usually don't affect functionality
   - Consider retraining models with the current scikit-learn version for production

3. **Memory Issues**
   - Monitor memory usage: `ps aux | grep python`
   - Consider using lighter ML models for low-memory environments

4. **Performance Optimization**
   - Use Gunicorn with multiple workers
   - Implement Redis caching for frequent predictions
   - Use a CDN for static assets

### Logs and Debugging
```bash
# Application logs
tail -f app.log

# Docker logs
docker logs -f crop-app

# System logs
journalctl -u crop-app -f
```

## 🔒 Security Considerations

1. **Environment Variables**: Store sensitive data in environment variables
2. **HTTPS**: Use SSL/TLS in production (Let's Encrypt recommended)
3. **Firewall**: Configure firewall rules to allow only necessary ports
4. **Updates**: Keep dependencies updated regularly
5. **Monitoring**: Implement security monitoring and logging

## 📈 Scaling

### Horizontal Scaling
- Use load balancer (nginx, HAProxy)
- Deploy multiple instances
- Use container orchestration (Kubernetes, Docker Swarm)

### Vertical Scaling
- Increase server resources (CPU, RAM)
- Optimize Gunicorn worker count
- Database optimization (if added)

## 🎯 Next Steps

1. **SSL Certificate**: Set up HTTPS with Let's Encrypt
2. **Monitoring**: Implement Prometheus + Grafana
3. **CI/CD**: Set up automated deployment pipeline
4. **Database**: Add database for prediction history
5. **API Rate Limiting**: Implement rate limiting for production use

---

**Need help?** Check the application logs or open an issue in the repository.
