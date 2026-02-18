# Aura Link - Video Management SaaS Platform

A production-ready, enterprise-grade video management SaaS application built with Django, PostgreSQL, and Bootstrap 5.

## 🚀 Features

### Core Functionality
- **Dual Authentication**: Session-based for web, JWT for mobile/TV apps
- **Role-Based Access Control**: Admin and User roles with strict permissions
- **Plan-Based Features**: Free and Premium tiers with different limits
- **Video Management**: Upload (Local/Cloud), organize, and play videos with playlists
- **Background Processing**: Celery tasks for metadata extraction and cleanup
- **Audit Logging**: Complete trail of all administrative actions (Video Archive, User Block, etc.)

### 🆕 Recent Updates
- **Admin Dashboard Enhancements**:
  - **Deletion Requests**: Centralized dashboard to manage user requests for deleting admin-uploaded content.
  - **Cloud Video Management**: Specialized view for managing user-uploaded cloud videos.
  - **Notification System**: Modern, JavaScript-based toast notifications replacing standard static messages.
  - **Security Hardening**:
    - **Secure Logout**: Custom logout flow preventing back-button caching.
    - **Admin Protection**: Explicit feedback for unauthorized access attempts.
    - **CSRF Fixes**: Robust session handling to prevent CSRF errors on re-login.
  - **Video Protection**: Enhanced logic for Admin-uploaded vs. User-uploaded content (deletion protection).

### 🔮 Up Next (Future Updates)
1. **User Profile Management**:
   - Change Password functionality.
   - OTP verification for Forget Password flow.
2. **Enhanced Authentication**:
   - OTP verification for Signup process.
3. **Advanced Billing**:
   - Dedicated payment pages for Users.
   - Comprehensive Transaction History interface for Admins.

## 📋 Prerequisites

Before running this application, ensure you have:

- Python 3.10 or higher
- PostgreSQL 13 or higher (running and accessible)
- Redis 6 or higher (for Celery and caching)
- FFmpeg (for video metadata extraction)

## 🛠️ Installation

### 1. Clone and Setup Virtual Environment

```bash
cd "d:\Work\Aura Link\videosaas"
python -m venv venv
venv\Scripts\activate  # On Windows
# source venv/bin/activate  # On Linux/Mac
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Create PostgreSQL Database

```sql
CREATE DATABASE auralink_db;
CREATE USER auralink_user WITH PASSWORD 'your_password';
ALTER ROLE auralink_user SET client_encoding TO 'utf8';
ALTER ROLE auralink_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE auralink_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE auralink_db TO auralink_user;
```

### 4. Configure Environment

Copy `.env.example` to `.env` and update with your settings:

```bash
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac
```

Edit `.env`:
```
DB_NAME=auralink_db
DB_USER=auralink_user
DB_PASSWORD=your_password
SECRET_KEY=your-secret-key-here
```

###  5. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Load Initial Data

```bash
python manage.py loaddata initial_plans
```

### 7. Create Superuser

```bash
python manage.py createsuperuser
# Or use the auto-creation command:
python manage.py create_admin
```

**Default Admin Credentials** (from auto-creation):
- Email: `jerinjaison07@gmail.com`
- Username: `admin`
- Password: `123`

### 8. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### 9. Start Redis (if not already running)

```bash
redis-server
```

### 10. Start Celery Worker

Open a new terminal:

```bash
celery -A config worker -l info
```

### 11. Start Celery Beat (for periodic tasks)

Open another terminal:

```bash
celery -A config beat -l info
```

### 12. Run Development Server

```bash
python manage.py runserver
```

The application will be available at: `http://localhost:8000/`

## 📁 Project Structure

```
videosaas/
├── config/                 # Django configuration
├── apps/                   # Django applications
│   ├── accounts/          # User authentication & management
│   ├── plans/             # Subscription plans
│   ├── videos/            # Video upload & management
│   ├── dashboard/         # User & admin dashboards
│   ├── subscriptions/     # Subscription lifecycle
│   ├── audit/             # Admin action logging
│   └── tasks/             # Celery background tasks
├── templates/              # HTML templates
├── static/                 # Static files
├── media/                  # User uploads
└── manage.py              # Django management script
```

## 🔑 Key Endpoints

### Web Pages
- `/` - Landing page
- `/auth/web/login/` - Web login
- `/auth/web/signup/` - User registration
- `/dashboard/` - User dashboard
- `/admin-portal/` - Admin panel

### API (v1)
- `/api/v1/auth/login/` - JWT login (mobile/TV)
- `/api/v1/videos/upload/` - Upload video
- `/api/v1/videos/` - List user videos
- `/health/` - Health check

## 🎥 Video Constraints

### Free Plan
- Max file size: 100MB per video
- Max duration: 10 minutes
- Allowed formats: MP4 only
- Cloud upload: ❌

### Premium Plan
- Max file size: 500MB per video
- Max duration: 60 minutes
- Allowed formats: MP4, MKV, WebM
- Cloud upload: ✅
- Playlist loop: ✅

## 👨‍💼 Admin Capabilities

Admins can:
- Manually assign plans to users
- Delete user accounts
- View and disable any video
- Toggle feature flags per user
- View audit logs of all actions
- Manage subscription lifecycle
- **NEW**: Manage deletion requests for admin content
- **NEW**: Manage user cloud videos

## 🔒 Security Features

- Bcrypt password hashing (12 rounds)
- HTTPOnly session cookies
- JWT with refresh token rotation
- CSRF protection (Enhanced)
- Rate limiting & Login throttling
- **NEW**: Anti-caching headers for secure logout

## 📊 Monitoring

### Health Check
```bash
curl http://localhost:8000/health/
```

### Metrics Dashboard
Access at: `/admin-portal/metrics/` (admin only)

## 📝 License

Proprietary - All Rights Reserved

## 👤 Support

For issues or questions, contact: jerinjaison07@gmail.com

---

**Built with ❤️ for real-world production use.**

cd videosaas
venv\Scripts\activate 
python manage.py runserver 