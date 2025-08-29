#!/usr/bin/env python3
"""
Update HTML with all 88 festivals from the complete data
"""

import json

# Read the complete festival data
with open('utils/utils/festivals_js_data.js', 'r') as f:
    js_content = f.read()
    
# Extract just the array content (between [ and ])
start = js_content.find('[')
end = js_content.rfind(']') + 1
festivals_array = js_content[start:end]

# Read the HTML file
with open('design/mockups/index.html', 'r') as f:
    html_content = f.read()

# Find the loadFestivals function
start_marker = "// Complete festival data with all 88 festivals including monthly observances"
end_marker = "];"

start_pos = html_content.find(start_marker)
if start_pos == -1:
    print("Could not find start marker")
    exit(1)

# Find the end of the festival array
end_pos = html_content.find("];", start_pos)
if end_pos == -1:
    print("Could not find end of festival array")
    exit(1)

# Find the actual start of the array
array_start = html_content.find("const allFestivals = [", start_pos)
if array_start == -1:
    print("Could not find festival array declaration")
    exit(1)

# Replace the festival array with complete data
new_content = (
    html_content[:array_start] + 
    "const allFestivals = " + 
    festivals_array +
    html_content[end_pos:]
)

# Write back the updated HTML
with open('design/mockups/index.html', 'w') as f:
    f.write(new_content)

print("✅ Updated HTML with all 89 festivals!")
print("   The app now has complete festival data")