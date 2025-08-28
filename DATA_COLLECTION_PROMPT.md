# Tamil Nadu Major Temples - Data Collection Prompt

## Project Overview
Creating a comprehensive mobile application featuring all major temples in Tamil Nadu with bilingual support (Tamil & English), location-based search, deity filtering, district categorization, and interactive map views.

## Core Data Requirements

### 1. Temple Basic Information (Bilingual)

#### English Fields:
- **Temple Name** (Official HRCE name)
- **Alternative Names** (Popular/Local names)
- **Temple ID** (Unique identifier)
- **Temple Type** (Shiva/Vishnu/Murugan/Amman/Other)
- **Historical Period** (Chola/Pallava/Pandya/Nayak/Modern)
- **Architecture Style** (Dravidian/Rock-cut/Modern)
- **UNESCO/ASI Status** (If applicable)

#### Tamil Fields (தமிழ் தகவல்கள்):
- **கோவில் பெயர்** (Temple name in Tamil)
- **மாற்று பெயர்கள்** (Alternative names)
- **கோவில் வகை** (சிவன்/விஷ்ணு/முருகன்/அம்மன்)
- **வரலாற்று காலம்** (Historical period)

### 2. Location & Geographic Data

#### Required Coordinates:
```json
{
  "coordinates": {
    "latitude": 10.7905, // Decimal degrees (6 decimal precision)
    "longitude": 78.7047,
    "google_maps_url": "https://maps.google.com/?q=...",
    "plus_code": "8CWM+XYZ", // Google Plus Code
    "what3words": "///word1.word2.word3"
  },
  "location": {
    "address_line1": "Temple Street Name",
    "address_line2": "Area/Locality",
    "village": "Village Name",
    "taluk": "Taluk Name",
    "district": "District Name",
    "state": "Tamil Nadu",
    "pincode": "600001",
    "nearest_railway_station": {
      "name": "Station Name",
      "distance_km": 5.2
    },
    "nearest_bus_stand": {
      "name": "Bus Stand Name",
      "distance_km": 1.5
    },
    "nearest_airport": {
      "name": "Airport Name",
      "distance_km": 45.0
    }
  }
}
```

### 3. Deity Information (முக்கிய தெய்வங்கள்)

#### Primary Deity:
- **Name** (English & Tamil)
- **Gender** (Male/Female/Formless)
- **Form** (Lingam/Idol/Abstract)
- **Facing Direction** (East/West/North/South)
- **Special Powers** (Healing/Prosperity/Education/Marriage)
- **Mythology/Legend** (Brief story)

#### Secondary Deities:
- **Consort Details** (if applicable)
- **Parivara Deities** (Associated deities)
- **Navagraha Presence** (Yes/No)
- **Specific Shrine Details**

### 4. Festivals & Events (திருவிழாக்கள்)

#### Major Festivals:
```json
{
  "festivals": [
    {
      "name_english": "Brahmotsavam",
      "name_tamil": "பிரம்மோற்சவம்",
      "tamil_month": "Chithirai",
      "english_month": "April-May",
      "duration_days": 10,
      "key_events": ["Flag Hoisting", "Car Festival", "Float Festival"],
      "special_poojas": ["Morning Abhishekam", "Evening Deeparadhana"],
      "crowd_level": "Very High",
      "booking_required": true
    }
  ],
  "monthly_festivals": {
    "pradosham": "Twice monthly",
    "shivaratri": "Monthly",
    "ekadasi": "Twice monthly",
    "pournami": "Full moon day"
  },
  "daily_poojas": [
    {
      "name": "Kalasandhi",
      "time": "06:00 AM",
      "duration_minutes": 30
    }
  ]
}
```

### 5. Temple Timings & Services

```json
{
  "regular_timings": {
    "morning": {
      "open": "05:00 AM",
      "close": "12:30 PM"
    },
    "evening": {
      "open": "04:00 PM",
      "close": "09:00 PM"
    }
  },
  "special_darshan": {
    "vip_darshan": {
      "available": true,
      "price": 300,
      "booking_url": "https://..."
    },
    "online_booking": {
      "available": true,
      "portal": "HRCE Portal"
    }
  },
  "services": [
    {
      "name": "Archanai",
      "price_range": "50-500",
      "advance_booking": false
    },
    {
      "name": "Abhishekam",
      "price_range": "500-5000",
      "advance_booking": true
    }
  ]
}
```

