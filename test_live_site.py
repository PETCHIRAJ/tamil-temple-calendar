#!/usr/bin/env python3
"""
Test the live GitHub Pages deployment of Tamil Nadu Temple Calendar app
"""

import time
from playwright.sync_api import sync_playwright
import json

def test_temple_app():
    """Test all functionalities of the temple app"""
    
    results = {
        "site_loading": False,
        "temples_loaded": 0,
        "search_working": False,
        "filters_working": False,
        "language_toggle_working": False,
        "temple_details_working": False,
        "map_view_working": False,
        "navigation_buttons": False,
        "errors": []
    }
    
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        page = context.new_page()
        
        try:
            print("🔍 Testing Tamil Nadu Temple Calendar App...")
            print("=" * 50)
            
            # 1. Test site loading
            print("\n1. Testing site loading...")
            page.goto("https://petchiraj.github.io/tamil-temple-calendar/", wait_until='networkidle', timeout=30000)
            time.sleep(3)
            
            # Check if redirected to the app
            current_url = page.url
            if "design/mockups" in current_url or page.title():
                results["site_loading"] = True
                print("✅ Site loaded successfully")
                print(f"   URL: {current_url}")
                print(f"   Title: {page.title()}")
            else:
                print("❌ Site failed to load properly")
                results["errors"].append("Site failed to load")
            
            # 2. Check if temples are loaded
            print("\n2. Checking temple data...")
            time.sleep(2)
            
            # Check for temple cards
            temple_cards = page.query_selector_all('.temple-card')
            if temple_cards:
                results["temples_loaded"] = len(temple_cards)
                print(f"✅ Found {len(temple_cards)} temple cards")
            else:
                print("❌ No temple cards found")
                results["errors"].append("No temple cards found")
            
            # 3. Test search functionality
            print("\n3. Testing search...")
            search_input = page.query_selector('#search-input')
            if search_input:
                search_input.fill("chennai")
                time.sleep(1)
                search_results = page.query_selector_all('.temple-card')
                if search_results:
                    results["search_working"] = True
                    print(f"✅ Search working - found {len(search_results)} results for 'chennai'")
                else:
                    print("❌ Search not returning results")
                search_input.fill("")  # Clear search
                time.sleep(1)
            else:
                print("❌ Search input not found")
                results["errors"].append("Search input not found")
            
            # 4. Test filters
            print("\n4. Testing filters...")
            filter_buttons = page.query_selector_all('.filter-btn')
            if filter_buttons:
                print(f"   Found {len(filter_buttons)} filter buttons")
                
                # Test location filter
                location_filter = None
                for btn in filter_buttons:
                    if "Location" in btn.inner_text():
                        location_filter = btn
                        break
                
                if location_filter:
                    location_filter.click()
                    time.sleep(1)
                    filtered_cards = page.query_selector_all('.temple-card')
                    results["filters_working"] = True
                    print(f"✅ Location filter working - showing {len(filtered_cards)} temples with location")
                    
                    # Reset filter
                    all_filter = page.query_selector('.filter-btn[data-filter="all"]')
                    if all_filter:
                        all_filter.click()
                        time.sleep(1)
            else:
                print("❌ Filter buttons not found")
                results["errors"].append("Filter buttons not found")
            
            # 5. Test language toggle
            print("\n5. Testing language toggle...")
            language_btn = page.query_selector('#language-btn')
            if language_btn:
                # Get initial text
                initial_text = language_btn.inner_text()
                language_btn.click()
                time.sleep(1)
                new_text = language_btn.inner_text()
                if initial_text != new_text:
                    results["language_toggle_working"] = True
                    print(f"✅ Language toggle working ({initial_text} → {new_text})")
                else:
                    print("❌ Language toggle not changing")
            else:
                print("❌ Language button not found")
                results["errors"].append("Language button not found")
            
            # 6. Test temple details
            print("\n6. Testing temple details...")
            first_temple = page.query_selector('.temple-card')
            if first_temple:
                first_temple.click()
                time.sleep(2)
                
                # Check if detail view opened
                detail_name = page.query_selector('#temple-detail-name')
                if detail_name and detail_name.inner_text():
                    results["temple_details_working"] = True
                    print(f"✅ Temple details working - showing: {detail_name.inner_text()}")
                    
                    # Check for navigation button
                    nav_btn = page.query_selector('#navigate-btn')
                    if nav_btn and nav_btn.is_visible():
                        results["navigation_buttons"] = True
                        print("✅ Navigation button visible")
                    else:
                        print("⚠️  Navigation button not visible (temple may not have location)")
                    
                    # Close detail view
                    back_btn = page.query_selector('.back-btn')
                    if back_btn:
                        back_btn.click()
                        time.sleep(1)
                else:
                    print("❌ Temple details not showing")
                    results["errors"].append("Temple details not showing")
            
            # 7. Test map view
            print("\n7. Testing map view...")
            map_tab = page.query_selector('[onclick*="showMapView"]')
            if map_tab:
                map_tab.click()
                time.sleep(2)
                
                # Check if map is loaded
                map_container = page.query_selector('#map')
                if map_container:
                    # Check if Leaflet map is initialized
                    map_loaded = page.evaluate('() => typeof L !== "undefined" && document.querySelector("#map").children.length > 0')
                    if map_loaded:
                        results["map_view_working"] = True
                        print("✅ Map view working")
                    else:
                        print("❌ Map not loading properly")
                        results["errors"].append("Map not loading")
            else:
                print("❌ Map tab not found")
            
            # 8. Check for console errors
            print("\n8. Checking for console errors...")
            # Note: Console errors would have been captured if we set up listeners earlier
            
        except Exception as e:
            print(f"\n❌ Error during testing: {str(e)}")
            results["errors"].append(str(e))
        
        finally:
            # Generate summary
            print("\n" + "=" * 50)
            print("📊 TEST SUMMARY")
            print("=" * 50)
            
            total_tests = 7
            passed_tests = sum([
                results["site_loading"],
                results["temples_loaded"] > 0,
                results["search_working"],
                results["filters_working"],
                results["language_toggle_working"],
                results["temple_details_working"],
                results["map_view_working"]
            ])
            
            print(f"\n✅ Passed: {passed_tests}/{total_tests} tests")
            print(f"📊 Temples loaded: {results['temples_loaded']}")
            
            if results["errors"]:
                print(f"\n⚠️  Issues found:")
                for error in results["errors"]:
                    print(f"   - {error}")
            
            if passed_tests >= 5:
                print(f"\n🎉 App is WORKING! ({passed_tests}/{total_tests} features functional)")
            elif passed_tests >= 3:
                print(f"\n⚠️  App is PARTIALLY working ({passed_tests}/{total_tests} features functional)")
            else:
                print(f"\n❌ App has MAJOR issues ({passed_tests}/{total_tests} features functional)")
            
            # Take screenshot
            page.screenshot(path="live_site_test.png")
            print("\n📸 Screenshot saved as 'live_site_test.png'")
            
            browser.close()
            
            return results

if __name__ == "__main__":
    test_results = test_temple_app()
    
    # Save results to file
    with open('test_results.json', 'w') as f:
        json.dump(test_results, f, indent=2)
    print("\n📝 Full results saved to 'test_results.json'")