# Onboarding Screens - Wireframes

## Screen 1: Language Selection (First Launch)

```
┌─────────────────────────────────────┐
│                                     │
│              🕉️ கோவில்               │
│         TEMPLE CALENDAR             │
│                                     │
│         Welcome / வரவேற்கிறோம்       │
│                                     │
│    Choose your preferred language   │
│      உங்கள் மொழியைத் தேர்ந்தெடுங்கள்    │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │         தமிழ் (Tamil)            │ │
│  │            [Selected]            │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │           English               │ │
│  │                                 │ │
│  └─────────────────────────────────┘ │
│                                     │
│                                     │
│           [Continue / தொடர்]          │
│                                     │
│                                     │
└─────────────────────────────────────┘
```

**Key Elements:**
- Traditional spiritual symbol (Om)
- Bilingual text for accessibility  
- Large, touchable language options
- Clear visual selection state
- Prominent continue button

---

## Screen 2: Location Permission Request

```
┌─────────────────────────────────────┐
│  ←                          தமிழ்/EN │
│                                     │
│              📍                     │
│         இடம் கண்டறிதல்                │
│      LOCATION DISCOVERY             │
│                                     │
│     உங்களுக்கு அருகில் உள்ள கோவில்களை │
│           கண்டறிய அனுமதி தேவை         │
│                                     │
│    We need location access to find  │
│       temples near you              │
│                                     │
│  • Find nearby temples             │
│  • Get accurate directions         │
│  • Show distance information       │
│  • Suggest relevant tour circuits  │
│                                     │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │      Allow Location Access      │ │
│  │       இடத்தை அனுமதிக்கவும்      │ │
│  └─────────────────────────────────┘ │
│                                     │
│         Skip for Now / இப்போது        │
│                                     │
└─────────────────────────────────────┘
```

**Key Elements:**
- Clear explanation of location benefits
- Bilingual permission request
- Primary action button emphasized
- Skip option for privacy-conscious users
- Permission benefits clearly listed

---

## Screen 3: Welcome & Features Overview

```
┌─────────────────────────────────────┐
│  ←                          தமிழ்/EN │
│                                     │
│           வரவேற்கிறோம் 🙏            │
│             WELCOME                 │
│                                     │
│      Discover Tamil Nadu's          │
│       Sacred Heritage              │
│                                     │
│  📍  588 Temples                   │
│      கோவில்கள்                      │
│                                     │
│  🧭  127 with GPS Navigation       │
│      வழிகாட்டுதல்                   │
│                                     │
│  🚶  4 Pilgrimage Circuits        │
│      யாத்திரை பாதைகள்               │
│                                     │
│  📅  Tamil Festival Calendar       │
│      திருவிழா நாட்காட்டி             │
│                                     │
│  📊  Real-time Crowd Updates       │
│      நேரலை கூட்டம்                 │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │    Start Exploring / தொடங்கு     │ │
│  └─────────────────────────────────┘ │
│                                     │
└─────────────────────────────────────┘
```

**Key Elements:**
- Welcoming spiritual greeting
- Key app features highlighted with icons
- Statistics showing database richness
- Bilingual feature descriptions
- Clear call-to-action to proceed

---

## Permission States & Error Handling

### Location Permission Denied State
```
┌─────────────────────────────────────┐
│              ⚠️                     │
│         Location Required           │
│         இடம் தேவையானது              │
│                                     │
│    To find nearby temples, please   │
│     enable location access in       │
│          device settings            │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │       Open Settings             │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │    Browse All Temples           │ │
│  │     அனைத்து கோவில்கள்           │ │
│  └─────────────────────────────────┘ │
│                                     │
└─────────────────────────────────────┘
```

### Network Connection Issues
```
┌─────────────────────────────────────┐
│              📱                     │
│         Offline Mode                │
│        ஆஃப்லைன் பயன்முறை            │
│                                     │
│    Limited features available       │
│      without internet              │
│                                     │
│  ✓ Cached temple data              │
│  ✓ Saved tours                     │
│  ✓ Basic navigation                │
│                                     │
│  ✗ Real-time updates               │
│  ✗ Latest festival info            │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │        Continue Offline         │ │
│  │       ஆஃப்லைனில் தொடர்           │ │
│  └─────────────────────────────────┘ │
│                                     │
│            Retry / மீண்டும்          │
│                                     │
└─────────────────────────────────────┘
```

## Design Considerations

### Accessibility Features
- High contrast text combinations
- Minimum 44pt touch targets
- Clear visual hierarchy
- Screen reader compatible structure
- Simple navigation patterns

### Cultural Sensitivity
- Traditional Om symbol respectfully used
- Tamil text grammatically correct
- Spiritual tone in messaging
- Appropriate color schemes (saffron, gold accents)

### Technical Notes
- Language preference stored locally
- Location permission cached
- Graceful degradation for denied permissions
- Offline-first data architecture
- Quick app startup without dependencies