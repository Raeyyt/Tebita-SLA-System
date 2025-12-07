# Deploy Tebita SLA System
Write-Host "Starting Deployment..." -ForegroundColor Green

# 1. Pull latest images
Write-Host "Pulling latest images..."
docker-compose pull

# 2. Start services (Build if necessary)
Write-Host "Starting services..."
docker-compose up -d --build --remove-orphans

# 3. Cleanup unused images
Write-Host "Cleaning up unused images..."
docker system prune -f

Write-Host "Deployment Complete!" -ForegroundColor Green
Write-Host "Access the application at http://localhost"
