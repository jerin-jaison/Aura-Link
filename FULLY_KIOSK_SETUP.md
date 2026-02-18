# Fully Kiosk Browser Setup Guide for Android TV/Firestick

## 🎯 Overview
This guide shows how to configure your Android TV or Amazon Firestick to auto-play Aura Link videos using **Fully Kiosk Browser**.

---

## 📱 Step 1: Install Fully Kiosk Browser

### On Android TV:
1. Open **Google Play Store** on your Android TV
2. Search for "**Fully Kiosk Browser**"
3. Install the app (Free version works fine)

### On Amazon Fire TV/Firestick:
1. Go to **Settings** → **My Fire TV** → **Developer Options**
2. Enable "**Apps from Unknown Sources**"
3. Download **Downloader** app from Amazon Appstore
4. Use code: **`https://www.fully-kiosk.com/apk/`**
5. Download and install Fully Kiosk Browser APK

---

## 🔧 Step 2: Configure Fully Kiosk Browser

1. **Launch Fully Kiosk Browser** on your TV

2. **Enter Settings** (usually via menu button or settings icon)

3. **Configure these settings**:

### A. Start URL
```
https://yourdomain.com/client/player/
```
Replace with your actual server URL.

### B. Kiosk Mode Settings
- ✅ **Enable Kiosk Mode** → ON
- ✅ **Hide Navigation Bar** → ON  
- ✅ **Hide Status Bar** → ON
- ✅ **Keep Screen On** → ON
- ✅ **Prevent Screen Sleep** → ON

### C. Remote Administration (Optional)
- **Remote Admin Password**: Set a password
- **Remote Admin Port**: 2323 (default)
- This allows remote control/monitoring

### D. Auto-Start Settings
- ✅ **Autostart on Boot** → ON
- ✅ **Bring to Front on Start** → ON
- **Start Delay**: 10 seconds (wait for network)

### E. Screensaver Settings
- ❌ **Enable Screensaver** → OFF
- ❌ **Daydream** → OFF

### F. Motion Detection (Optional)
- If you want to wake TV on motion → Enable
- Otherwise → Disable

---

## 🔐 Step 3: Login to Aura Link

1. **The browser will load** your player URL
2. **First time** → You'll see login screen
3. **Enter Access Code** provided by your staff admin
4. **Submit** → Player will start automatically
5. **Session persists** (30 days) → No need to login again

---

## 🔄 Step 4: Restart & Test

1. **Restart your Android TV/Firestick**
2. Wait for device to boot (~30 seconds)
3. **Fully Kiosk Browser should auto-launch**
4. **Videos should auto-play** in fullscreen

---

## ✅ Verification Checklist

After setup, verify:
- [ ] TV boots → Fully Kiosk launches automatically
- [ ] Videos auto-play without user interaction
- [ ] Fullscreen mode (no browser chrome)
- [ ] Screen stays always-on (no sleep)
- [ ] Videos loop/advance as configured
- [ ] Rotation works correctly (if set by staff)

---

## 🛠️ Advanced Settings (Optional)

### Remote Access
Once configured, you can access your TV remotely:
```
http://<TV_IP_ADDRESS>:2323/?cmd=...
```

**Useful Commands**:
- Reload page: `/?cmd=reloadPage`
- Clear cache: `/?cmd=clearCache`
- Screenshot: `/?cmd=getScreenshot`

### Prevent TV from Turning Off
Some TVs still sleep even with "Keep Screen On". Solutions:

**Option A**: Use Fully Kiosk's **Keep Awake** feature
- Settings → Display → **Prevent Display From Sleep** → ON

**Option B**: USB Power Trick (Fire TV only)
- Power Fire TV via wall adapter (not TV USB)
- This keeps it always powered

**Option C**: HDMI-CEC Settings
- TV Settings → **HDMI-CEC** → Enable
- TV will wake Fire TV/Android TV when turned on

---

## 🔍 Troubleshooting

### Issue: Videos don't auto-play
**Solution**: 
- Ensure **Autoplay** is enabled in Fully Kiosk settings
- Check browser console for errors
- Try clicking screen once to trigger playback

### Issue: App doesn't auto-start on boot
**Solution**:
- Check **Autostart on Boot** is enabled
- Increase **Start Delay** to 15-20 seconds
- Grant all requested permissions
- Some devices require enabling in system settings:
  - Settings → Apps → Fully Kiosk → **Display over other apps** → Allow

### Issue: Screen sleeps after 30 minutes
**Solution**:
- Enable **Prevent Display From Sleep** in Fully Kiosk
- Disable screensaver in device settings
- Set **Screen Timeout** to "Never" in system settings

### Issue: Network connection errors
**Solution**:
- Increase **Start Delay** to 15-20 seconds
- Check WiFi/Ethernet is connected
- Verify server URL is correct and accessible

### Issue: Login required every restart
**Solution**:
- Check **Cookies** are enabled
- Don't clear cache on start
- Session should persist 30 days automatically

---

## 📊 Recommended TV Settings

For best digital signage experience:

1. **Picture Mode**: Standard or Vivid
2. **Brightness**: 80-100% (for visibility)
3. **Sleep Timer**: Disabled
4. **Auto Power Off**: Disabled  
5. **HDMI-CEC**: Enabled (optional)
6. **Energy Saving Mode**: Disabled

---

## 💡 Pro Tips

1. **Test before mounting**: Configure everything before wall-mounting TV
2. **Use Ethernet**: More stable than WiFi for 24/7 operation
3. **Remote Admin**: Enable for easy troubleshooting
4. **Backup config**: Export Fully Kiosk settings after configuration
5. **Label devices**: Name each TV in staff dashboard for easy management

---

## 🆓 Fully Kiosk Free vs Plus

**Free Version** (Recommended for starting):
- ✅ Kiosk mode
- ✅ Auto-start
- ✅ Hide navigation/status
- ✅ Remote admin
- ✅ Basic motion detection
- ⚠️ Shows small watermark

**Plus Version** (€14.90/device):
- ✅ Everything in Free
- ✅ No watermark
- ✅ Advanced motion detection
- ✅ REST API
- ✅ NFC/Bluetooth support

**Recommendation**: Start with free version. Upgrade if you need to hide watermark or use advanced features.

---

## 📞 Support

**For Fully Kiosk Browser issues**:
- Documentation: https://www.fully-kiosk.com
- Forum: https://www.fully-kiosk.com/forum
- Email: support@fully-kiosk.com

**For Aura Link issues**:
- Contact your staff administrator
- Check staff dashboard for device status

---

## 🎉 You're Ready!

Your Android TV/Firestick is now a professional digital signage display! Videos will auto-play every time you power on the device.

**Staff can now**:
- Assign videos remotely
- Update content instantly
- Monitor online/offline status
- Control rotation and loop settings

No more manual intervention needed! 🚀
