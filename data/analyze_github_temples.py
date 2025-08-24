#!/usr/bin/env python3
"""
Analyze and Convert GitHub Temple Dataset
Parse the consolidated Tamil Nadu temples Excel file
"""

import pandas as pd
import json
from pathlib import Path

def analyze_temple_data():
    """Analyze the downloaded temple dataset"""
    
    print("\n" + "="*60)
    print(" TAMIL NADU TEMPLES DATASET ANALYSIS")
    print("="*60)
    
    # Read Excel file
    excel_file = "tn_temples_consolidated.xlsx"
    
    try:
        # Read all sheets
        excel_data = pd.ExcelFile(excel_file)
        print(f"\n📊 Excel file loaded: {excel_file}")
        print(f"   Sheets available: {excel_data.sheet_names}")
        
        # Read the main sheet (usually first one)
        df = pd.read_excel(excel_file, sheet_name=0)
        
        print(f"\n📈 Dataset Overview:")
        print(f"   Total temples: {len(df)}")
        print(f"   Columns: {list(df.columns)}")
        
        # Analyze data structure
        print(f"\n🔍 Data Structure Analysis:")
        print(f"   Shape: {df.shape}")
        print(f"   Data types:")
        for col in df.columns:
            print(f"     - {col}: {df[col].dtype} (nulls: {df[col].isna().sum()})")
        
        # Sample data
        print(f"\n📝 Sample Data (first 5 temples):")
        print(df.head().to_string())
        
        # District-wise distribution
        if 'District' in df.columns or 'district' in df.columns:
            district_col = 'District' if 'District' in df.columns else 'district'
            district_counts = df[district_col].value_counts()
            
            print(f"\n📍 District-wise Distribution:")
            print(f"   Total districts: {len(district_counts)}")
            print("\n   Top 5 districts by temple count:")
            for district, count in district_counts.head().items():
                print(f"     - {district}: {count} temples")
        
        # Check for temple IDs
        id_columns = [col for col in df.columns if 'id' in col.lower() or 'code' in col.lower()]
        if id_columns:
            print(f"\n🔑 ID Columns found: {id_columns}")
            for col in id_columns:
                sample_ids = df[col].dropna().head(5).tolist()
                print(f"   {col} samples: {sample_ids}")
        
        # Check for location data
        location_cols = [col for col in df.columns if any(x in col.lower() for x in ['lat', 'long', 'location', 'address'])]
        if location_cols:
            print(f"\n📍 Location columns: {location_cols}")
        
        # Check for deity/festival information
        deity_cols = [col for col in df.columns if any(x in col.lower() for x in ['deity', 'god', 'goddess', 'festival', 'celebration'])]
        if deity_cols:
            print(f"\n🛕 Deity/Festival columns: {deity_cols}")
        
        # Save as JSON for easier processing
        print(f"\n💾 Converting to JSON...")
        
        # Convert to JSON-serializable format
        temples_json = df.fillna("").to_dict('records')
        
        # Save full dataset
        output_dir = Path("raw_data")
        output_dir.mkdir(exist_ok=True)
        
        with open(output_dir / "tn_temples_full.json", "w", encoding="utf-8") as f:
            json.dump(temples_json, f, ensure_ascii=False, indent=2)
        print(f"   ✓ Full dataset saved: raw_data/tn_temples_full.json")
        
        # Save sample of 100 temples for validation
        sample_100 = temples_json[:100]
        with open(output_dir / "tn_temples_sample_100.json", "w", encoding="utf-8") as f:
            json.dump(sample_100, f, ensure_ascii=False, indent=2)
        print(f"   ✓ Sample (100 temples) saved: raw_data/tn_temples_sample_100.json")
        
        # Save district-wise summary
        if 'District' in df.columns or 'district' in df.columns:
            district_col = 'District' if 'District' in df.columns else 'district'
            district_summary = {}
            
            for district in df[district_col].unique():
                if pd.notna(district):
                    district_temples = df[df[district_col] == district]
                    district_summary[district] = {
                        "count": len(district_temples),
                        "sample_temples": district_temples.head(5).fillna("").to_dict('records')
                    }
            
            with open(output_dir / "tn_temples_by_district.json", "w", encoding="utf-8") as f:
                json.dump(district_summary, f, ensure_ascii=False, indent=2)
            print(f"   ✓ District summary saved: raw_data/tn_temples_by_district.json")
        
        # Generate validation report
        print(f"\n✅ VALIDATION REPORT")
        print(f"   ─────────────────")
        print(f"   Total temples: {len(df)}")
        print(f"   Districts covered: {df[district_col].nunique() if 'District' in df.columns or 'district' in df.columns else 'N/A'}")
        print(f"   Data completeness:")
        
        for col in df.columns[:10]:  # Check first 10 columns
            completeness = (1 - df[col].isna().sum() / len(df)) * 100
            print(f"     - {col}: {completeness:.1f}% complete")
        
        # Find Sankarankovil temple for validation
        print(f"\n🔍 Searching for known temples...")
        search_terms = ["Sankarankovil", "Sankaran", "சங்கரன்", "நெல்லை"]
        
        for term in search_terms:
            matches = df[df.apply(lambda row: row.astype(str).str.contains(term, case=False).any(), axis=1)]
            if not matches.empty:
                print(f"   Found {len(matches)} matches for '{term}':")
                for idx, temple in matches.head(3).iterrows():
                    # Find the most relevant column with temple name
                    name_cols = [col for col in df.columns if 'name' in col.lower() or 'temple' in col.lower()]
                    if name_cols:
                        temple_name = temple[name_cols[0]]
                    else:
                        temple_name = str(temple.iloc[0])
                    print(f"     - {temple_name}")
        
        return df
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None

