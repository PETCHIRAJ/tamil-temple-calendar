// Tamil Temple Mobile App V2 - With Map and Calendar
class TamilTempleApp {
    constructor() {
        this.temples = [];
        this.templesWithCoords = [];
        this.featuredTemples = [];
        this.festivalCalendar = {};
        this.userLocation = null;
        this.currentPage = 'home';
        this.searchRadius = 10; // km
        this.map = null;
        this.markers = [];
        this.userMarker = null;
        
        // Tamil deity mappings
        this.deityTamil = {
            'Shiva': 'சிவன்',
            'Vishnu': 'விஷ்ணு',
            'Murugan': 'முருகன்',
            'Devi': 'அம்மன்',
            'Other': 'மற்றவை'
        };
        
        // Tamil month names
        this.tamilMonths = {
            'Thai': 'தை',
            'Masi': 'மாசி',
            'Panguni': 'பங்குனி',
            'Chithirai': 'சித்திரை',
            'Vaikasi': 'வைகாசி',
            'Aani': 'ஆனி',
            'Aadi': 'ஆடி',
            'Aavani': 'ஆவணி',
            'Purattasi': 'புரட்டாசி',
            'Aippasi': 'ஐப்பசி',
            'Karthigai': 'கார்த்திகை',
            'Margazhi': 'மார்கழி'
        };

        // Deity to festival mapping
        this.deityFestivals = {
            'Shiva': ['pradosham', 'shivaratri'],
            'Vishnu': ['ekadashi', 'vaikunta ekadashi'],
            'Murugan': ['sashti', 'thai pusam', 'skanda'],
            'Devi': ['pournami', 'navaratri', 'aadi']
        };
        
        this.init();
    }
    
    async init() {
        await this.loadData();
        this.setupEventListeners();
        this.checkTodaysFestivals();
        this.displayFeaturedTemples();
    }
    
    async loadData() {
        try {
            const response = await fetch('../data/temples_with_location.json');
            const data = await response.json();
            
            this.temples = data.all_temples || [];
            this.templesWithCoords = data.temples_with_coordinates || [];
            this.featuredTemples = data.featured_temples || [];
            this.festivalCalendar = data.festival_calendar || {};
            
            console.log(`Loaded ${this.temples.length} temples, ${this.templesWithCoords.length} with coordinates`);
        } catch (error) {
            console.error('Error loading data:', error);
        }
    }
    
    setupEventListeners() {
        // Search on home page
        const homeSearch = document.querySelector('#homePage .search-input');
        if (homeSearch) {
            homeSearch.addEventListener('input', (e) => {
                this.quickSearch(e.target.value);
            });
        }
        
        // Modal close on backdrop click
        document.getElementById('templeModal').addEventListener('click', (e) => {
            if (e.target.id === 'templeModal') {
                this.closeModal();
            }
        });
    }
    
    switchPage(pageName) {
        // Update nav
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        event.target.closest('.nav-item').classList.add('active');
        
        // Switch pages
        document.querySelectorAll('.page').forEach(page => {
            page.classList.remove('active');
        });
        document.getElementById(`${pageName}Page`).classList.add('active');
        
        this.currentPage = pageName;
        
        // Load page content
        switch(pageName) {
            case 'home':
                this.displayFeaturedTemples();
                break;
            case 'map':
                this.initMap();
                break;
            case 'festivals':
                this.displayCalendar();
                break;
        }
    }
    
    async requestLocation() {
        if (!navigator.geolocation) {
            alert('உங்கள் சாதனம் இருப்பிட சேவையை ஆதரிக்கவில்லை');
            return;
        }
        
        navigator.geolocation.getCurrentPosition(
            (position) => {
                this.userLocation = {
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude
                };
                
                // Hide location banner
                document.getElementById('locationBanner').style.display = 'none';
                
                // Update title and display nearby temples
                document.getElementById('templeListTitle').textContent = 'அருகில் உள்ள கோயில்கள்';
                this.displayNearbyTemples();
                
                // Update map if it's initialized
                if (this.map && this.userMarker) {
                    this.map.setView([this.userLocation.latitude, this.userLocation.longitude], 13);
                    this.userMarker.setLatLng([this.userLocation.latitude, this.userLocation.longitude]);
                }
            },
            (error) => {
                console.log('Location denied:', error);
                document.getElementById('locationBanner').style.display = 'none';
            }
        );
    }
    
