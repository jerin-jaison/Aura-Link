# Phase 5 Testing Guide - Web Browser

## 🧪 Quick Test Checklist

### Prerequisites
- ✅ Staff account created and logged in
- ✅ At least one client created (access code generated)
- ✅ At least one video uploaded

---

## 📋 Test Scenario 1: Staff Assigns Videos to Client

### Step 1: Staff Login
1. Navigate to `/auth/web/login/`
2. Login as staff member
3. Should redirect to `/staff/`

### Step 2: Generate Access Code (if not done)
1. Go to **Access Codes** tab
2. Click "**Generate Access Code**"
3. **Copy the code** (e.g., `ABC12345`)

### Step 3: Upload Video (if not done)
1. Go to **Videos** tab
2. Upload a test video
3. Set rotation (try 90° for testing rotation feature)

### Step 4: Assign Video to Client
1. Click "**Assign**" on a video
2. Choose "**Assign to All Clients (Global)**"
3. Or select specific client
4. Click "**Save Assignment**"
5. Should see success message

---

## 📋 Test Scenario 2: Client Login & Auto-Play

### Step 1: Open Incognito/Private Window
- Chrome: `Ctrl+Shift+N`
- Firefox: `Ctrl+Shift+P`
- This simulates fresh client device

### Step 2: Navigate to Client Login
1. Go to `/auth/web/login/`
2. **Enter access code** (from Step 1.2)
3. Leave email/password blank
4. Click "**Login**"

### Step 3: Verify Auto-Redirect
- Should automatically redirect to `/client/player/`
- Should see loading screen briefly

### Step 4: Verify Video Auto-Play
Expected behavior:
- ✅ Loading screen disappears
- ✅ Video starts playing automatically
- ✅ Fullscreen mode attempted (click "Allow" if prompted)
- ✅ Rotation applied if set (video rotated 90°/180°/270°)
- ✅ No navbar visible
- ✅ Video loops/advances to next when finished

---

## 🔍 Test Cases

### Test Case 1: Single Video Loop
**Setup:**
- Assign 1 video to client
- Loop mode: `playlist` (default)

**Expected:**
- Video plays → ends → loops back and plays again

---

### Test Case 2: Multiple Video Playlist
**Setup:**
- Assign 3+ videos to client
- Loop mode: `playlist`

**Expected:**
- Video 1 plays → Video 2 → Video 3 → back to Video 1 (continuous loop)

---

### Test Case 3: Rotation Settings
**Setup:**
- Upload 4 videos
- Set rotations: 0°, 90°, 180°, 270°
- Assign all to client

**Expected:**
- Each video displays with correct rotation
- Portrait videos show correctly when rotated 90°/270°

---

### Test Case 4: Online Status
**Setup:**
- Client player is running
- Staff logged in on another tab

**Expected:**
- Staff dashboard → Clients tab
- Client should show "**Online**" status (green badge)
- "Last Seen" should update every 60 seconds

---

### Test Case 5: No Videos Assigned
**Setup:**
- Client has no videos assigned

**Expected:**
- Shows info overlay: "No Videos Assigned"
- Message: "Please contact your administrator..."

---

## 🐛 Troubleshooting

### Issue: Videos don't auto-play
**Check:**
1. Open browser console (`F12`)
2. Look for errors
3. Browser may block autoplay with sound
4. **Solution**: Click anywhere on screen to allow playback

### Issue: 404 on `/api/client/playlist/`
**Check:**
1. Verify URLs are set up in `config/urls.py`
2. Run: `python manage.py check`
3. Check migration status

### Issue: Empty playlist returned
**Check:**
1. Videos are assigned to THIS client
2. Videos are active (`is_active=True`)
3. Check staff_profile has videos uploaded

### Issue: No rotation applied
**Check:**
1. Video.rotation field exists in database
2. Migration applied: `0006_video_rotation.py`
3. JavaScript console for CSS transform errors

### Issue: Client shows offline in staff dashboard
**Check:**
1. Heartbeat API is being called (check Network tab in browser)
2. No CSRF token errors
3. ClientAccount.last_seen is updating

---

## 🎯 Quick Commands for Testing

### Check System Status
```bash
cd "d:\Work\Aura LInk\videosaas"
python manage.py check
```

### View Migrations Status
```bash
python manage.py showmigrations
```

### Create Test Staff User
```bash
python manage.py shell
from apps.accounts.models import User, StaffProfile
user = User.objects.create_user(
    email='staff@test.com',
    password='test123',
    user_type='STAFF'
)
StaffProfile.objects.create(
    user=user,
    max_clients=2,
    max_storage_gb=5
)
```

### View Client API Response
```bash
# After client logs in, test API directly
curl -X GET http://127.0.0.1:8000/api/client/playlist/ \
  -H "Cookie: sessionid=YOUR_SESSION_ID"
```

---

## ✅ Success Criteria

Phase 5 is working if:
- [x] Staff can assign videos to clients
- [x] Client logs in with access code → redirects to player
- [x] Videos auto-play without user interaction
- [x] Playlist loops continuously
- [x] Rotation applied correctly
- [x] Heartbeat updates online status
- [x] No navbar in client player
- [x] Error messages shown when no videos

---

## 📊 Browser Developer Tools Checks

### Console Tab (F12 → Console)
Look for:
```
[Aura Link] Initializing player...
[Aura Link] Loaded 3 videos
[Aura Link] Loop mode: playlist
[Aura Link] Loading video 1/3: My Video
[Aura Link] Applying rotation: 90°
[Aura Link] Playback started
[Aura Link] Heartbeat sent successfully
```

### Network Tab (F12 → Network)
Should see:
- `GET /api/client/playlist/` → 200 OK
- `POST /api/client/heartbeat/` → 200 OK (every 60s)

### Application Tab (F12 → Application → Cookies)
Should have:
- `sessionid` cookie (client logged in)
- `csrftoken` cookie

---

## 🚀 Next Steps After Testing

Once web testing passes:
1. ✅ All features work in browser
2. ➡️ Test on actual Android TV with Fully Kiosk
3. ➡️ Implement Phase 6 (Admin approval, payments)
4. ➡️ Build native Android app (optional)

---

**Ready to test? Start with Scenario 1!** 🎬
