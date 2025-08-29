# User Flows - Tamil Nadu Temple Calendar App

## Primary User Journeys

### 1. First-Time User Onboarding Flow
```
Launch App
    ↓
Language Selection (Tamil/English)
    ↓
Location Permission Request
    ↓ (Allow)
Welcome Screen (App Features Overview)
    ↓
Home Dashboard
```

### 2. Temple Discovery Flow
```
Home Dashboard
    ↓
"Find Temples" → Temple Discovery Screen
    ↓
Choose View: [Map View] OR [List View]
    ↓
Apply Filters (Optional)
    ↓
Select Temple from Results
    ↓
Temple Details Screen
    ↓
Actions: [Get Directions] OR [Add to Tour] OR [View Calendar]
```

### 3. Navigation-Ready Temple Journey
```
Temple Details Screen
    ↓ (GPS Available)
"Get Directions" Button
    ↓
GPS Navigation Launch
    ↓ (External Maps App)
Navigate to Temple
    ↓ (Return to App)
Check-in/Review Options
```

### 4. Tour Circuit Planning Flow  
```
Home Dashboard
    ↓
"Tour Circuits" → Circuit Selection Screen
    ↓
Choose Circuit: [Navagraha] [Murugan] [Pancha Bhoota] [Traditional]
    ↓
Circuit Details & Map
    ↓
"Start Tour" → Route Planning
    ↓
Navigate to First Temple
    ↓
Progress Tracking Through Circuit
```

### 5. Festival Calendar Discovery Flow
```
Home Dashboard
    ↓
"Festival Calendar" → Calendar View (Tamil)
    ↓
Select Date/Month
    ↓
View Festivals for Selected Period
    ↓
Select Specific Festival
    ↓
Festival Details + Related Temples
    ↓
"Find Temples" → Temple List for Festival
```

### 6. Search & Filter Flow
```
Any Screen with Search
    ↓
Search Bar (Type temple name/location)
    ↓
Real-time Results Display
    ↓
Apply Advanced Filters:
    • District
    • Deity Type  
    • Distance Range
    • Navigation Available
    • Crowd Level
    ↓
Filtered Results
    ↓
Select Temple → Temple Details
```

## Navigation Patterns

### Bottom Tab Navigation (Primary)
```
┌─────────┬─────────┬─────────┬─────────┬─────────┐
│ Home    │ Temples │ Tours   │ Calendar│ Profile │
│ 🏠      │ 🕉️      │ 🚶‍♂️     │ 📅      │ 👤     │
└─────────┴─────────┴─────────┴─────────┴─────────┘
```

### Top Navigation (Secondary)
- **Back Button** (←) - Return to previous screen
- **Search Icon** (🔍) - Global temple search  
- **Language Toggle** (தமிழ்/EN) - Switch interface language
- **Menu/Settings** (≡) - App settings and preferences

## Critical Decision Points

### 1. Temple Selection Decision Tree
```
User Selects Temple
    ↓
Check Temple Status:
    
GPS Available? → [YES] → Show "Get Directions" prominently
    ↓               [NO] → Show "View Location Info" + contact details
    
Crowd Data Available? → [YES] → Display crowd indicator
    ↓                    [NO] → Show standard temple info
    
Special Features? → [YES] → Highlight unique aspects
    ↓                [NO] → Show standard template
```

### 2. Offline vs Online Experience
```
App Launch
    ↓
Check Internet Connection:
    
Online → Full Features Available
    ↓
    • Real-time crowd data
    • Festival updates
    • GPS navigation launch
    • Search all 588 temples
    
Offline → Limited Features
    ↓
    • Cached temple data (127 with GPS)
    • Saved tour circuits
    • Basic temple information
    • Local festival calendar
```

## Screen Transition Patterns

### Slide Transitions
- **Forward Navigation**: Right to Left slide
- **Back Navigation**: Left to Right slide
- **Tab Switches**: Fade transition

### Modal Presentations
- **Filter Panels**: Slide up from bottom
- **Temple Image Gallery**: Fade with zoom
- **Settings Menu**: Slide down from top

### Loading States
- **Temple Search**: Skeleton cards with shimmer
- **Map Loading**: Progressive tile loading
- **Navigation Launch**: Brief loading spinner

## Error & Edge Case Flows

### No Location Permission
```
Location Required Screen
    ↓
"Allow Location Access" Button
    ↓ (Declined)
Manual Location Entry
    ↓
District/City Selection
    ↓
Proceed with Selected Location
```

### No Internet Connection  
```
Offline Mode Banner
    ↓
"Limited Features Available"
    ↓
Show Cached Data Only
    ↓
"Retry Connection" Option
```

### No Nearby Temples
```
Empty State Screen
    ↓
"No temples found nearby"
    ↓
Suggestions:
• Expand search radius
• Browse by district
• Explore tour circuits
```

## Accessibility Considerations

### Voice Navigation Flow
```
Voice Command Trigger
    ↓
Speech Recognition
    ↓
Parse Intent:
• "Find Murugan temples"  
• "Navigate to nearest temple"
• "Show festival calendar"
    ↓
Execute Action + Audio Feedback
```

### High Contrast Mode
- All flows maintain navigation clarity
- Button states clearly indicated
- Text remains readable at 200% zoom
- Color is never the sole information indicator