# Temple Discovery - Wireframes

## Map View Screen

```
┌─────────────────────────────────────┐
│  ← Temple Discovery    🔍  [List] ≡ │
│      கோவில் கண்டுபிடிப்பு             │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │                               📍│ │
│  │        🌟        ⭐              │ │
│  │     (Kapali)  (Vadapalani)      │ │
│  │                                 │ │
│  │  🏛️                   🌟        │ │
│  │(Parthasarathy)   (Ashtalakshmi) │ │
│  │                                 │ │
│  │         Current Location        │ │
│  │             📍🔵               │ │
│  │                                 │ │
│  │    🌟              🏛️          │ │
│  │  (Marundeeswarar) (San Thome)   │ │
│  │                                 │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 🌟 Kapaleeshwarar Temple        │ │
│  │    📍 0.8km • 🟢 Quiet          │ │
│  │    Lord Shiva • Mylapore        │ │
│  │                                 │ │
│  │  [Navigate] [Details] [Close]   │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 🎯 Filter & Sort  • வடிகட்டு    │ │
│  └─────────────────────────────────┘ │
│                                     │
└─────────────────────────────────────┘
┌─────────┬─────────┬─────────┬─────────┐
│ 🏠 Home │🕉️Temples│🚶 Tours │📅Calendar│
└─────────┴─────────┴─────────┴─────────┘
```

**Key Elements:**
- Interactive map with temple markers
- Different icons for navigation-ready vs info-only
- Current location indicator
- Selected temple info card
- Quick filter access
- Toggle between map/list views

---

## List View Screen

```
┌─────────────────────────────────────┐
│  ← Temple Discovery    🔍   [Map] ≡ │
│      கோவில் கண்டுபிடிப்பு             │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 🎯 Filter: All • Distance: 5km │ │
│  │    Sort by: Distance            │ │
│  └─────────────────────────────────┘ │
│                                     │
│  588 temples • 127 with navigation  │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 🌟 [IMG] Kapaleeshwarar         │ │
│  │           📍 0.8km • Mylapore   │ │
│  │           🟢 Quiet • ⏰ Open    │ │
│  │           🕉️ Lord Shiva         │ │
│  │    Famous Dravidian temple...   │ │
│  │  [Navigate] [Details] [⭐Save]  │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ ⭐ [IMG] Vadapalani Murugan     │ │
│  │           📍 2.1km • Vadapalani │ │
│  │           🟡 Moderate • ⏰ Open │ │
│  │           🔱 Lord Murugan       │ │
│  │    Popular healing temple...    │ │
│  │  [Navigate] [Details] [⭐Save]  │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 🏛️ [IMG] Parthasarathy         │ │
│  │           📍 3.2km • Triplicane │ │
│  │           ℹ️ Info Only • ⏰ Open│ │
│  │           🕉️ Lord Vishnu        │ │
│  │    Ancient Krishna temple...    │ │
│  │  [View Info] [Photos] [⭐Save]  │ │
│  └─────────────────────────────────┘ │
│                                     │
│           Load More (585) →         │
│                                     │
└─────────────────────────────────────┘
```

**Key Elements:**
- Active filter indicators
- Temple count summary
- List cards with key information
- Different action buttons based on temple type
- Progressive loading indicator
- Sort and filter options readily visible

---

## Filter Panel (Slide-up Modal)

```
┌─────────────────────────────────────┐
│                  ━                  │
│                                     │
│  🎯 Filter Temples • வடிகட்டு        │
│                                 [×] │
│                                     │
│  Distance • தூரம்                   │
│  ○ 1km   ● 5km   ○ 10km   ○ 25km   │
│  ○ 50km  ○ All Tamil Nadu          │
│                                     │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                     │
│  Temple Type • கோவில் வகை            │
│  ☑️ With Navigation (127)           │
│  ☑️ Information Only (461)          │
│                                     │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                     │
│  Deity • தெய்வம்                    │
│  ☑️ Lord Shiva (245)               │
│  ☑️ Lord Vishnu (178)              │
│  ☑️ Lord Murugan (89)              │
│  ☑️ Goddess Amman (76)             │
│      Show More... (▼)              │
│                                     │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                     │
│  District • மாவட்டம்                │
│  ☑️ Chennai (47)                   │
│  ☑️ Thanjavur (38)                 │
│  ☑️ Madurai (29)                   │
│  ☑️ Kanchipuram (25)               │
│      Show More... (▼)              │
│                                     │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                     │
│  Special Features • சிறப்பு அம்சங்கள் │
│  ☐ Real-time Crowd Data (5)        │
│  ☐ Festival Today                   │
│  ☐ Recently Added                   │
│  ☐ User Favorites                   │
│                                     │
│  ┌─────────────┐ ┌─────────────────┐ │
│  │ Clear All   │ │ Apply Filters   │ │
│  │ அனைத்தும்    │ │ வடிகட்டு        │ │
│  └─────────────┘ └─────────────────┘ │
│                                     │
└─────────────────────────────────────┘
```