### 6. Historical & Cultural Significance

- **Age/Period of Construction**
- **Built by** (King/Dynasty/Devotee)
- **Inscriptions** (Number and language)
- **Literary References** (Thevaram/Divya Prabandham/Others)
- **Sung by** (Nayanmars/Alwars if applicable)
- **Sthala Purana** (Temple mythology)
- **Architectural Highlights** (Gopuram height, sculptures, paintings)

### 7. Visitor Information

```json
{
  "facilities": {
    "parking": {
      "two_wheeler": true,
      "four_wheeler": true,
      "bus_parking": true
    },
    "amenities": [
      "Free meals (Annadanam)",
      "Drinking water",
      "Restrooms",
      "Wheelchair accessibility",
      "Footwear stand",
      "Prasadam counter"
    ],
    "accommodation": {
      "temple_guest_house": true,
      "rooms_available": 20,
      "booking_contact": "+91-XXXXXXXXXX"
    }
  },
  "dress_code": {
    "men": "Dhoti or formal wear",
    "women": "Saree or churidar",
    "restrictions": "No shorts, sleeveless"
  },
  "photography": {
    "allowed": "Only outside",
    "camera_fee": 50,
    "video_fee": 200
  }
}
```

### 8. Contact Information

```json
{
  "contact": {
    "office_phone": ["+91-44-XXXXXXXX"],
    "mobile": ["+91-9XXXXXXXXX"],
    "email": "temple@hrce.tn.gov.in",
    "website": "https://temple.tn.gov.in",
    "social_media": {
      "facebook": "@templename",
      "instagram": "@templename",
      "youtube": "ChannelName"
    },
    "administration": {
      "executive_officer": "Name",
      "office_hours": "10:00 AM - 5:00 PM"
    }
  }
}
```

### 9. Media & Resources

```json
{
  "media": {
    "images": [
      {
        "url": "https://...",
        "type": "main_gopuram",
        "caption": "Eastern Gopuram",
        "photographer": "Credit",
        "resolution": "high"
      }
    ],
    "virtual_tour": "https://360tour.link",
    "youtube_videos": [
      {
        "title": "Temple Documentary",
        "url": "https://youtube.com/...",
        "duration": "15:30"
      }
    ],
    "audio_guides": {
      "tamil": "https://audio_tamil.mp3",
      "english": "https://audio_english.mp3"
    }
  }
}
```

### 10. Temple Groupings & Circuits

```json
{
  "temple_circuits": {
    "navagraha_temples": {
      "name": "Navagraha Temples",
      "name_tamil": "நவகிரக தலங்கள்",
      "total_temples": 9,
      "temples": [
        {
          "planet": "Sun (Surya)",
          "temple": "Suryanar Temple",
          "location": "Kumbakonam",
          "order": 1
        }
      ],
      "circuit_map": "https://map_url",
      "suggested_duration": "2 days",
      "total_distance": "150 km"
    },
    "pancha_bootha_sthalams": {
      "name": "Five Elements Temples",
      "total_temples": 5
    },
    "arupadai_veedu": {
      "name": "Six Abodes of Murugan",
      "total_temples": 6
    },
    "divya_desams": {
      "name": "108 Divya Desams",
      "in_tamil_nadu": 84
    }
  }
}
```

### 11. Specialized Information

#### For Researchers:
- **HRCE Registration Number**
- **Annual Income Category**
- **Land/Property Details**
- **Trust/Management Type**
- **Historical Inscriptions Database ID**
- **ASI Monument Number** (if applicable)

#### For Pilgrims:
- **Parihara Sthalams** (Remedial temples)
- **Rasi/Nakshatra Specific Benefits**
- **Special Vratas/Penances**
- **Miracle/Healing Stories**