def create_app_ready_format(df):
    """Convert DataFrame to app-ready format"""
    
    print(f"\n📱 Creating App-Ready Format...")
    
    app_data = {
        "metadata": {
            "source": "GitHub - vindicindic/tn-hindu-temples",
            "total_temples": len(df),
            "last_updated": "2024",
            "districts": df['District'].nunique() if 'District' in df.columns else 0
        },
        "temples": []
    }
    
    # Process each temple
    for idx, row in df.iterrows():
        temple = {
            "id": f"TEMPLE_{idx:05d}",
            "original_data": row.fillna("").to_dict()
        }
        
        # Extract key fields (adjust based on actual column names)
        name_cols = [col for col in df.columns if 'name' in col.lower() or 'temple' in col.lower()]
        if name_cols:
            temple["name"] = row[name_cols[0]]
        
        district_cols = [col for col in df.columns if 'district' in col.lower()]
        if district_cols:
            temple["district"] = row[district_cols[0]]
        
        # Add location if available
        lat_cols = [col for col in df.columns if 'lat' in col.lower()]
        lon_cols = [col for col in df.columns if 'lon' in col.lower() or 'lng' in col.lower()]
        
        if lat_cols and lon_cols:
            try:
                temple["location"] = {
                    "latitude": float(row[lat_cols[0]]),
                    "longitude": float(row[lon_cols[0]])
                }
            except:
                pass
        
        app_data["temples"].append(temple)
    
    # Save app-ready format
    with open("raw_data/temples_app_format.json", "w", encoding="utf-8") as f:
        json.dump(app_data, f, ensure_ascii=False, indent=2)
    
    print(f"   ✓ App format saved: raw_data/temples_app_format.json")
    
    return app_data

def main():
    """Main function"""
    
    # Analyze the data
    df = analyze_temple_data()
    
    if df is not None:
        # Create app-ready format
        app_data = create_app_ready_format(df)
        
        print(f"\n" + "="*60)
        print(" 🎉 SUCCESS!")
        print("="*60)
        print(f"\n✅ Successfully processed {len(df)} temples from GitHub dataset!")
        print(f"\n📁 Generated files:")
        print(f"   1. raw_data/tn_temples_full.json - Complete dataset")
        print(f"   2. raw_data/tn_temples_sample_100.json - Sample for validation")
        print(f"   3. raw_data/tn_temples_by_district.json - District-wise breakdown")
        print(f"   4. raw_data/temples_app_format.json - App-ready format")
        
        print(f"\n🚀 Next Steps:")
        print(f"   1. Validate data quality with known temples")
        print(f"   2. Cross-reference with HR&CE official data if needed")
        print(f"   3. Add calculated festival dates using Swiss Ephemeris")
        print(f"   4. Design app database schema")
        print(f"   5. Build the Tamil calendar app!")
    else:
        print(f"\n❌ Failed to process temple data")
        print(f"   Please check if the Excel file is valid")

if __name__ == "__main__":
    main()