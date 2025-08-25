// Tamil Temple Guide App JavaScript
class TempleApp {
    constructor() {
        this.temples = [
            {
                "temple_id": "TM001",
                "name": "Arulmigu Aabathsagayeswara Swamy Temple",
                "tamil_name": "ஆபத்சகாயேஸ்வரர் கோயில்",
                "district": "Thanjavur",
                "location": "Aduthurai",
                "deity_type": "Shiva",
                "main_deity": "Sri Aabathsahayeswarar",
                "goddess": "Sri Pavalakkodiyammai",
                "timings": "7:00 AM - 12:00 PM, 5:00 PM - 8:30 PM",
                "phone": "04435-279234",
                "festivals": ["PanguniUthiram", "Navarathri", "Shivarathri", "Arudra Dharshan"],
                "architectural_style": "Dravidian",
                "historical_period": "Chola Period",
                "latitude": 10.9936,
                "longitude": 79.4816,
                "distance": 2.5
            },
            {
                "temple_id": "TM002", 
                "name": "Sri Ranganathaswamy Temple",
                "tamil_name": "ஸ்ரீ ரங்கநாதசுவாமி கோயில்",
                "district": "Tiruchirappalli",
                "location": "Srirangam",
                "deity_type": "Vishnu",
                "main_deity": "Sri Ranganatha",
                "goddess": "Sri Ranganayaki",
                "timings": "6:00 AM - 12:00 PM, 3:30 PM - 9:00 PM",
                "phone": "0431-2435085",
                "festivals": ["Vaikunta Ekadasi", "Brahmotsavam", "Panguni Uthiram"],
                "architectural_style": "Dravidian",
                "historical_period": "Chola Period",
                "latitude": 10.8505,
                "longitude": 78.6969,
                "distance": 5.2
            },
            {
                "temple_id": "TM003",
                "name": "Arulmigu Dhandayuthapani Swamy Temple", 
                "tamil_name": "அருள்மிகு தண்டாயுதபாணி சுவாமி கோயில்",
                "district": "Dindigul",
                "location": "Palani",
                "deity_type": "Murugan",
                "main_deity": "Sri Dhandayuthapani",
                "goddess": "Sri Valli Devasena",
                "timings": "5:00 AM - 10:00 PM",
                "phone": "04545-243277",
                "festivals": ["Thai Pusam", "Panguni Uthiram", "Skanda Sashti"],
                "architectural_style": "Dravidian",
                "historical_period": "Ancient",
                "latitude": 10.4515,
                "longitude": 77.5152,
                "distance": 8.7
            },
            {
                "temple_id": "TM004",
                "name": "Arulmigu Meenakshi Sundareshwarar Temple",
                "tamil_name": "அருள்மிகு மீனாட்சி சுந்தரேஸ்வரர் கோயில்",
                "district": "Madurai", 
                "location": "Madurai",
                "deity_type": "Shiva",
                "main_deity": "Sri Sundareshwarar",
                "goddess": "Sri Meenakshi",
                "timings": "5:00 AM - 12:30 PM, 4:00 PM - 10:00 PM",
                "phone": "0452-2344360",
                "festivals": ["Meenakshi Tirukalyanam", "Navarathri", "Float Festival"],
                "architectural_style": "Dravidian",
                "historical_period": "Pandyan Period",
                "latitude": 9.9195,
                "longitude": 78.1194,
                "distance": 12.3
            },
            {
                "temple_id": "TM005",
                "name": "Arulmigu Rajarajeshwari Amman Temple",
                "tamil_name": "அருள்மிகு ராஜராஜேஸ்வரி அம்மன் கோயில்",
                "district": "Chennai",
                "location": "Besant Nagar",
                "deity_type": "Devi",
                "main_deity": "Sri Rajarajeshwari",
                "goddess": "Sri Rajarajeshwari Amman",
                "timings": "6:00 AM - 11:00 AM, 4:00 PM - 8:00 PM",
                "phone": "044-24461555",
                "festivals": ["Navarathri", "Diwali", "Thai Poosam"],
                "architectural_style": "Modern",
                "historical_period": "Contemporary",
                "latitude": 12.9986,
                "longitude": 80.2669,
                "distance": 15.8
            }
        ];
        
        this.currentScreen = 'splash-screen';
        this.selectedTemple = null;
        this.filters = {
            district: '',
            deityType: [],
            distance: 50,
            period: ''
        };
        this.searchQuery = '';
        this.favorites = this.getFavorites();
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.showSplashScreen();
        this.loadPopularTemples();
    }
    
