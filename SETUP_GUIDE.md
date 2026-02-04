# 🚀 Aura Link - Quick Setup Guide

This guide will help you get your Aura Link video management platform up and running quickly.

## ✅ Prerequisites Checklist

Before proceeding, ensure you have:

- [ ] **Python 3.10+** installed (`python --version`)
- [ ] **PostgreSQL 13+** installed and running
- [ ] **Redis 6+** installed and running  
- [ ] **FFmpeg** installed (for video metadata extraction)
- [ ] **Git** (optional, for version control)

## 📦 Step 1: Install PostgreSQL

### Windows:
1. Download from: https://www.postgresql.org/download/windows/
2. Run installer and remember the password you set for `postgres` user
3. PostgreSQL runs automatically as a Windows service

### Verify Installation:
```bash
psql --version
```

## 📦 Step 2: Install Redis

### Windows:
1. Download from: https://github.com/microsoftarchive/redis/releases
2. Or use Windows Subsystem for Linux (WSL) and install via:
   ```bash
   sudo apt-get install redis-server
   sudo service redis-server start
   ```

### Verify Installation:
```bash
redis-cli ping
# Should respond with: PONG
```

## 📦 Step 3: Install FFmpeg

### Windows:
1. Download from: https://ffmpeg.org/download.html
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to system PATH

### Verify Installation:
```bash
ffmpeg -version
```

## 💻 Step 4: Setup Python Environment

```bash
# Navigate to project directory
cd "d:\Work\Aura Link\videosaas"

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## 🗄️ Step 5: Setup PostgreSQL Database

```bash
# Open PostgreSQL command line (psql)
psql -U postgres

# In psql, run:
CREATE DATABASE auralink_db;
CREATE USER auralink_user WITH PASSWORD 'change_this_password';
ALTER ROLE auralink_user SET client_encoding TO 'utf8';
ALTER ROLE auralink_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE auralink_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE auralink_db TO auralink_user;
\q
```

## ⚙️ Step 6: Configure Environment

```bash
# Copy environment template
copy .env.example .env

# Edit .env file and update:
```

**Important settings to change in `.env`:**

```env
SECRET_KEY=generate-a-strong-random-key-here
DEBUG=True
DB_NAME=auralink_db
DB_USER=auralink_user
DB_PASSWORD=change_this_password
DB_HOST=localhost
DB_PORT=5432
```

**To generate a secret key:**
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## 🏗️ Step 7: Initialize Database

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Load initial plan data (Free and Premium)
python manage.py loaddata apps/plans/fixtures/initial_plans.json

# Create admin user
python manage.py create_admin
```

**Default Admin Credentials:**
- Email: `jerinjaison07@gmail.com`
- Username: `admin`
- Password: `123`

**⚠️ IMPORTANT: Change these credentials in production!**

## 🎨 Step 8: Collect Static Files

```bash
python manage.py collectstatic --noinput
```

## 🚀 Step 9: Start Services

You'll need **4 terminal windows**:

### Terminal 1: Django Server
```bash
cd "d:\Work\Aura Link\videosaas"
venv\Scripts\activate
python manage.py runserver
```

### Terminal 2: Redis Server
```bash
# If not running as a service:
redis-server
```

### Terminal 3: Celery Worker
```bash
cd "d:\Work\Aura Link\videosaas"
venv\Scripts\activate
celery -A apps.tasks.celery worker -l info
```

### Terminal 4: Celery Beat (Periodic Tasks)
```bash
cd "d:\Work\Aura Link\videosaas"
venv\Scripts\activate
celery -A apps.tasks.celery beat -l info
```

## ✨ Step 10: Access the Application

Open your browser and navigate to:

- **Landing Page**: http://localhost:8000/
- **User Dashboard**: http://localhost:8000/dashboard/
- **Admin Portal**: http://localhost:8000/admin-portal/
- **Django Admin**: http://localhost:8000/admin/
- **API Health Check**: http://localhost:8000/health/
- **API Documentation**: http://localhost:8000/api/v1/

## 🧪 Testing the Setup

### 1. Login as Admin
- Go to http://localhost:8000/auth/web/login/
- Email: `jerinjaison07@gmail.com`
- Password: `123`

### 2. Check Health Endpoint
```bash
curl http://localhost:8000/health/
```

Should return:
```json
{
    "status": "healthy",
    "database": "connected",
    "redis": "connected"
}
```

### 3. Test API (JWT Authentication)
```bash
# Get JWT token
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"jerinjaison07@gmail.com","password":"123"}'

# Use token for API calls
curl http://localhost:8000/api/v1/plans/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 🐛 Troubleshooting

### Database Connection Error
```
Error: FATAL: role "auralink_user" does not exist
```

**Solution:** Recreate the database user in psql

### Redis Connection Error
```
Error: Connection refused (111)
```

**Solution:** Start Redis server
```bash
redis-server
```

### FFmpeg Not Found
```
FileNotFoundError: [Errno 2] No such file or directory: 'ffmpeg'
```

**Solution:** Install FFmpeg and add to PATH

### Import Errors
```
ModuleNotFoundError: No module named 'rest_framework'
```

**Solution:** Reinstall dependencies
```bash
pip install -r requirements.txt
```

### Migration Errors
```
django.db.migrations.exceptions.InconsistentMigrationHistory
```

**Solution:** Drop and recreate database
```bash
# In psql:
DROP DATABASE auralink_db;
CREATE DATABASE auralink_db;
GRANT ALL PRIVILEGES ON DATABASE auralink_db TO auralink_user;
```

Then rerun migrations:
```bash
python manage.py migrate
python manage.py loaddata apps/plans/fixtures/initial_plans.json
python manage.py create_admin
```

## 📚 Next Steps

1. **Change Admin Password**: Login and update password in user dashboard
2. **Create Test Users**: Register new accounts to test Free/Premium features
3. **Upload Videos**: Test video upload with different formats and sizes
4. **Test Playlist**: Upload multiple videos and test auto-play functionality
5. **Review Logs**: Check `logs/auralink.log` for application logs

## 🔐 Security Reminders

Before deploying to production:

1. ✅ Change `SECRET_KEY` in `.env`
2. ✅ Change admin password from default
3. ✅ Set `DEBUG=False`
4. ✅ Update `ALLOWED_HOSTS`  in production settings
5. ✅ Use strong PostgreSQL password
6. ✅ Enable HTTPS
7. ✅ Setup Sentry for error tracking
8. ✅ Configure S3 for cloud storage
9. ✅ Setup automated backups

## 📞 Support

If you encounter issues:

1. Check logs in `logs/auralink.log`
2. Review Django error pages (in DEBUG mode)
3. Check Celery worker output for background task errors
4. Contact: jerinjaison07@gmail.com

---

**🎉 Congratulations! Your Aura Link platform is ready to use!**
