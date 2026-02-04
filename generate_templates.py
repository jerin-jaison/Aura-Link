"""
Template generator for Aura Link.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).parent

TEMPLATES = {
    'templates/base.html': '''<!DOCTYPE html>
<html lang="en" data-bs-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Aura Link - Video Management Platform{% endblock %}</title>
    
    <!-- Bootstrap 5 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css">
    
    {% load static %}
    <link rel="stylesheet" href="{% static 'css/main.css' %}">
    
    {% block extra_css %}{% endblock %}
</head>
<body>
    {% include 'partials/navbar.html' %}
    
    <main class="container-fluid px-4 py-4">
        {% block content %}{% endblock %}
    </main>
    
    {% include 'partials/footer.html' %}
    
    <!-- Bootstrap 5 JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="{% static 'js/main.js' %}"></script>
    
    {% block extra_js %}{% endblock %}
</body>
</html>
''',

    'templates/partials/navbar.html': '''<nav class="navbar navbar-expand-lg navbar-dark bg-dark border-bottom border-secondary">
    <div class="container-fluid">
        <a class="navbar-brand fw-bold" href="/">
            <i class="bi bi-play-circle-fill text-primary"></i> Aura Link
        </a>
        
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
            <span class="navbar-toggler-icon"></span>
        </button>
        
        <div class="collapse navbar-collapse" id="navbarNav">
            <ul class="navbar-nav ms-auto">
                {% if user.is_authenticated %}
                    <li class="nav-item">
                        <a class="nav-link" href="{% url 'user_dashboard' %}">
                            <i class="bi bi-speedometer2"></i> Dashboard
                        </a>
                    </li>
                    {% if user.is_admin %}
                    <li class="nav-item">
                        <a class="nav-link" href="{% url 'admin_dashboard' %}">
                            <i class="bi bi-shield-lock"></i> Admin Portal
                        </a>
                    </li>
                    {% endif %}
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" data-bs-toggle="dropdown">
                            <i class="bi bi-person-circle"></i> {{ user.email }}
                        </a>
                        <ul class="dropdown-menu dropdown-menu-end">
                            <li><span class="dropdown-item-text small">Plan: {{ user.plan.name }}</span></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="{% url 'logout' %}">Logout</a></li>
                        </ul>
                    </li>
                {% else %}
                    <li class="nav-item">
                        <a class="nav-link" href="{% url 'login' %}">Login</a>
                    </li>
                {% endif %}
            </ul>
        </div>
    </div>
</nav>
''',

    'templates/partials/footer.html': '''<footer class="bg-dark text-light py-4 mt-5 border-top border-secondary">
    <div class="container">
        <div class="row">
            <div class="col-md-6">
                <h5><i class="bi bi-play-circle-fill text-primary"></i> Aura Link</h5>
                <p class="text-muted">Enterprise Video Management Platform</p>
            </div>
            <div class="col-md-6 text-md-end">
                <p class="text-muted mb-0">&copy; 2026 Aura Link. All rights reserved.</p>
            </div>
        </div>
    </div>
</footer>
''',

    'templates/landing.html': '''{% extends 'base.html' %}

{% block content %}
<div class="container py-5">
    <!-- Hero Section -->
    <div class="row align-items-center mb-5">
        <div class="col-lg-6">
            <h1 class="display-3 fw-bold mb-4">
                Professional Video<br>
                <span class="text-primary">Management</span>
            </h1>
            <p class="lead text-muted mb-4">
                Upload, organize, and share your videos with ease. Built for creators, teams, and enterprises.
            </p>
            <a href="{% url 'login' %}" class="btn btn-primary btn-lg me-2">
                <i class="bi bi-box-arrow-in-right"></i> Get Started
            </a>
        </div>
        <div class="col-lg-6">
            <div class="card bg-secondary border-0 shadow">
                <div class="card-body text-center py-5">
                    <i class="bi bi-play-circle display-1 text-primary"></i>
                    <h3 class="mt-3">Ready to Upload</h3>
                    <p class="text-muted">Secure, fast, reliable</p>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Features -->
    <div class="row g-4 mb-5">
        <div class="col-md-4">
            <div class="card bg-dark border-secondary h-100">
                <div class="card-body text-center">
                    <i class="bi bi-cloud-upload display-4 text-primary mb-3"></i>
                    <h5>Cloud Storage</h5>
                    <p class="text-muted">Upload to cloud or local storage</p>
                </div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card bg-dark border-secondary h-100">
                <div class="card-body text-center">
                    <i class="bi bi-collection-play display-4 text-primary mb-3"></i>
                    <h5>Smart Playlists</h5>
                    <p class="text-muted">Auto-play and loop controls</p>
                </div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card bg-dark border-secondary h-100">
                <div class="card-body text-center">
                    <i class="bi bi-shield-check display-4 text-primary mb-3"></i>
                    <h5>Secure & Private</h5>
                    <p class="text-muted">Enterprise-grade security</p>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Pricing -->
    <div class="row g-4">
        <div class="col-md-6">
            <div class="card bg-secondary border-0 h-100">
                <div class="card-body p-4">
                    <h3 class="mb-3">Free</h3>
                    <h2 class="display-5 mb-4">$0<small class="text-muted">/mo</small></h2>
                    <ul class="list-unstyled mb-4">
                        <li class="mb-2"><i class="bi bi-check-circle-fill text-success"></i> 5 videos</li>
                        <li class="mb-2"><i class="bi bi-check-circle-fill text-success"></i> 100MB per video</li>
                        <li class="mb-2"><i class="bi bi-check-circle-fill text-success"></i> 500MB total storage</li>
                        <li class="mb-2"><i class="bi bi-x-circle-fill text-danger"></i> Cloud upload</li>
                    </ul>
                    <a href="{% url 'login' %}" class="btn btn-outline-light w-100">Start Free</a>
                </div>
            </div>
        </div>
        <div class="col-md-6">
            <div class="card bg-primary border-0 h-100 shadow-lg">
                <div class="card-body p-4">
                    <span class="badge bg-warning text-dark mb-2">Popular</span>
                    <h3 class="mb-3">Premium</h3>
                    <h2 class="display-5 mb-4">$9.99<small class="text-light">/mo</small></h2>
                    <ul class="list-unstyled mb-4">
                        <li class="mb-2"><i class="bi bi-check-circle-fill text-warning"></i> Unlimited videos</li>
                        <li class="mb-2"><i class="bi bi-check-circle-fill text-warning"></i> 500MB per video</li>
                        <li class="mb-2"><i class="bi bi-check-circle-fill text-warning"></i> 50GB total storage</li>
                        <li class="mb-2"><i class="bi bi-check-circle-fill text-warning"></i> Cloud upload</li>
                        <li class="mb-2"><i class="bi bi-check-circle-fill text-warning"></i> Playlist loop</li>
                    </ul>
                    <a href="{% url 'login' %}" class="btn btn-warning w-100">Upgrade Now</a>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
''',

    'templates/auth/login.html': '''{% extends 'base.html' %}

{% block title %}Login - Aura Link{% endblock %}

{% block content %}
<div class="container">
    <div class="row justify-content-center py-5">
        <div class="col-md-5">
            <div class="card bg-dark border-secondary shadow">
                <div class="card-body p-5">
                    <h2 class="text-center mb-4">
                        <i class="bi bi-play-circle-fill text-primary"></i><br>
                        Login to Aura Link
                    </h2>
                    
                    <form method="post">
                        {% csrf_token %}
                        
                        <div class="mb-3">
                            <label class="form-label">Email</label>
                            <input type="email" name="username" class="form-control" required autofocus>
                        </div>
                        
                        <div class="mb-4">
                            <label class="form-label">Password</label>
                            <input type="password" name="password" class="form-control" required>
                        </div>
                        
                        <button type="submit" class="btn btn-primary w-100 mb-3">
                            <i class="bi bi-box-arrow-in-right"></i> Login
                        </button>
                    </form>
                    
                    <p class="text-center text-muted mb-0">
                        <small>Default Admin: admin / 123</small>
                    </p>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
''',

    'templates/dashboard/user_dashboard.html': '''{% extends 'base.html' %}

{% block  title %}Dashboard - Aura Link{% endblock %}

{% block content %}
<div class="container-fluid">
    <div class="row mb-4">
        <div class="col">
            <h2><i class="bi bi-speedometer2"></i> Dashboard</h2>
            <p class="text-muted">Welcome back, {{ user.email }}</p>
        </div>
    </div>
    
    <!-- Stats -->
    <div class="row g-3 mb-4">
        <div class="col-md-3">
            <div class="card bg-primary text-white">
                <div class="card-body">
                    <h6>Current Plan</h6>
                    <h3>{{ user.plan.name }}</h3>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card bg-secondary">
                <div class="card-body">
                    <h6>Total Videos</h6>
                    <h3>{{ videos.count }}</h3>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card bg-secondary">
                <div class="card-body">
                    <h6>Storage Used</h6>
                    <h3>{{ total_storage|filesizeformat }}</h3>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card bg-secondary">
                <div class="card-body text-end">
                    <button class="btn btn-warning" data-bs-toggle="modal" data-bs-target="#uploadModal">
                        <i class="bi bi-cloud-upload"></i> Upload Video
                    </button>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Video Grid -->
    <div class="card bg-dark border-secondary">
        <div class="card-header">
            <h5 class="mb-0"><i class="bi bi-collection-play"></i> My Videos</h5>
        </div>
        <div class="card-body">
            {% if videos %}
            <div class="row g-3">
                {% for video in videos %}
                <div class="col-md-4">
                    <div class="card bg-secondary">
                        <div class="card-body">
                            <h6>{{ video.title }}</h6>
                            <p class="text-muted small mb-2">
                                <i class="bi bi-file-earmark-play"></i> {{ video.file_size_mb }}MB
                                <span class="ms-2"><i class="bi bi-clock"></i> {{ video.duration_minutes }}min</span>
                            </p>
                            <span class="badge bg-info">{{ video.format }}</span>
                            <span class="badge bg-success">{{ video.storage_type }}</span>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
            {% else %}
            <div class="text-center py-5 text-muted">
                <i class="bi bi-inbox display-1"></i>
                <p>No videos yet. Upload your first video!</p>
            </div>
            {% endif %}
        </div>
    </div>
</div>

<!-- Upload Modal -->
<div class="modal fade" id="uploadModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content bg-dark">
            <div class="modal-header border-secondary">
                <h5 class="modal-title">Upload Video</h5>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <form id="uploadForm" enctype="multipart/form-data">
                    {% csrf_token %}
                    <div class="mb-3">
                        <label class="form-label">Title</label>
                        <input type="text" name="title" class="form-control" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Video File</label>
                        <input type="file" name="video_file" class="form-control" accept="video/*" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Storage</label>
                        <select name="storage_type" class="form-select">
                            <option value="LOCAL">Local Storage</option>
                            {% if user.plan.cloud_upload_allowed %}
                            <option value="CLOUD">Cloud Storage</option>
                            {% endif %}
                        </select>
                    </div>
                    <button type="submit" class="btn btn-primary w-100">
                        <i class="bi bi-cloud-upload"></i> Upload
                    </button>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script src="{% static 'js/upload.js' %}"></script>
{% endblock %}
''',

    'templates/dashboard/admin_dashboard.html': '''{% extends 'base.html' %}

{% block title %}Admin Dashboard - Aura Link{% endblock %}

{% block content %}
<div class="container-fluid">
    <div class="row mb-4">
        <div class="col">
            <h2><i class="bi bi-shield-lock"></i> Admin Dashboard</h2>
        </div>
    </div>
    
    <!-- Stats -->
    <div class="row g-3 mb-4">
        <div class="col-md-4">
            <div class="card bg-primary">
                <div class="card-body">
                    <h6>Total Users</h6>
                    <h2>{{ total_users }}</h2>
                </div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card bg-success">
                <div class="card-body">
                    <h6>Total Videos</h6>
                    <h2>{{ total_videos }}</h2>
                </div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card bg-warning text-dark">
                <div class="card-body">
                    <h6>Quick Actions</h6>
                    <a href="/admin/" class="btn btn-dark btn-sm">Django Admin</a>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Recent Actions -->
    <div class="card bg-dark border-secondary">
        <div class="card-header">
            <h5 class="mb-0"><i class="bi bi-journal-text"></i> Recent Admin Actions</h5>
        </div>
        <div class="card-body">
            <div class="table-responsive">
                <table class="table table-dark table-hover">
                    <thead>
                        <tr>
                            <th>Action</th>
                            <th>Admin</th>
                            <th>Target</th>
                            <th>Time</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for log in recent_logs %}
                        <tr>
                            <td><span class="badge bg-info">{{ log.action_type }}</span></td>
                            <td>{{ log.admin.email }}</td>
                            <td>{{ log.target_model }}</td>
                            <td class="text-muted small">{{ log.timestamp|timesince }} ago</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>
{% endblock %}
''',

    'templates/errors/403.html': '''{% extends 'base.html' %}

{% block title %}Access Denied{% endblock %}

{% block content %}
<div class="container text-center py-5">
    <i class="bi bi-shield-x display-1 text-danger"></i>
    <h1 class="mt-4">Access Denied</h1>
    <p class="lead text-muted">You don't have permission to access this resource.</p>
    <a href="/" class="btn btn-primary">Go Home</a>
</div>
{% endblock %}
''',

    'templates/errors/404.html': '''{% extends 'base.html' %}

{% block title %}Page Not Found{% endblock %}

{% block content %}
<div class="container text-center py-5">
    <i class="bi bi-exclamation-triangle display-1 text-warning"></i>
    <h1 class="mt-4">Page Not Found</h1>
    <p class="lead text-muted">The page you're looking for doesn't exist.</p>
    <a href="/" class="btn btn-primary">Go Home</a>
</div>
{% endblock %}
''',

    'templates/errors/500.html': '''{% extends 'base.html' %}

{% block title %}Server Error{% endblock %}

{% block content %}
<div class="container text-center py-5">
    <i class="bi bi-exclamation-octagon display-1 text-danger"></i>
    <h1 class="mt-4">Server Error</h1>
    <p class="lead text-muted">Something went wrong. We're working on it.</p>
    <a href="/" class="btn btn-primary">Go Home</a>
</div>
{% endblock %}
''',

    # CSS
    'static/css/main.css': '''/* Aura Link Custom Styles */

:root {
    --bs-body-bg: #0d1117;
    --bs-dark-bg-subtle: #161b22;
}

body {
    background-color: var(--bs-body-bg);
    min-height: 100vh;
}

.navbar {
    backdrop-filter: blur(10px);
}

.card {
    transition: transform 0.2s, box-shadow 0.2s;
}

.card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.btn {
    transition: all 0.2s;
}

.btn:hover {
    transform: translateY(-1px);
}

/* Video Grid */
.video-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1rem;
}

/* Upload Progress */
.upload-progress {
    height: 4px;
    background: linear-gradient(90deg, #0d6efd, #6610f2);
    transition: width 0.3s;
}
''',

    # JavaScript
    'static/js/main.js': '''// Aura Link Main JavaScript

// Auto-dismiss alerts
setTimeout(() => {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        const bsAlert = new bootstrap.Alert(alert);
        bsAlert.close();
    });
}, 5000);

// Add smooth scrolling
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth' });
        }
    });
});
''',

    'static/js/upload.js': '''// Video Upload Handler

document.addEventListener('DOMContentLoaded', () => {
    const uploadForm = document.getElementById('uploadForm');
    
    if (uploadForm) {
        uploadForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData(uploadForm);
            const submitBtn = uploadForm.querySelector('button[type="submit"]');
            
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Uploading...';
            
            try {
                const response = await fetch('/api/v1/videos/upload/', {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                    }
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    alert('Video uploaded successfully!');
                    location.reload();
                } else {
                    alert('Error: ' + (data.error || 'Upload failed'));
                }
            } catch (error) {
                alert('Network error: ' + error.message);
            } finally {
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="bi bi-cloud-upload"></i> Upload';
            }
        });
    }
});
''',

    'static/js/playlist.js': '''// Playlist Auto-Play

class VideoPlaylist {
    constructor(videos, loopEnabled = false) {
        this.videos = videos;
        this.currentIndex = 0;
        this.loopEnabled = loopEnabled;
    }
    
    play() {
        if (this.currentIndex < this.videos.length) {
            const video = this.videos[this.currentIndex];
            this.playVideo(video);
        } else if (this.loopEnabled) {
            this.currentIndex = 0;
            this.play();
        } else {
            console.log('Playlist ended');
        }
    }
    
    playVideo(video) {
        console.log('Playing:', video.title);
        // Implement video player logic here
    }
    
    next() {
        this.currentIndex++;
        this.play();
    }
    
    previous() {
        if (this.currentIndex > 0) {
            this.currentIndex--;
            this.play();
        }
    }
}
''',
}

def create_files():
    """Create all template files."""
    for file_path, content in TEMPLATES.items():
        full_path = BASE_DIR / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"[OK] Created: {file_path}")

if __name__ == '__main__':
    print("Generating Templates and Static Files...")
    create_files()
    print("\n[SUCCESS] All templates generated!")