    setupEventListeners() {
        // Wait for elements to be available before setting up listeners
        setTimeout(() => {
            this.bindEventListeners();
        }, 100);
    }
    
    bindEventListeners() {
        // Navigation buttons
        const filterBtn = document.getElementById('filter-btn');
        const nearbyBtn = document.getElementById('nearby-btn');
        const searchBtn = document.getElementById('search-btn');
        const searchInput = document.getElementById('search-input');
        
        if (filterBtn) {
            filterBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.navigateToScreen('filter-screen');
            });
        }
        
        if (nearbyBtn) {
            nearbyBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.showNearbyTemples();
            });
        }
        
        // Search functionality
        if (searchBtn) {
            searchBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.performSearch();
            });
        }
        
        if (searchInput) {
            searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    this.performSearch();
                }
            });
        }
        
        // Quick filter chips
        document.querySelectorAll('.filter-chip').forEach(chip => {
            chip.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleQuickFilter(e.target);
            });
        });
        
        // Back buttons
        const filterBackBtn = document.getElementById('filter-back-btn');
        const resultsBackBtn = document.getElementById('results-back-btn');
        const detailsBackBtn = document.getElementById('details-back-btn');
        
        if (filterBackBtn) {
            filterBackBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.navigateToScreen('home-screen');
            });
        }
        
        if (resultsBackBtn) {
            resultsBackBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.navigateToScreen('home-screen');
            });
        }
        
        if (detailsBackBtn) {
            detailsBackBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.navigateToScreen('results-screen');
            });
        }
        
        // Filter screen controls
        const distanceSlider = document.getElementById('distance-slider');
        if (distanceSlider) {
            distanceSlider.addEventListener('input', (e) => {
                const distanceValue = document.getElementById('distance-value');
                if (distanceValue) {
                    distanceValue.textContent = e.target.value;
                }
                this.filters.distance = parseInt(e.target.value);
            });
        }
        
        document.querySelectorAll('.deity-chip').forEach(chip => {
            chip.addEventListener('click', (e) => {
                e.preventDefault();
                this.toggleDeityFilter(e.target);
            });
        });
        
        const applyFilterBtn = document.getElementById('apply-filter-btn');
        const clearFilterBtn = document.getElementById('clear-filter-btn');
        
        if (applyFilterBtn) {
            applyFilterBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.applyFilters();
            });
        }
        
        if (clearFilterBtn) {
            clearFilterBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.clearFilters();
            });
        }
        
        // Temple details tabs
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                this.switchTab(e.target.dataset.tab);
            });
        });
        
        // Temple action buttons
        const callBtn = document.getElementById('call-btn');
        const directionsBtn = document.getElementById('directions-btn');
        const shareBtn = document.getElementById('share-btn');
        const favoriteBtn = document.getElementById('favorite-btn');
        
        if (callBtn) {
            callBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.callTemple();
            });
        }
        
        if (directionsBtn) {
            directionsBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.getDirections();
            });
        }
        
        if (shareBtn) {
            shareBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.shareTemple();
            });
        }
        
        if (favoriteBtn) {
            favoriteBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.toggleFavorite();
            });
        }
        
        // Bottom navigation
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleNavigation(e.currentTarget);
            });
        });
    }
    
    showSplashScreen() {
        this.currentScreen = 'splash-screen';
        this.updateScreenVisibility();
        
        // Auto-navigate to home screen after 3 seconds
        setTimeout(() => {
            this.navigateToScreen('home-screen');
        }, 3000);
    }
    
    navigateToScreen(screenId) {
        console.log(`Navigating to: ${screenId}`);
        this.currentScreen = screenId;
        this.updateScreenVisibility();
        
        // Update bottom navigation
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        if (screenId === 'home-screen') {
            const homeBtn = document.querySelector('[data-screen="home"]');
            if (homeBtn) homeBtn.classList.add('active');
        }
    }
    
    updateScreenVisibility() {
        // Hide all screens
        document.querySelectorAll('.screen').forEach(screen => {
            screen.classList.remove('active');
            screen.style.display = 'none';
        });
        
        // Show current screen
        const currentScreenEl = document.getElementById(this.currentScreen);
        if (currentScreenEl) {
            currentScreenEl.classList.add('active');
            currentScreenEl.style.display = 'flex';
        }
    }
    
    loadPopularTemples() {
        setTimeout(() => {
            const grid = document.getElementById('popular-temples-grid');
            if (!grid) return;
            
            const popularTemples = this.temples.slice(0, 3);
            grid.innerHTML = '';
            
            popularTemples.forEach(temple => {
                const card = this.createTempleCard(temple);
                grid.appendChild(card);
            });
        }, 100);
    }
    
    createTempleCard(temple) {
        const card = document.createElement('div');
        card.className = 'temple-card';
        card.setAttribute('data-temple-id', temple.temple_id);
        
        const isFavorite = this.favorites.includes(temple.temple_id);
        const favoriteIcon = isFavorite ? '❤️' : '🤍';
        
        card.innerHTML = `
            <div class="temple-card-header">
                <div>
                    <h4 class="temple-name-tamil">${temple.tamil_name}</h4>
                    <p class="temple-name-english">${temple.name}</p>
                </div>
                <div class="temple-actions">
                    <button class="action-icon favorite-icon" data-temple-id="${temple.temple_id}">${favoriteIcon}</button>
                    <button class="action-icon">→</button>
                </div>
            </div>
            <div class="temple-info">
                <div class="temple-info-item">
                    <span class="info-label">முக்கிய தெய்வம் | Main Deity:</span>
                    <span class="info-value">${temple.main_deity}</span>
                </div>
                <div class="temple-info-item">
                    <span class="info-label">இடம் | Location:</span>
                    <span class="info-value">${temple.location} (${temple.distance}km)</span>
                </div>
                <div class="temple-info-item">
                    <span class="info-label">தொலைபேசி | Phone:</span>
                    <span class="info-value">${temple.phone}</span>
                </div>
            </div>
        `;
        
        // Add click events
        card.addEventListener('click', (e) => {
            if (!e.target.classList.contains('action-icon')) {
                this.showTempleDetails(temple);
            }
        });
        
        const favoriteBtn = card.querySelector('.favorite-icon');
        if (favoriteBtn) {
            favoriteBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleFavoriteFromCard(temple.temple_id, favoriteBtn);
            });
        }
        
        return card;
    }
    
    handleQuickFilter(chip) {
        const deity = chip.dataset.deity;
        console.log(`Quick filter clicked: ${deity}`);
        
        // Reset all chips
        document.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
        chip.classList.add('active');
        
        if (deity === 'nearby') {
            this.showNearbyTemples();
        } else {
            // Filter temples by deity
            const results = this.temples.filter(temple => 
                temple.deity_type.toLowerCase() === deity.toLowerCase()
            );
            console.log(`Found ${results.length} temples for ${deity}`);
            this.showSearchResults(results, `${deity} கோயில்கள் | ${deity} Temples`);
        }
    }
    
    performSearch() {
        const searchInput = document.getElementById('search-input');
        if (!searchInput) return;
        
        const query = searchInput.value.trim().toLowerCase();
        console.log(`Searching for: ${query}`);
        
        if (!query) {
            alert('தயவுசெய்து தேடல் சொல்லை உள்ளிடுக | Please enter search term');
            return;
        }
        
        this.searchQuery = query;
        const results = this.temples.filter(temple => 
            temple.name.toLowerCase().includes(query) ||
            temple.tamil_name.includes(query) ||
            temple.location.toLowerCase().includes(query) ||
            temple.main_deity.toLowerCase().includes(query)
        );
        
        console.log(`Search results: ${results.length} temples found`);
        this.showSearchResults(results, `"${query}" தேடல் முடிவுகள் | Search Results for "${query}"`);
    }
    
    showNearbyTemples() {
        console.log('Showing nearby temples');
        const nearbyTemples = [...this.temples].sort((a, b) => a.distance - b.distance);
        this.showSearchResults(nearbyTemples, 'அருகிலுள்ள கோயில்கள் | Nearby Temples');
    }
    
    showSearchResults(results, title) {
        console.log(`Showing search results: ${results.length} temples`);
        this.navigateToScreen('results-screen');
        
        setTimeout(() => {
            const titleEl = document.getElementById('results-title');
            const countEl = document.getElementById('results-count');
            const listEl = document.getElementById('results-list');
            
            if (titleEl) titleEl.textContent = title;
            if (countEl) {
                countEl.textContent = `${results.length} கோயில்கள் கண்டறியப்பட்டன | ${results.length} temples found`;
            }
            
            if (listEl) {
                listEl.innerHTML = '';
                results.forEach(temple => {
                    const card = this.createTempleCard(temple);
                    listEl.appendChild(card);
                });
            }
        }, 100);
    }
    
    showTempleDetails(temple) {
        console.log(`Showing details for: ${temple.name}`);
        this.selectedTemple = temple;
        this.navigateToScreen('details-screen');
        
        setTimeout(() => {
            // Update temple header
            const elements = {
                'temple-name': `${temple.tamil_name} | ${temple.name}`,
                'temple-tamil-name': temple.tamil_name,
                'temple-english-name': temple.name,
                'temple-location': `${temple.location}, ${temple.district} (${temple.distance}km away)`,
                'main-deity': temple.main_deity,
                'goddess': temple.goddess,
                'temple-phone': temple.phone,
                'temple-district': temple.district,
                'temple-timings': temple.timings,
                'architecture': temple.architectural_style,
                'historical-period': temple.historical_period
            };
            
            // Update all elements
            Object.entries(elements).forEach(([id, value]) => {
                const element = document.getElementById(id);
                if (element) element.textContent = value;
            });
            
            // Update festivals list
            const festivalsList = document.getElementById('festivals-list');
            if (festivalsList) {
                festivalsList.innerHTML = '';
                temple.festivals.forEach(festival => {
                    const li = document.createElement('li');
                    li.textContent = festival;
                    festivalsList.appendChild(li);
                });
            }
            
            // Update favorite button
            this.updateFavoriteButton();
            
            // Reset to first tab
            this.switchTab('info');
        }, 100);
    }
    
    switchTab(tabName) {
        console.log(`Switching to tab: ${tabName}`);
        
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        const activeTabBtn = document.querySelector(`[data-tab="${tabName}"]`);
        if (activeTabBtn) activeTabBtn.classList.add('active');
        
        // Update tab panels
        document.querySelectorAll('.tab-panel').forEach(panel => {
            panel.classList.remove('active');
            panel.style.display = 'none';
        });
        const activePanel = document.getElementById(`${tabName}-tab`);
        if (activePanel) {
            activePanel.classList.add('active');
            activePanel.style.display = 'block';
        }
    }
    
    toggleDeityFilter(chip) {
        chip.classList.toggle('active');
        const deity = chip.dataset.deity;
        
        if (chip.classList.contains('active')) {
            if (!this.filters.deityType.includes(deity)) {
                this.filters.deityType.push(deity);
            }
        } else {
            this.filters.deityType = this.filters.deityType.filter(d => d !== deity);
        }
        console.log('Deity filters:', this.filters.deityType);
    }
    
    applyFilters() {
        const districtFilter = document.getElementById('district-filter');
        const periodFilter = document.getElementById('period-filter');
        
        this.filters.district = districtFilter ? districtFilter.value : '';
        this.filters.period = periodFilter ? periodFilter.value : '';
        
        console.log('Applying filters:', this.filters);
        
        let results = this.temples.filter(temple => {
            // District filter
            if (this.filters.district && temple.district !== this.filters.district) {
                return false;
            }
            
            // Deity type filter
            if (this.filters.deityType.length > 0 && 
                !this.filters.deityType.includes(temple.deity_type)) {
                return false;
            }
            
            // Distance filter
            if (temple.distance > this.filters.distance) {
                return false;
            }
            
            // Period filter
            if (this.filters.period && temple.historical_period !== this.filters.period) {
                return false;
            }
            
            return true;
        });
        
        // Sort by distance
        results.sort((a, b) => a.distance - b.distance);
        
        console.log(`Filter results: ${results.length} temples found`);
        this.showSearchResults(results, 'வடிகட்டப்பட்ட முடிவுகள் | Filtered Results');
    }
    
    clearFilters() {
        console.log('Clearing filters');
        this.filters = {
            district: '',
            deityType: [],
            distance: 50,
            period: ''
        };
        
        // Reset form elements
        const districtFilter = document.getElementById('district-filter');
        const periodFilter = document.getElementById('period-filter');
        const distanceSlider = document.getElementById('distance-slider');
        const distanceValue = document.getElementById('distance-value');
        
        if (districtFilter) districtFilter.value = '';
        if (periodFilter) periodFilter.value = '';
        if (distanceSlider) distanceSlider.value = '25';
        if (distanceValue) distanceValue.textContent = '25';
        
        // Reset deity chips
        document.querySelectorAll('.deity-chip').forEach(chip => {
            chip.classList.remove('active');
        });
    }
    
    callTemple() {
        if (this.selectedTemple && this.selectedTemple.phone) {
            alert(`அழைக்கிறது | Calling ${this.selectedTemple.phone}`);
        }
    }
    
    getDirections() {
        if (this.selectedTemple) {
            alert(`${this.selectedTemple.location} க்கு வழி காட்டுதல் | Getting directions to ${this.selectedTemple.location}`);
        }
    }
    
    shareTemple() {
        if (this.selectedTemple) {
            const shareText = `${this.selectedTemple.tamil_name} | ${this.selectedTemple.name}\n${this.selectedTemple.location}, ${this.selectedTemple.district}`;
            alert(`பகிர்தல் | Sharing:\n${shareText}`);
        }
    }
    
    toggleFavorite() {
        if (!this.selectedTemple) return;
        
        const templeId = this.selectedTemple.temple_id;
        if (this.favorites.includes(templeId)) {
            this.favorites = this.favorites.filter(id => id !== templeId);
        } else {
            this.favorites.push(templeId);
        }
        
        this.saveFavorites();
        this.updateFavoriteButton();
        
        const action = this.favorites.includes(templeId) ? 'சேர்க்கப்பட்டது | Added' : 'நீக்கப்பட்டது | Removed';
        alert(`பிடித்தவைகளில் ${action} to favorites`);
    }
    
    toggleFavoriteFromCard(templeId, button) {
        if (this.favorites.includes(templeId)) {
            this.favorites = this.favorites.filter(id => id !== templeId);
            button.textContent = '🤍';
        } else {
            this.favorites.push(templeId);
            button.textContent = '❤️';
        }
        
        this.saveFavorites();
    }
    
    updateFavoriteButton() {
        if (!this.selectedTemple) return;
        
        const isFavorite = this.favorites.includes(this.selectedTemple.temple_id);
        const favoriteBtn = document.getElementById('favorite-btn');
        
        if (favoriteBtn) {
            if (isFavorite) {
                favoriteBtn.innerHTML = '❤️ <span id="favorite-text">நீக்கு | Remove</span>';
            } else {
                favoriteBtn.innerHTML = '🤍 <span id="favorite-text">சேர் | Add</span>';
            }
        }
    }
    
    handleNavigation(navBtn) {
        const screen = navBtn.dataset.screen;
        console.log(`Bottom nav clicked: ${screen}`);
        
        // Update active nav button
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        navBtn.classList.add('active');
        
        // Navigate to appropriate screen
        switch(screen) {
            case 'home':
                this.navigateToScreen('home-screen');
                break;
            case 'search':
                this.navigateToScreen('home-screen');
                setTimeout(() => {
                    const searchInput = document.getElementById('search-input');
                    if (searchInput) searchInput.focus();
                }, 100);
                break;
            case 'nearby':
                this.showNearbyTemples();
                break;
            case 'favorites':
                this.showFavorites();
                break;
        }
    }
    
    showFavorites() {
        console.log(`Showing favorites: ${this.favorites.length} temples`);
        const favoriteTemples = this.temples.filter(temple => 
            this.favorites.includes(temple.temple_id)
        );
        this.showSearchResults(favoriteTemples, 'பிடித்த கோயில்கள் | Favorite Temples');
    }
    
    getFavorites() {
        try {
            return JSON.parse(localStorage.getItem('temple_favorites') || '[]');
        } catch (e) {
            console.error('Error loading favorites:', e);
            return [];
        }
    }
    
    saveFavorites() {
        try {
            localStorage.setItem('temple_favorites', JSON.stringify(this.favorites));
        } catch (e) {
            console.error('Error saving favorites:', e);
        }
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('Initializing Tamil Temple App');
    window.templeApp = new TempleApp();
});

// Enhanced search with debouncing
document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        const debouncedSearch = Utils.debounce(() => {
            if (window.templeApp && searchInput.value.trim()) {
                window.templeApp.performSearch();
            }
        }, 500);
        
        searchInput.addEventListener('input', debouncedSearch);
    }
});

// Utility functions
const Utils = {
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
};

// Handle keyboard navigation
document.addEventListener('keydown', (event) => {
    if (!window.templeApp) return;
    
    switch(event.key) {
        case 'Escape':
            if (window.templeApp.currentScreen === 'details-screen') {
                window.templeApp.navigateToScreen('results-screen');
            } else if (window.templeApp.currentScreen !== 'home-screen') {
                window.templeApp.navigateToScreen('home-screen');
            }
            break;
    }
});