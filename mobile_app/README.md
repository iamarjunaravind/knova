# KNOVA Gate Check-In Mobile App 📱⚡

Dedicated, ultra-responsive mobile QR scanner application built for gate staff and volunteers at the **KNOVA Higher Education Expo**.

---

## 🌟 Features
- **Pure QR Check-in**: No cluttered desktop navigation or admin menus. Full screen camera scanning built strictly for smartphones.
- **Hardware Acceleration**: Powered by `html5-qrcode` with native `BarcodeDetector` support (sub-200ms decoding).
- **Audio Chime Synthesizer**: Built using native Web Audio API oscillators (D5 -> A5 ascending chord) — zero audio downloads needed, 0ms latency.
- **Haptic Vibration**: Physical tactile feedback on scan (`navigator.vibrate`).
- **Torch / Flashlight**: One-tap toggle for dimly lit exhibition halls.
- **Camera Flip**: Switch seamlessly between rear and front cameras.
- **Instant Result Bottom Sheet**:
  - 🟢 **Success**: Green banner, attendee name, role badge (Student/Parent/Exhibitor), Badge ID, check-in timestamp.
  - 🟡 **Already Checked In**: Amber warning with previous check-in time to prevent duplicate entry or pass sharing.
  - 🔴 **Unregistered**: Crimson alert for invalid or unregistered passes.
- **Fast Continuous Queue Scanning**: Auto-resumes in 1.8 seconds with progress countdown or tap to scan next immediately.
- **Manual Badge ID Entry**: Numeric/alphanumeric keypad modal for damaged or glare-covered phone screens.
- **Recent Scans History Drawer**: Slide-up drawer showing today's verified check-ins.
- **Live Counter**: Displays real-time today's check-ins vs total registered.

---

## 🚀 How to Use

### Method 1: Instant Mobile PWA (Recommended for iPhones & Androids)
Zero downloads or compilation required:
1. On any smartphone (gate staff's iPhone or Android), open Chrome or Safari.
2. Navigate to:
   ```
   https://knovaexpo.com/scanner/
   ```
3. Tap the browser menu:
   - **iOS (Safari)**: Tap Share (square with arrow) ➡️ **"Add to Home Screen"**.
   - **Android (Chrome)**: Tap 3 dots or the prompt ➡️ **"Install app"** / **"Add to Home screen"**.
4. A dedicated **"KNOVA Scan"** app icon appears on the mobile home screen. Tapping it opens in standalone full-screen mode with zero browser chrome!

---

### Method 2: Compile Native Android APK / App (Capacitor)
If you wish to compile an offline `.apk` package to distribute via USB or MDM:

1. **Install dependencies**:
   ```bash
   cd mobile_app
   npm install
   ```

2. **Initialize & Sync Android project**:
   ```bash
   npx cap add android
   npx cap sync android
   ```

3. **Open in Android Studio & Build APK**:
   ```bash
   npx cap open android
   ```
   In Android Studio, select **Build ➡️ Build Bundle(s) / APK(s) ➡️ Build APK(s)**.