    initMap() {
        if (this.map) {
            // Map already initialized, just refresh
            setTimeout(() => this.map.invalidateSize(), 100);
            return;
        }
        
        // Initialize map centered on Tamil Nadu
        const defaultLat = 11.1271; // Tamil Nadu center
        const defaultLng = 78.6569;
        
        this.map = L.map('mapContainer').setView([defaultLat, defaultLng], 7);
        
        // Add OpenStreetMap tiles
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 18
        }).addTo(this.map);
        
        // Add user location marker if available
        if (this.userLocation) {
            this.userMarker = L.marker([this.userLocation.latitude, this.userLocation.longitude], {
                icon: L.divIcon({
                    html: '📍',
                    iconSize: [30, 30],
                    className: 'user-marker'
                })
            }).addTo(this.map);
            
            this.map.setView([this.userLocation.latitude, this.userLocation.longitude], 13);
        }
        
        // Add temple markers
        this.addTempleMarkers();
    }
    
    addTempleMarkers() {
        // Clear existing markers
        this.markers.forEach(marker => this.map.removeLayer(marker));
        this.markers = [];
        
        // Track which temples are shown to avoid duplicates
        const shownTempleIds = new Set();
        
        // First, add markers for temples with exact coordinates
        this.templesWithCoords.forEach(temple => {
            const marker = L.marker([temple.latitude, temple.longitude], {
                icon: L.divIcon({
                    html: '🛕',
                    iconSize: [25, 25],
                    className: 'temple-marker'
                })
            });
            
            // Add popup with temple info
            const popupContent = `
                <div style="font-family: 'Noto Sans Tamil', sans-serif;">
                    <b>${temple.tamil_name || temple.name}</b><br>
                    ${temple.district}<br>
                    <button onclick="app.showTempleDetails('${temple.temple_id}')" 
                            style="margin-top: 8px; padding: 4px 8px; background: #667eea; color: white; border: none; border-radius: 4px;">
                        விவரங்கள்
                    </button>
                </div>
            `;
            
            marker.bindPopup(popupContent);
            marker.addTo(this.map);
            this.markers.push(marker);
            shownTempleIds.add(temple.temple_id);
        });
        
        // Group temples by pincode for those without coordinates
        const pincodeGroups = {};
        this.temples.forEach(temple => {
            // Skip if already shown with coordinates
            if (shownTempleIds.has(temple.temple_id)) return;
            
            if (temple.pincode && !temple.latitude) {
                if (!pincodeGroups[temple.pincode]) {
                    pincodeGroups[temple.pincode] = [];
                }
                pincodeGroups[temple.pincode].push(temple);
            }
        });
        
        // Add cluster markers for pincode groups
        // Use approximate coordinates based on district centers
        const districtCoords = {
            'Chennai': [13.0827, 80.2707],
            'Coimbatore': [11.0168, 76.9558],
            'Madurai': [9.9252, 78.1198],
            'Tiruchirappalli': [10.7905, 78.7047],
            'Salem': [11.6643, 78.1460],
            'Tirunelveli': [8.7139, 77.7567],
            'Erode': [11.3410, 77.7172],
            'Vellore': [12.9165, 79.1325],
            'Thoothukudi': [8.7642, 78.1348],
            'Thanjavur': [10.7867, 79.1378],
            'Dindigul': [10.3673, 77.9803],
            'Kanchipuram': [12.8342, 79.7036],
            'Tiruppur': [11.1085, 77.3411],
            'Tiruvallur': [13.1231, 79.9119],
            'Kanyakumari': [8.0883, 77.5385],
            'Nagapattinam': [10.7672, 79.8449],
            'Cuddalore': [11.7480, 79.7714],
            'Villupuram': [11.9401, 79.4930],
            'Dharmapuri': [12.1357, 78.1602],
            'Krishnagiri': [12.5186, 78.2137],
            'Tiruvannamalai': [12.2253, 79.0747],
            'Sivaganga': [9.8477, 78.4815],
            'Karur': [10.9601, 78.0766],
            'Namakkal': [11.2189, 78.1673],
            'Theni': [10.0104, 77.4777],
            'Nilgiris': [11.4916, 76.7337],
            'Ramanathapuram': [9.3639, 78.8395],
            'Virudhunagar': [9.5810, 77.9624],
            'Ariyalur': [11.1401, 79.0786],
            'Perambalur': [11.2342, 78.8807],
            'Pudukkottai': [10.3833, 78.8001],
            'Ranipet': [12.9344, 79.3328],
            'Tenkasi': [8.9604, 77.3152],
            'Tirupathur': [12.4967, 78.5730],
            'Kallakurichi': [11.7387, 78.9609],
            'Chengalpattu': [12.6819, 79.9888],
            'Mayiladuthurai': [11.1018, 79.6521]
        };
        
        // Show pincode clusters for major areas
        Object.entries(pincodeGroups).forEach(([pincode, temples]) => {
            // Skip if too many temples (likely error in data)
            if (temples.length > 50) return;
            
            // Try to get coordinates from district
            const district = temples[0].district;
            const coords = districtCoords[district] || districtCoords[district?.replace(' District', '')];
            
            if (coords) {
                // Add small random offset to prevent exact overlap
                const lat = coords[0] + (Math.random() - 0.5) * 0.1;
                const lng = coords[1] + (Math.random() - 0.5) * 0.1;
                
                const marker = L.marker([lat, lng], {
                    icon: L.divIcon({
                        html: `<div style="background: #667eea; color: white; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: bold;">${temples.length}</div>`,
                        iconSize: [30, 30],
                        className: 'cluster-marker'
                    })
                });
                
                // Create popup with temple list
                const templeList = temples.slice(0, 5).map(t => 
                    `<div style="padding: 4px 0; cursor: pointer;" onclick="app.showTempleDetails('${t.temple_id}')">
                        • ${t.tamil_name || t.name}
                    </div>`
                ).join('');
                
                const popupContent = `
                    <div style="font-family: 'Noto Sans Tamil', sans-serif; max-width: 200px;">
                        <b>📮 ${pincode}</b><br>
                        <b>${temples.length} கோயில்கள்</b><br>
                        <div style="margin-top: 8px; max-height: 150px; overflow-y: auto;">
                            ${templeList}
                            ${temples.length > 5 ? `<div style="padding: 4px 0; color: #666;">...மேலும் ${temples.length - 5}</div>` : ''}
                        </div>
                        <button onclick="app.showPincodeTemples('${pincode}')" 
                                style="margin-top: 8px; width: 100%; padding: 4px 8px; background: #667eea; color: white; border: none; border-radius: 4px;">
                            அனைத்தும் காண்க
                        </button>
                    </div>
                `;
                
                marker.bindPopup(popupContent);
                marker.addTo(this.map);
                this.markers.push(marker);
            }
        });
        
        // Update map info
        console.log(`Map showing: ${this.templesWithCoords.length} exact locations, ${Object.keys(pincodeGroups).length} pincode clusters`);
    }
    
    showPincodeTemples(pincode) {
        // Switch to home page and show temples from this pincode
        this.switchToHome();
        const results = this.temples.filter(t => t.pincode === pincode).slice(0, 50);
        document.getElementById('templeListTitle').textContent = `📮 ${pincode} - பகுதி கோயில்கள்`;
        
        const container = document.getElementById('templeList');
        if (results.length > 0) {
            container.innerHTML = results.map(temple => 
                this.createTempleCard(temple)
            ).join('');
        }
    }
    
    centerOnUser() {
        if (this.userLocation && this.map) {
            this.map.setView([this.userLocation.latitude, this.userLocation.longitude], 14);
        } else {
            alert('இருப்பிட அனுமதி தேவை');
        }
    }
    
    zoomIn() {
        if (this.map) this.map.zoomIn();
    }
    
    zoomOut() {
        if (this.map) this.map.zoomOut();
    }
    
    displayCalendar() {
        const now = new Date();
        const year = now.getFullYear();
        const month = now.getMonth();
        const today = now.getDate();
        
        // Tamil month names for display
        const tamilMonthNames = ['ஜனவரி', 'பிப்ரவரி', 'மார்ச்', 'ஏப்ரல்', 'மே', 'ஜூன்', 
                                'ஜூலை', 'ஆகஸ்ட்', 'செப்டம்பர்', 'அக்டோபர்', 'நவம்பர்', 'டிசம்பர்'];
        
        // Update month title
        document.getElementById('calendarMonth').textContent = `${tamilMonthNames[month]} ${year}`;
        
        // Get festivals for this month
        const monthFestivals = this.getMonthFestivals(year, month + 1);
        const festivalDates = new Set(monthFestivals.map(f => new Date(f.date).getDate()));
        
        // Generate calendar
        const firstDay = new Date(year, month, 1).getDay();
        const daysInMonth = new Date(year, month + 1, 0).getDate();
        
        const calendarGrid = document.getElementById('calendarGrid');
        calendarGrid.innerHTML = '';
        
        // Add day headers
        const dayHeaders = ['ஞா', 'தி', 'செ', 'பு', 'வி', 'வெ', 'ச'];
        dayHeaders.forEach(day => {
            const header = document.createElement('div');
            header.className = 'calendar-header';
            header.textContent = day;
            calendarGrid.appendChild(header);
        });
        
        // Add empty cells for days before month starts
        for (let i = 0; i < firstDay; i++) {
            const emptyCell = document.createElement('div');
            calendarGrid.appendChild(emptyCell);
        }
        
        // Add days of month
        for (let day = 1; day <= daysInMonth; day++) {
            const dayCell = document.createElement('div');
            dayCell.className = 'calendar-day';
            
            if (day === today) {
                dayCell.classList.add('today');
            }
            
            if (festivalDates.has(day)) {
                dayCell.classList.add('has-festival');
                dayCell.onclick = () => this.showDayFestivals(year, month + 1, day);
            }
            
            dayCell.innerHTML = `
                <div class="calendar-day-number">${day}</div>
                ${festivalDates.has(day) ? '<div class="calendar-festival-dot"></div>' : ''}
            `;
            
            calendarGrid.appendChild(dayCell);
        }
        
        // Display festival list
        this.displayFestivalList(monthFestivals);
    }
    
    getMonthFestivals(year, month) {
        const festivals = [];
        
        // Get all festivals for the month
        for (const [type, festivalList] of Object.entries(this.festivalCalendar.festivals || {})) {
            festivalList.forEach(festival => {
                const festivalDate = new Date(festival.date);
                if (festivalDate.getFullYear() === year && festivalDate.getMonth() + 1 === month) {
                    festivals.push({...festival, category: type});
                }
            });
        }
        
        // Add major annual festivals
        (this.festivalCalendar.major_annual_festivals || []).forEach(festival => {
            const festivalDate = new Date(festival.date);
            if (festivalDate.getFullYear() === year && festivalDate.getMonth() + 1 === month) {
                festivals.push({...festival, category: 'major'});
            }
        });
        
        // Sort by date
        festivals.sort((a, b) => new Date(a.date) - new Date(b.date));
        
        return festivals;
    }
    
    displayFestivalList(festivals) {
        const container = document.getElementById('festivalList');
        
        if (festivals.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">📅</div>
                    <div class="empty-title">இந்த மாதம் விழாக்கள் இல்லை</div>
                </div>
            `;
            return;
        }
        
        container.innerHTML = festivals.map(festival => {
            const date = new Date(festival.date);
            const tamilMonth = this.tamilMonths[festival.tamil_month] || '';
            
            return `
                <div class="festival-card" onclick="app.showFestivalTemples('${festival.type || festival.name}')">
                    <div class="festival-date">${date.getDate()}</div>
                    <div class="festival-type">${festival.type || festival.name}</div>
                    <div class="festival-tamil-month">${tamilMonth} - ${festival.day || ''}</div>
                </div>
            `;
        }).join('');
    }
    
    showDayFestivals(year, month, day) {
        const dayFestivals = this.getMonthFestivals(year, month).filter(f => 
            new Date(f.date).getDate() === day
        );
        
        if (dayFestivals.length > 0) {
            alert(`${day} தேதி விழாக்கள்:\n${dayFestivals.map(f => f.type || f.name).join('\n')}`);
        }
    }
    
    showFestivalTemples(festivalName) {
        // Determine deity type based on festival
        let deityType = null;
        const festivalLower = festivalName.toLowerCase();
        
        if (festivalLower.includes('pradosham') || festivalLower.includes('shiva')) {
            deityType = 'Shiva';
        } else if (festivalLower.includes('ekadashi') || festivalLower.includes('vishnu') || festivalLower.includes('vaikunta')) {
            deityType = 'Vishnu';
        } else if (festivalLower.includes('sashti') || festivalLower.includes('murugan') || festivalLower.includes('skanda')) {
            deityType = 'Murugan';
        } else if (festivalLower.includes('pournami') || festivalLower.includes('amman') || festivalLower.includes('devi')) {
            deityType = 'Devi';
        }
        
        if (deityType) {
            // Filter temples by deity type
            const relevantTemples = this.temples.filter(temple => 
                temple.deity_type === deityType
            ).slice(0, 20);
            
            // Switch to home page and display results
            this.switchToHome();
            document.getElementById('templeListTitle').textContent = `${festivalName} - ${this.deityTamil[deityType]} கோயில்கள்`;
            
            const container = document.getElementById('templeList');
            if (relevantTemples.length > 0) {
                container.innerHTML = relevantTemples.map(temple => 
                    this.createTempleCard(temple)
                ).join('');
            } else {
                container.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-icon">🛕</div>
                        <div class="empty-title">கோயில்கள் இல்லை</div>
                    </div>
                `;
            }
        } else {
            alert(`${festivalName} - அனைத்து கோயில்களிலும் கொண்டாடப்படும்`);
        }
    }
    
    switchToHome() {
        // Programmatically switch to home page
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector('[onclick*="home"]').classList.add('active');
        
        document.querySelectorAll('.page').forEach(page => {
            page.classList.remove('active');
        });
        document.getElementById('homePage').classList.add('active');
        
        this.currentPage = 'home';
    }
    
    displayFeaturedTemples() {
        const container = document.getElementById('templeList');
        
        // Mix of temples: some with coordinates, some popular ones
        let displayTemples = [];
        
        // Add some temples with coordinates first
        displayTemples.push(...this.featuredTemples.slice(0, 5));
        
        // Add some temples from different districts for variety
        const districtSample = {};
        this.temples.forEach(temple => {
            if (!districtSample[temple.district] && Object.keys(districtSample).length < 5) {
                districtSample[temple.district] = temple;
            }
        });
        displayTemples.push(...Object.values(districtSample));
        
        // Limit to 15 temples for initial display
        displayTemples = displayTemples.slice(0, 15);
        
        container.innerHTML = displayTemples.map(temple => 
            this.createTempleCard(temple)
        ).join('');
        
        // Update title to show what's being displayed
        document.getElementById('templeListTitle').textContent = 'பிரபலமான கோயில்கள்';
    }
    
    displayNearbyTemples() {
        if (!this.userLocation) {
            this.displayFeaturedTemples();
            return;
        }
        
        const nearbyTemples = this.templesWithCoords
            .map(temple => ({
                ...temple,
                distance: this.calculateDistance(
                    this.userLocation.latitude,
                    this.userLocation.longitude,
                    temple.latitude,
                    temple.longitude
                )
            }))
            .filter(temple => temple.distance <= this.searchRadius)
            .sort((a, b) => a.distance - b.distance)
            .slice(0, 20);
        
        const container = document.getElementById('templeList');
        container.innerHTML = nearbyTemples.map(temple => 
            this.createTempleCard(temple, true)
        ).join('');
    }
    
    createTempleCard(temple, showDistance = false) {
        const tamilDeity = this.deityTamil[temple.deity_type] || temple.deity_type || '';
        const distance = showDistance && temple.distance 
            ? `<span class="distance-tag">${temple.distance.toFixed(1)} கி.மீ</span>` 
            : '';
        
        return `
            <div class="temple-card" onclick="app.showTempleDetails('${temple.temple_id}')">
                <div class="temple-card-header">
                    <div class="temple-name">${temple.tamil_name || temple.name}</div>
                    ${distance}
                </div>
                ${tamilDeity ? `<div class="temple-deity">🕉️ ${tamilDeity}</div>` : ''}
                <div class="temple-location">
                    <span class="location-icon">📍</span>
                    ${temple.district}${temple.pincode ? ', ' + temple.pincode : ''}
                </div>
            </div>
        `;
    }
    
    quickSearch(query) {
        if (!query.trim()) {
            this.displayFeaturedTemples();
            return;
        }
        
        const results = this.searchTemples(query).slice(0, 10);
        const container = document.getElementById('templeList');
        
        if (results.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">🔍</div>
                    <div class="empty-title">கோயில்கள் இல்லை</div>
                    <div class="empty-desc">வேறு தேடல் முயற்சிக்கவும்</div>
                </div>
            `;
            return;
        }
        
        container.innerHTML = results.map(temple => 
            this.createTempleCard(temple)
        ).join('');
    }
    
    searchTemples(query) {
        const searchTerms = query.toLowerCase().trim().split(' ');
        
        return this.temples.filter(temple => {
            const searchText = [
                temple.name,
                temple.tamil_name,
                temple.district,
                temple.address,
                temple.main_deity,
                temple.deity_type,
                temple.pincode
            ].filter(Boolean).join(' ').toLowerCase();
            
            return searchTerms.every(term => searchText.includes(term));
        });
    }
    
    filterByDeity(deityTamil) {
        // Find English deity type
        let deityType = Object.keys(this.deityTamil).find(
            key => this.deityTamil[key] === deityTamil
        );
        
        const filtered = this.temples.filter(temple => 
            temple.deity_type === deityType
        ).slice(0, 20);
        
        const container = document.getElementById('templeList');
        document.getElementById('templeListTitle').textContent = `${deityTamil} கோயில்கள்`;
        
        if (filtered.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">🛕</div>
                    <div class="empty-title">கோயில்கள் இல்லை</div>
                </div>
            `;
            return;
        }
        
        container.innerHTML = filtered.map(temple => 
            this.createTempleCard(temple)
        ).join('');
    }
    
    checkTodaysFestivals() {
        const today = new Date().toISOString().split('T')[0];
        const festivals = [];
        
        // Check all festival types
        for (const [type, festivalList] of Object.entries(this.festivalCalendar.festivals || {})) {
            festivals.push(...festivalList.filter(f => f.date === today));
        }
        
        // Check major annual festivals
        festivals.push(...(this.festivalCalendar.major_annual_festivals || [])
            .filter(f => f.date === today));
        
        if (festivals.length > 0) {
            const banner = document.getElementById('festivalBanner');
            const festivalName = document.getElementById('todayFestival');
            
            banner.style.display = 'block';
            
            // Get Tamil month name
            const tamilMonth = this.tamilMonths[festivals[0].tamil_month] || festivals[0].tamil_month;
            festivalName.textContent = `${festivals[0].type || festivals[0].name} - ${tamilMonth || ''}`;
        }
    }
    
    showTempleDetails(templeId) {
        const temple = this.temples.find(t => t.temple_id === templeId) || 
                      this.templesWithCoords.find(t => t.temple_id === templeId);
        
        if (!temple) return;
        
        const modal = document.getElementById('templeModal');
        const title = document.getElementById('modalTempleTitle');
        const body = document.getElementById('modalBody');
        
        title.textContent = temple.tamil_name || temple.name;
        
        const tamilDeity = this.deityTamil[temple.deity_type] || temple.deity_type || '';
        
        // Calculate distance if user location available
        let distance = '';
        if (this.userLocation && temple.latitude) {
            const dist = this.calculateDistance(
                this.userLocation.latitude,
                this.userLocation.longitude,
                temple.latitude,
                temple.longitude
            );
            distance = `${dist.toFixed(1)} கி.மீ தூரம்`;
        }
        
        body.innerHTML = `
            <!-- Temple Image Placeholder -->
            <div class="temple-image-placeholder">
                🛕
            </div>
            
            <!-- Basic Information -->
            <div class="detail-section">
                <div class="detail-section-title">அடிப்படை விவரங்கள்</div>
                
                <div class="detail-label">ஆங்கில பெயர்</div>
                <div class="detail-value">${temple.name}</div>
                
                ${temple.tamil_name ? `
                <div class="detail-label">தமிழ் பெயர்</div>
                <div class="detail-value">${temple.tamil_name}</div>
                ` : ''}
                
                ${temple.temple_id ? `
                <div class="detail-label">கோயில் குறியீடு</div>
                <div class="detail-value">${temple.temple_id}</div>
                ` : ''}
            </div>
            
            <!-- Location Details -->
            <div class="detail-section">
                <div class="detail-section-title">இருப்பிட விவரங்கள்</div>
                
                <div class="detail-label">முகவரி</div>
                <div class="detail-value">${temple.address || 'தகவல் இல்லை'}</div>
                
                <div class="detail-label">மாவட்டம்</div>
                <div class="detail-value">${temple.district || 'N/A'}</div>
                
                ${temple.pincode ? `
                <div class="detail-label">அஞ்சல் குறியீடு</div>
                <div class="detail-value">${temple.pincode}</div>
                ` : ''}
                
                ${distance ? `
                <div class="detail-label">தூரம்</div>
                <div class="detail-value">${distance}</div>
                ` : ''}
                
                ${temple.latitude ? `
                <div class="detail-label">GPS இருப்பிடம்</div>
                <div class="detail-value">${temple.latitude.toFixed(6)}, ${temple.longitude.toFixed(6)}</div>
                ` : ''}
            </div>
            
            <!-- Deity Information -->
            <div class="detail-section">
                <div class="detail-section-title">தெய்வ விவரங்கள்</div>
                
                ${temple.main_deity ? `
                <div class="detail-label">மூலவர் / பிரதான தெய்வம்</div>
                <div class="detail-value">${temple.main_deity}</div>
                ` : ''}
                
                ${temple.goddess ? `
                <div class="detail-label">அம்மன் / தாயார்</div>
                <div class="detail-value">${temple.goddess}</div>
                ` : ''}
                
                ${tamilDeity ? `
                <div class="detail-label">தெய்வ வகை</div>
                <div class="detail-value">${tamilDeity}</div>
                ` : ''}
            </div>
            
            <!-- Temple Features -->
            ${(temple.holy_water || temple.sacred_tree || temple.temple_tank) ? `
            <div class="detail-section">
                <div class="detail-section-title">கோயில் சிறப்புகள்</div>
                
                ${temple.holy_water ? `
                <div class="detail-label">தீர்த்தம் (புனித நீர்)</div>
                <div class="detail-value">${temple.holy_water}</div>
                ` : ''}
                
                ${temple.sacred_tree ? `
                <div class="detail-label">ஸ்தல விருட்சம் (புனித மரம்)</div>
                <div class="detail-value">${temple.sacred_tree}</div>
                ` : ''}
                
                ${temple.temple_tank ? `
                <div class="detail-label">குளம் / தெப்பக்குளம்</div>
                <div class="detail-value">${temple.temple_tank}</div>
                ` : ''}
            </div>
            ` : ''}
            
            <!-- Visiting Information -->
            ${(temple.timings || temple.phone) ? `
            <div class="detail-section">
                <div class="detail-section-title">வருகை தகவல்</div>
                
                ${temple.timings ? `
                <div class="detail-label">கோயில் திறக்கும் நேரம்</div>
                <div class="detail-value">${temple.timings}</div>
                ` : ''}
                
                ${temple.phone ? `
                <div class="detail-label">தொலைபேசி எண்</div>
                <div class="detail-value">${temple.phone}</div>
                ` : ''}
            </div>
            ` : ''}
            
            <!-- Festivals & Rituals -->
            ${(temple.festivals || temple.special_rituals) ? `
            <div class="detail-section">
                <div class="detail-section-title">விழாக்கள் & சிறப்பு பூஜைகள்</div>
                
                ${temple.festivals && temple.festivals.length > 0 ? `
                <div class="detail-label">முக்கிய விழாக்கள்</div>
                <div class="detail-value">${temple.festivals.join(', ')}</div>
                ` : ''}
                
                ${temple.special_rituals ? `
                <div class="detail-label">சிறப்பு பூஜைகள் / வழிபாடுகள்</div>
                <div class="detail-value">${temple.special_rituals}</div>
                ` : ''}
            </div>
            ` : ''}
            
            <!-- Historical Information -->
            ${(temple.inscriptions || temple.historical_period || temple.temple_age) ? `
            <div class="detail-section">
                <div class="detail-section-title">வரலாற்று தகவல்</div>
                
                ${temple.historical_period || temple.temple_age ? `
                <div class="detail-label">கால கட்டம் / வயது</div>
                <div class="detail-value">${temple.historical_period || temple.temple_age}</div>
                ` : ''}
                
                ${temple.inscriptions ? `
                <div class="detail-label">கல்வெட்டுகள்</div>
                <div class="detail-value">${temple.inscriptions}</div>
                ` : ''}
            </div>
            ` : ''}
            
            <!-- Administrative Info -->
            ${(temple.income_category || temple.temple_type) ? `
            <div class="detail-section">
                <div class="detail-section-title">நிர்வாக தகவல்</div>
                
                ${temple.temple_type ? `
                <div class="detail-label">கோயில் வகை</div>
                <div class="detail-value">${temple.temple_type}</div>
                ` : ''}
                
                ${temple.income_category ? `
                <div class="detail-label">வருமான வகை</div>
                <div class="detail-value">${temple.income_category}</div>
                ` : ''}
            </div>
            ` : ''}
            
            <!-- Data Completeness -->
            ${temple.data_completeness ? `
            <div class="detail-section">
                <div class="detail-section-title">தரவு முழுமை</div>
                <div class="detail-value">
                    <div style="background: #e9ecef; border-radius: 8px; height: 20px; overflow: hidden;">
                        <div style="background: linear-gradient(90deg, #667eea, #764ba2); height: 100%; width: ${temple.data_completeness}%; transition: width 0.3s;"></div>
                    </div>
                    <div style="text-align: center; margin-top: 8px; color: #6c757d;">
                        ${temple.data_completeness}% முழுமையான தகவல்
                    </div>
                </div>
            </div>
            ` : ''}
            
            <!-- Action Buttons -->
            ${this.userLocation && temple.latitude ? `
            <button class="location-btn" style="width: 100%; margin: 16px 0; padding: 16px; font-size: 16px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 12px;" 
                    onclick="app.openMaps(${temple.latitude}, ${temple.longitude})">
                📍 Google Maps இல் வழிகாட்டி பெறுக
            </button>
            ` : temple.pincode ? `
            <button class="location-btn" style="width: 100%; margin: 16px 0; padding: 16px; font-size: 16px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 12px;" 
                    onclick="app.searchByPincode('${temple.pincode}')">
                📮 ${temple.pincode} பகுதியில் மற்ற கோயில்கள் காண்க
            </button>
            ` : ''}
            
            <!-- Report/Feedback -->
            <div style="text-align: center; padding: 20px; border-top: 1px solid #e9ecef; margin-top: 20px;">
                <p style="color: #6c757d; font-size: 14px; margin-bottom: 12px;">தகவல் தவறாக உள்ளதா?</p>
                <button style="background: #f8f9fa; color: #6c757d; border: 1px solid #dee2e6; padding: 8px 16px; border-radius: 8px; font-size: 14px;">
                    ✏️ திருத்தம் பரிந்துரை
                </button>
            </div>
            
            <!-- Data Source -->
            <div style="text-align: center; color: #adb5bd; font-size: 12px; padding: 20px 0;">
                தரவு ஆதாரம்: HRCE தமிழ்நாடு அரசு<br>
                ${temple.location_confidence ? `GPS துல்லியம்: ${temple.location_confidence}` : ''}
            </div>
        `;
        
        modal.classList.add('active');
        document.querySelector('.modal-content').scrollTop = 0;
    }
    
    searchByPincode(pincode) {
        // Close modal and search for temples in same pincode
        this.closeModal();
        this.switchToHome();
        
        const results = this.temples.filter(t => t.pincode === pincode).slice(0, 20);
        document.getElementById('templeListTitle').textContent = `${pincode} - பகுதி கோயில்கள்`;
        
        const container = document.getElementById('templeList');
        if (results.length > 0) {
            container.innerHTML = results.map(temple => 
                this.createTempleCard(temple)
            ).join('');
        }
    }
    
    closeModal() {
        document.getElementById('templeModal').classList.remove('active');
    }
    
    openMaps(lat, lon) {
        const url = `https://www.google.com/maps/dir/?api=1&destination=${lat},${lon}`;
        window.open(url, '_blank');
    }
    
    calculateDistance(lat1, lon1, lat2, lon2) {
        const R = 6371; // Earth's radius in km
        const dLat = this.toRad(lat2 - lat1);
        const dLon = this.toRad(lon2 - lon1);
        const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                  Math.cos(this.toRad(lat1)) * Math.cos(this.toRad(lat2)) *
                  Math.sin(dLon/2) * Math.sin(dLon/2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
        return R * c;
    }
    
    toRad(value) {
        return value * Math.PI / 180;
    }
}

// Initialize app
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new TamilTempleApp();
});