#### For Tourists:
- **Best Time to Visit**
- **Nearby Tourist Attractions**
- **Local Festivals Calendar**
- **Shopping/Local Crafts**
- **Traditional Food Specialties**

## Data Collection Sources

### Primary Sources:
1. **HR&CE Department** (Official data)
   - Website: https://www.tn.gov.in/hrce
   - Temple portals

2. **Google Maps API**
   - Places API for coordinates
   - Photos API for images
   - Reviews and ratings

3. **Archaeological Survey of India**
   - Protected monuments list
   - Historical documentation

### Secondary Sources:
1. **Wikipedia** (Tamil & English)
2. **Temple Websites** (Individual)
3. **Travel Websites** (TripAdvisor, etc.)
4. **Books & Publications**
5. **Local Temple Authorities**

## Data Quality Requirements

### Mandatory Fields (Must Have):
- Temple Name (Tamil & English)
- Exact GPS Coordinates
- District
- Main Deity
- One Major Festival
- Basic Timings
- Contact Number

### Priority Fields (Should Have):
- Complete Address
- All Festivals
- Historical Information
- Photos (min 3)
- Nearby Landmarks

### Optional Fields (Nice to Have):
- Virtual Tours
- Audio Guides
- Detailed Mythology
- Architectural Details

## Data Validation Checklist

- [ ] GPS coordinates verified with Google Maps
- [ ] Tamil text properly encoded (UTF-8)
- [ ] Phone numbers in correct format
- [ ] Timings in 12/24 hour format
- [ ] Festival dates verified with Tamil calendar
- [ ] Images properly licensed/credited
- [ ] URLs are active and correct
- [ ] District names match official list

## Sample Data Entry

```json
{
  "temple_id": "TN_CHE_001",
  "name": {
    "english": "Kapaleeswarar Temple",
    "tamil": "கபாலீசுவரர் கோவில்"
  },
  "location": {
    "coordinates": {
      "latitude": 13.0339,
      "longitude": 80.2695
    },
    "district": "Chennai",
    "address": "Mylapore, Chennai - 600004"
  },
  "deity": {
    "main": {
      "english": "Lord Shiva",
      "tamil": "சிவபெருமான்"
    }
  },
  "festivals": [
    {
      "name": "Panguni Peruvizha",
      "month": "March-April",
      "duration_days": 10
    }
  ],
  "timings": {
    "morning": "5:00 AM - 12:00 PM",
    "evening": "4:00 PM - 9:00 PM"
  },
  "contact": "+91-44-24643670",
  "temple_group": ["Paadal Petra Sthalams"],
  "data_verified": "2025-01-15",
  "data_source": "HRCE + Field Visit"
}
```

## API Response Format

```json
{
  "status": "success",
  "data": {
    "temples": [...],
    "total_count": 2500,
    "filters_applied": {
      "district": "Chennai",
      "deity": "Shiva",
      "radius_km": 10
    }
  },
  "meta": {
    "version": "1.0",
    "last_updated": "2025-01-15",
    "languages": ["en", "ta"]
  }
}
```

## Notes for Data Collectors

1. **Accuracy First**: Better to have fewer temples with complete, accurate data
2. **Bilingual Priority**: Always collect both Tamil and English names
3. **Coordinates Precision**: Use at least 6 decimal places for GPS
4. **Image Rights**: Ensure proper permissions for all images
5. **Regular Updates**: Festival dates change yearly - plan for updates
6. **User Feedback**: Include mechanism to collect corrections from users
7. **Offline Support**: Structure data for offline mobile app usage

---

## Target Metrics

- **Phase 1**: 500 major temples (Income > 10 Lakhs)
- **Phase 2**: 2000 prominent temples (District headquarters)
- **Phase 3**: 5000+ temples (Complete coverage)
- **Languages**: 100% bilingual (Tamil & English)
- **Coordinates**: 100% GPS mapped
- **Images**: Minimum 3 per temple
- **Festivals**: Minimum 1 major festival per temple

---

*This prompt can be used with AI assistants, data entry teams, or web scraping tools to collect comprehensive temple data for the Tamil Nadu Temple App.*