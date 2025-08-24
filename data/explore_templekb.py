#!/usr/bin/env python3
"""
Explore TempleKB Dataset
Check if it contains useful data for Tamil Nadu temples
"""

import requests
import json
from pathlib import Path

def explore_templekb():
    """Download and explore TempleKB dataset"""
    
    print("\n" + "="*60)
    print(" EXPLORING TEMPLEKB DATASET")
    print("="*60)
    
    # GitHub API to explore repository structure
    repo_api = "https://api.github.com/repos/priyaradhakrishnan0/templeKB"
    contents_api = "https://api.github.com/repos/priyaradhakrishnan0/templeKB/contents"
    
    try:
        # Get repository info
        print("\n1. Fetching repository information...")
        resp = requests.get(repo_api)
        if resp.status_code == 200:
            repo_info = resp.json()
            print(f"   Repository: {repo_info.get('full_name')}")
            print(f"   Description: {repo_info.get('description')}")
            print(f"   Last updated: {repo_info.get('updated_at')}")
        
        # Get repository contents
        print("\n2. Exploring repository structure...")
        resp = requests.get(contents_api)
        if resp.status_code == 200:
            contents = resp.json()
            
            print("\n   Repository contents:")
            for item in contents:
                print(f"   - {item['name']} ({item['type']})")
                if item['name'] == 'corpus' and item['type'] == 'dir':
                    # Explore corpus directory
                    corpus_url = item['url']
                    corpus_resp = requests.get(corpus_url)
                    if corpus_resp.status_code == 200:
                        corpus_contents = corpus_resp.json()
                        print(f"\n   Corpus directory contents:")
                        for corpus_item in corpus_contents[:10]:  # First 10 items
                            print(f"     - {corpus_item['name']}")
        
        # Try to get sample data files
        print("\n3. Looking for data files...")
        
        # Common data file patterns
        data_urls = [
            "https://raw.githubusercontent.com/priyaradhakrishnan0/templeKB/master/corpus/temple_facts.json",
            "https://raw.githubusercontent.com/priyaradhakrishnan0/templeKB/master/corpus/temples.json",
            "https://raw.githubusercontent.com/priyaradhakrishnan0/templeKB/master/corpus/temple_data.csv",
            "https://raw.githubusercontent.com/priyaradhakrishnan0/templeKB/master/temple_list.txt",
            "https://raw.githubusercontent.com/priyaradhakrishnan0/templeKB/master/README.md"
        ]
        
        found_data = False
        for url in data_urls:
            try:
                resp = requests.get(url, timeout=5)
                if resp.status_code == 200:
                    filename = url.split('/')[-1]
                    print(f"   ✓ Found: {filename}")
                    
                    # Save README for analysis
                    if filename == "README.md":
                        Path("raw_data/templekb").mkdir(parents=True, exist_ok=True)
                        with open(f"raw_data/templekb/{filename}", "w") as f:
                            f.write(resp.text)
                        
                        # Parse README for useful info
                        content = resp.text.lower()
                        if "tamil" in content:
                            print(f"     → Mentions Tamil temples!")
                        if "deity" in content or "deities" in content:
                            print(f"     → Contains deity information")
                        if "festival" in content:
                            print(f"     → Contains festival information")
                    
                    # If JSON, try to parse
                    if filename.endswith('.json'):
                        try:
                            data = resp.json()
                            print(f"     → Contains {len(data)} entries")
                            # Save sample
                            with open(f"raw_data/templekb/sample_{filename}", "w") as f:
                                json.dump(data[:10] if isinstance(data, list) else data, f, indent=2)
                        except:
                            pass
                    
                    found_data = True
            except:
                continue
        
        if not found_data:
            print("   ✗ No standard data files found")
        
        # Check for Tamil Nadu specific content
        print("\n4. Checking for Tamil Nadu temples...")
        
        # Try to get temple list or index
        temple_list_urls = [
            "https://raw.githubusercontent.com/priyaradhakrishnan0/templeKB/master/corpus/temple_list.txt",
            "https://raw.githubusercontent.com/priyaradhakrishnan0/templeKB/master/corpus/temples.txt",
            "https://raw.githubusercontent.com/priyaradhakrishnan0/templeKB/master/temple_index.txt"
        ]
        
        tamil_temples_found = False
        for url in temple_list_urls:
            try:
                resp = requests.get(url, timeout=5)
                if resp.status_code == 200:
                    content = resp.text
                    
                    # Check for Tamil Nadu temples
                    tn_keywords = ["tamil nadu", "chennai", "madurai", "thanjavur", 
                                  "kanchipuram", "trichy", "coimbatore", "tirunelveli"]
                    
                    for keyword in tn_keywords:
                        if keyword in content.lower():
                            tamil_temples_found = True
                            print(f"   ✓ Found references to {keyword}")
                            break
            except:
                continue
        
        if not tamil_temples_found:
            print("   ✗ No specific Tamil Nadu temple references found")
        
        print("\n" + "="*60)
        print(" SUMMARY")
        print("="*60)
        
        print("\n📊 TempleKB Dataset Overview:")
        print("  - Academic project for temple knowledge base")
        print("  - Contains ~4,933 facts about 573 temples")
        print("  - Includes deity and language information")
        print("  - Uses NLP/BERT for processing")
        
        print("\n🎯 Relevance to Our Project:")
        print("  - May contain additional deity relationships")
        print("  - Could provide mythological context")
        print("  - Might have festival descriptions")
        print("  - Limited to 573 temples (we have 46,004)")
        
        print("\n⚠️ Limitations:")
        print("  - Much smaller dataset than ours")
        print("  - May not focus on Tamil Nadu")
        print("  - Academic format (may need processing)")
        print("  - Unclear data structure without downloading")
        
        print("\n💡 Recommendation:")
        print("  - Our HR&CE dataset is more comprehensive")
        print("  - TempleKB might add deity/mythology context")
        print("  - Could be useful for famous temples only")
        print("  - Not essential for the app's core functionality")
        
    except Exception as e:
        print(f"\n❌ Error exploring TempleKB: {e}")

if __name__ == "__main__":
    explore_templekb()