**Key Elements:**
- Grouped filter categories
- Live count indicators
- Expandable sections for long lists
- Clear all and apply actions
- Bilingual labels throughout
- Easy-to-access checkboxes

---

## Search Interface (Expanded)

```
┌─────────────────────────────────────┐
│  ← Search Temples                ×  │
│      கோவில் தேடல்                   │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 🔍 Search temples, location...  │ │
│  │     கோவில், இடம் தேடவும்...        │ │
│  └─────────────────────────────────┘ │
│                                     │
│  Recent Searches • சமீபத்திய தேடல்கள் │
│                                     │
│  • Murugan temples                 │
│  • Temples in Madurai              │
│  • Navagraha circuit               │
│                                     │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                     │
│  Popular Searches • பிரபலமான தேடல்கள்│
│                                     │
│  • Shiva temples                   │
│  • Temples near me                 │
│  • Festival temples                │
│  • Pilgrimage circuits             │
│                                     │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                     │
│  Browse by District • மாவட்டம் அடிப்படை│
│                                     │
│  Chennai (47) • Thanjavur (38)     │
│  Madurai (29) • Kanchipuram (25)   │
│  Tirunelveli (22) • Salem (18)     │
│                                     │
│           View All Districts →     │
│                                     │
└─────────────────────────────────────┘
```

---

## Search Results (Real-time)

```
┌─────────────────────────────────────┐
│  ← Search Results               [×] │
│      தேடல் முடிவுகள்               │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 🔍 "murugan"           [Filter] │ │
│  └─────────────────────────────────┘ │
│                                     │
│  89 results found • 23 with GPS    │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 🌟 Vadapalani Murugan Temple    │ │
│  │    📍 2.1km • 🟡 Moderate      │ │
│  │    Popular Lord Murugan...      │ │
│  │         [Navigate] [Details]    │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 🌟 Palani Murugan Temple       │ │
│  │    📍 462km • ⭐ Famous         │ │
│  │    Hill temple, one of six...   │ │
│  │         [Navigate] [Details]    │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 🏛️ Thiruthani Murugan          │ │
│  │    📍 85km • ℹ️ Info Only       │ │
│  │    Ancient hill temple...       │ │
│  │         [View Info] [Details]   │ │
│  └─────────────────────────────────┘ │
│                                     │
│           Load More (86) →          │
│                                     │
└─────────────────────────────────────┘
```

---

## Sort Options Modal

```
┌─────────────────────────────────────┐
│                                     │
│  📊 Sort Results • வரிசைப்படுத்து     │
│                                 [×] │
│                                     │
│  ● Distance (Nearest First)        │
│    தூரம் (அருகில் உள்ளவை முதலில்)     │
│                                     │
│  ○ Distance (Farthest First)       │
│    தூரம் (தொலைவில் உள்ளவை முதலில்)    │
│                                     │
│  ○ Name (A-Z)                      │
│    பெயர் (அ-ஃ)                     │
│                                     │
│  ○ Name (Z-A)                      │
│    பெயர் (ஃ-அ)                     │
│                                     │
│  ○ Recently Added                   │
│    சமீபத்தில் சேர்க்கப்பட்டவை         │
│                                     │
│  ○ Most Popular                     │
│    மிகவும் பிரபலமானது                │
│                                     │
│  ○ With Navigation First            │
│    வழிகாட்டுதல் உடையவை முதலில்        │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │             Apply               │ │
│  │         பயன்படுத்து              │ │
│  └─────────────────────────────────┘ │
│                                     │
└─────────────────────────────────────┘
```

## Performance & UX Considerations

### Map View Optimizations
- Clustered markers for dense areas
- Level-of-detail based on zoom
- Lazy loading of temple details
- Smooth pan and zoom animations

### List View Optimizations  
- Virtual scrolling for large lists
- Image lazy loading with placeholders
- Infinite scroll with proper loading states
- Search debouncing (300ms delay)

### Accessibility Features
- Screen reader compatible search
- High contrast mode for maps
- Voice search capability
- Keyboard navigation support

### Offline Capabilities
- Cached search results
- Offline maps for major areas
- Saved filter preferences
- Graceful degradation for real-time features