# Tamil Nadu Temple Calendar App - User Testing Guide

## 🚀 Quick Start

### Access the Prototype:
```bash
# Open terminal in demo-ui folder
python3 -m http.server 8000

# Visit in browser (works on mobile too)
http://localhost:8000
```

Or share via ngrok for remote testing:
```bash
ngrok http 8000
# Share the generated URL with testers
```

## ✅ Testing Checklist

### Core Features to Test:

#### 1. **First Impressions** (2 min)
- [ ] Does the app load quickly?
- [ ] Is the purpose clear immediately?
- [ ] Can you switch to Tamil language?
- [ ] Are the colors and fonts readable?

#### 2. **Find Nearest Temple** (5 min)
- [ ] Allow location access when prompted
- [ ] Check if nearest temples show correctly
- [ ] Verify distance calculations
- [ ] Test "Navigate" button (opens Google Maps)
- [ ] Test "Call" button with real phone numbers

#### 3. **Search Functionality** (5 min)
- [ ] Search for "Meenakshi" 
- [ ] Search for temples in your district
- [ ] Filter by deity type (Shiva, Vishnu, etc.)
- [ ] Check GPS vs non-GPS temple indicators

#### 4. **Temple Details** (5 min)
- [ ] View full temple information
- [ ] Check ratings and addresses
- [ ] Test navigation for GPS temples
- [ ] Notice "No GPS" indicator for others
- [ ] Check crowd levels (5 temples have this)

#### 5. **Tour Circuits** (5 min)
- [ ] Explore Navagraha circuit
- [ ] Check Murugan temples circuit
- [ ] View distance and time estimates
- [ ] Understand the temple sequence

#### 6. **Mobile Experience** (3 min)
- [ ] Test on your phone
- [ ] Check touch targets are large enough
- [ ] Verify responsive layout
- [ ] Test bottom navigation

## 📊 Data Available

### Real Temple Data:
- **588 Total Temples** - Complete directory
- **127 GPS Temples** - Full navigation support
- **5 Crowd Temples** - Real-time busy indicators
- **4 Tour Circuits** - Curated pilgrimage routes
- **30+ Districts** - Full Tamil Nadu coverage

### Unique Features:
- ✅ Real Google ratings (4.6-4.8)
- ✅ Actual phone numbers
- ✅ Precise GPS coordinates
- ✅ Tamil/English bilingual
- ✅ Elder-friendly design

## 📝 Feedback Questions

### Usability:
1. How easy was it to find a temple near you?
2. Could you easily switch between Tamil and English?
3. Were the buttons and text large enough?
4. Did you understand the GPS vs non-GPS difference?

### Features:
5. Which feature did you find most useful?
6. What's missing that you expected?
7. Would you use the tour circuits feature?
8. Is the search/filter helpful?

### Design:
9. Do the colors feel appropriate for a temple app?
10. Is the Tamil text clear and readable?
11. Any confusion with icons or buttons?

### Overall:
12. Would you download this app?
13. Would you recommend it to family/friends?
14. What's the ONE thing to improve?
15. Rating out of 10?

## 🎯 Target Users

### Primary:
- Tamil families planning temple visits
- Elderly devotees (50+ age)
- Weekend pilgrimage planners
- Festival attendees

### Secondary:
- Tourists visiting Tamil Nadu
- Young professionals reconnecting with culture
- Temple tour organizers

## 💡 Key Metrics to Observe

During testing, note:
- Time to find first temple: < 30 seconds
- Search success rate: > 90%
- Navigation clicks: < 3 to reach any temple
- Language switch usage: Check if needed
- Error encounters: Should be zero

## 📱 Technical Notes

### Supported Browsers:
- Chrome/Safari/Firefox (Latest)
- Mobile browsers (iOS/Android)
- Edge (Windows)

### Required:
- Internet connection (first load)
- Location permission (for nearby)
- Modern browser (2020+)

### Data Usage:
- Initial load: ~400KB
- Cached after first visit
- Offline capable for browsing

## 🔄 Feedback Collection

### Method 1: Live Session
1. Screen share or in-person
2. Observe user actions
3. Note confusion points
4. Ask questions after each task

### Method 2: Self-Testing
1. Share this guide + app link
2. User tests independently
3. Fills feedback form
4. Follow-up call if needed

### Method 3: Analytics
- Add Google Analytics
- Track: searches, filters, navigation clicks
- Measure: session time, bounce rate
- Monitor: error rates

## 🚩 Red Flags to Watch

- User can't find nearby temples
- Search doesn't work as expected
- Navigation buttons don't work
- Tamil text is unreadable
- Mobile layout is broken
- Takes > 5 seconds to load

## ✨ Success Indicators

- User finds temple in < 30 seconds
- Successfully navigates to temple
- Understands tour circuits
- Appreciates Tamil language option
- Says "I would use this"
- Asks "When can I download?"

---

## Next Steps After Testing

1. **Collect all feedback**
2. **Identify top 3 issues**
3. **Prioritize features**
4. **Decide on MVP scope**
5. **Go/No-Go decision**

**Testing Period:** Show to 5-10 users
**Decision Date:** Within 1 week
**Success Criteria:** 7/10 average rating + willing to download

---

*Ready for user testing! The app has real data and working features.*