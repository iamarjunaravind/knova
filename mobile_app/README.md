# KNOVA 4-in-1 Mobile QR Scanner & Check-In App 📱⚡

Dedicated, ultra-responsive mobile QR scanner application built for staff, university exhibitors, and seminar coordinators at the **KNOVA Higher Education Expo**.

---

## 🌟 4 Types of Users & Operations

The mobile scanner supports 4 distinct expo personas using the **same database accounts and credentials**:

| Persona / Tab | Function | Reward / Action | Role Boundary |
|---|---|---|---|
| **🚪 Gate Entry** | Verifies attendee badge & registers hall entry | Attendance logged (`Registration.is_checked_in = True`) | Admin / Gate Staff |
| **🏛️ Booth Visit** | University booth visit punch & student lead capture | **+20 XP** awarded to student badge | Auto-locked to exhibitor's university |
| **🎤 Seminars** | Keynote session attendance punch | **+25 XP** awarded to student badge | Auto-locked to assigned session |
| **🎓 Counselling** | 1-on-1 expert educational counselling punch | **+40 XP** awarded to student badge | Auto-locked to expert's desk |

---

## 🔐 Database Authentication & Automatic Role Locking

- **Uses existing database credentials**: Staff sign in using their standard Django account username, email, attendee badge ID (e.g. `KNOVA-EX-19997`), or phone number.
- **Role Detection & Station Auto-Locking**:
  - **University Exhibitors**: Automatically locked to their university booth (`mode='booth'`); tabs and station selectors are locked so exhibitors cannot punch on behalf of other booths.
  - **Seminar Coordinators**: Automatically locked to their auditorium/session (`mode='seminar'`).
  - **Academic Counsellors**: Automatically locked to their counselling desk (`mode='counselling'`).
  - **Gate Staff & Admins**: Granted full unrestricted access across all 4 modes with live station switching.
  - **Students / General Public**: Blocked from accessing the staff scanner.
- **Session Persistence**: Works seamlessly across browser refreshes and native app launches using session tokens (`X-Session-Key`).
- **One-Tap Sign Out**: Accessible anytime via the user avatar chip in the header.

---

## ⚡ Hardware & Scanning Capabilities
- **Pure QR Experience**: Fast, uncluttered viewfinder strictly engineered for smartphones.
- **Hardware Acceleration**: Powered by `html5-qrcode` with native `BarcodeDetector` support (sub-200ms decoding).
- **Zero-Latency Audio Synthesizer**: Web Audio API oscillator chimes for success, duplicate, and warning.
- **Haptic Vibration**: Physical tactile feedback on scan (`navigator.vibrate`).
- **Torch / Flashlight Toggle**: For dimly lit exhibition halls.
- **Camera Flip**: Switch seamlessly between rear and front cameras.
- **Auto-Queue Continuous Scanning**: Auto-dismisses sheet in 1.8 seconds with progress countdown or tap to scan next immediately.
- **Manual Badge ID Entry**: Numeric/alphanumeric keypad modal for damaged or glare-covered phone screens.
- **Recent Scans History Drawer**: Slide-up drawer showing today's verified check-ins.

---

## 🚀 How to Access & Install

### Method 1: Instant Mobile PWA (Recommended for iPhones & Androids)
Zero downloads or compilation required:
1. On any smartphone (gate staff's iPhone or Android), open Chrome or Safari.
2. Navigate to:
   ```
   https://knovaexpo.com/scanner/
   ```
3. Sign in with your staff, exhibitor, or counsellor account.
4. Tap the browser menu:
   - **iOS (Safari)**: Tap Share (square with arrow) ➡️ **"Add to Home Screen"**.
   - **Android (Chrome)**: Tap 3 dots or the prompt ➡️ **"Install app"** / **"Add to Home screen"**.
5. A dedicated **"KNOVA Scan"** app icon appears on the mobile home screen. Tapping it opens in standalone full-screen mode with zero browser chrome!

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
