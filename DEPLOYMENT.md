# Deployment Guide for Arat Kilo Gibi Gubae Quiz System

## Production Deployment Options

### Option 1: Docker Deployment (Recommended)

#### Prerequisites
- Docker and Docker Compose installed
- Domain name (optional)

#### Step 1: Create Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data docs

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Run the application
CMD ["python", "scripts/main.py"]
```

#### Step 2: Create docker-compose.yml
```yaml
version: '3.8'

services:
  quiz-app:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./docs:/app/docs
    environment:
      - PYTHONPATH=/app
      - LOG_LEVEL=INFO
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
      - ./:/usr/share/nginx/html:ro
    depends_on:
      - quiz-app
    restart: unless-stopped

volumes:
  data:
  docs:
```

#### Step 3: Create nginx.conf
```nginx
events {
    worker_connections 1024;
}

http {
    upstream quiz_backend {
        server quiz-app:8000;
    }

    server {
        listen 80;
        server_name your-domain.com;
        
        # Redirect HTTP to HTTPS (uncomment for SSL)
        # return 301 https://$server_name$request_uri;

        # Serve static files
        location / {
            root /usr/share/nginx/html;
            try_files $uri $uri/ /index.html;
            
            # Cache static assets
            location ~* \.(css|js|png|jpg|jpeg|gif|ico|svg)$ {
                expires 1y;
                add_header Cache-Control "public, immutable";
            }
        }

        # Proxy API requests
        location /api/ {
            proxy_pass http://quiz_backend/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    }

    # SSL Configuration (uncomment for HTTPS)
    # server {
    #     listen 443 ssl http2;
    #     server_name your-domain.com;
    #     
    #     ssl_certificate /etc/nginx/ssl/cert.pem;
    #     ssl_certificate_key /etc/nginx/ssl/key.pem;
    #     
    #     # SSL settings
    #     ssl_protocols TLSv1.2 TLSv1.3;
    #     ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    #     ssl_prefer_server_ciphers off;
    #     
    #     # Same configuration as HTTP
    #     location / {
    #         root /usr/share/nginx/html;
    #         try_files $uri $uri/ /index.html;
    #     }
    #     
    #     location /api/ {
    #         proxy_pass http://quiz_backend/;
    #         proxy_set_header Host $host;
    #         proxy_set_header X-Real-IP $remote_addr;
    #         proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    #         proxy_set_header X-Forwarded-Proto $scheme;
    #     }
    # }
}
```

#### Step 4: Deploy
```bash
# Build and start containers
docker-compose up -d

# View logs
docker-compose logs -f

# Stop containers
docker-compose down
```

### Option 2: Traditional Server Deployment

#### Prerequisites
- Ubuntu 20.04+ or CentOS 8+
- Python 3.8+
- Nginx (optional but recommended)

#### Step 1: Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3 python3-pip python3-venv nginx -y

# Create application user
sudo useradd -m -s /bin/bash quizapp
sudo usermod -aG sudo quizapp
```

#### Step 2: Application Deployment
```bash
# Switch to application user
sudo su - quizapp

# Clone repository
git clone <your-repo-url> /home/quizapp/app
cd /home/quizapp/app

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Test the application
python scripts/main.py
```

#### Step 3: Create Systemd Service
```bash
sudo tee /etc/systemd/system/quiz-app.service > /dev/null <<EOF
[Unit]
Description=Arat Kilo Gibi Gubae Quiz App
After=network.target

[Service]
Type=simple
User=quizapp
WorkingDirectory=/home/quizapp/app
Environment=PATH=/home/quizapp/app/venv/bin
Environment=PYTHONPATH=/home/quizapp/app
ExecStart=/home/quizapp/app/venv/bin/python scripts/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable quiz-app
sudo systemctl start quiz-app
sudo systemctl status quiz-app
```

#### Step 4: Configure Nginx
```bash
sudo tee /etc/nginx/sites-available/quiz-app > /dev/null <<EOF
server {
    listen 80;
    server_name your-domain.com;

    root /home/quizapp/app;
    index index.html;

    location / {
        try_files \$uri \$uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/quiz-app /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Option 3: Cloud Platform Deployment

#### Heroku Deployment
1. Create `Procfile`:
```
web: python scripts/main.py
```

2. Create `runtime.txt`:
```
python-3.11.0
```

3. Deploy:
```bash
heroku create your-app-name
git push heroku main
```

#### PythonAnywhere Deployment
1. Upload files to PythonAnywhere
2. Create virtual environment
3. Install dependencies
4. Configure web app to run `scripts/main.py`
5. Set up static files mapping

## Environment Variables

Create `.env` file for production:
```bash
# Application settings
LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=8000

# Security
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=your-domain.com,localhost

# Database (if using)
DATABASE_URL=sqlite:///data/quiz.db

# External services
REDIS_URL=redis://localhost:6379
```

## Monitoring and Maintenance

### Log Management
```bash
# View application logs
sudo journalctl -u quiz-app -f

# View Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Backup Strategy
```bash
#!/bin/bash
# backup.sh - Backup script

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/quiz-app"
APP_DIR="/home/quizapp/app"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup data files
tar -czf $BACKUP_DIR/data_$DATE.tar.gz -C $APP_DIR data/

# Backup database (if using)
# mysqldump -u user -p database > $BACKUP_DIR/db_$DATE.sql

# Clean old backups (keep 30 days)
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

### Health Monitoring
Add to your application:
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }
```

## Security Considerations

1. **HTTPS**: Always use SSL in production
2. **Firewall**: Configure firewall to allow only necessary ports
3. **Updates**: Keep system and dependencies updated
4. **Backups**: Regular automated backups
5. **Monitoring**: Set up alerts for downtime
6. **Rate Limiting**: Implement API rate limiting
7. **Input Validation**: Already implemented in data_validator.py

## Performance Optimization

1. **Caching**: Use Redis for caching API responses
2. **CDN**: Serve static assets via CDN
3. **Database**: Use PostgreSQL for better performance
4. **Compression**: Enable gzip compression in Nginx
5. **Load Balancing**: Multiple app instances behind load balancer

## Troubleshooting

### Common Issues

**Application won't start:**
- Check logs: `sudo journalctl -u quiz-app`
- Verify Python path and dependencies
- Check file permissions

**502 Bad Gateway:**
- Check if app is running on port 8000
- Verify Nginx configuration
- Check firewall settings

**Static files not loading:**
- Verify file permissions
- Check Nginx static file configuration
- Clear browser cache

### Performance Issues

1. Monitor memory usage
2. Check database query performance
3. Analyze Nginx access logs
4. Use profiling tools to identify bottlenecks
