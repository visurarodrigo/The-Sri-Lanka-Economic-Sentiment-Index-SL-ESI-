import pandas as pd
import os
from pathlib import Path

# Define paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / 'src' / 'data' / 'reference'
OUTPUT_PATH = OUTPUT_DIR / 'key_events.csv'

def build_event_annotations():
    print("🚀 Starting Phase 5: Building Event Annotation Layer...")
    
    # Define key events based on Sri Lanka's economic and political timeline (2020-2026)
    events = [
        {
            "date": "2020-03-20",
            "label": "COVID-19 Lockdown",
            "category": "External Shock",
            "description": "Global pandemic hits Sri Lanka; strict lockdowns halt tourism and economic activity."
        },
        {
            "date": "2021-04-27",
            "label": "Organic Fertilizer Ban",
            "category": "Policy Shock",
            "description": "Government bans chemical fertilizers, triggering a severe agricultural crisis and food inflation."
        },
        {
            "date": "2022-04-12",
            "label": "Sovereign Default",
            "category": "Economic Crisis",
            "description": "Sri Lanka defaults on its sovereign debt for the first time in its history amid severe forex shortages."
        },
        {
            "date": "2022-07-09",
            "label": "President Flees Country",
            "category": "Political Crisis",
            "description": "Mass protests force President Gotabaya Rajapaksa to flee the country amid economic collapse."
        },
        {
            "date": "2022-07-22",
            "label": "New President Elected",
            "category": "Political Shift",
            "description": "Ranil Wickremesinghe is elected as the new President to stabilize the economy."
        },
        {
            "date": "2023-03-20",
            "label": "IMF Bailout Approved",
            "category": "Economic Recovery",
            "description": "IMF approves a $2.9 billion Extended Fund Facility (EFF) bailout package to restore economic stability."
        },
        {
            "date": "2024-09-21",
            "label": "Presidential Election",
            "category": "Political Shift",
            "description": "Anura Kumara Dissanayake (NPP/JVP) wins the presidential election, marking a historic political shift."
        },
        {
            "date": "2024-11-14",
            "label": "Parliamentary Election",
            "category": "Political Shift",
            "description": "NPP wins a historic supermajority in parliament, signaling strong mandate for structural reforms."
        },
        {
            "date": "2025-04-09",
            "label": "Global Trade War / US Tariffs",
            "category": "External Shock",
            "description": "US imposes sweeping global tariffs, creating uncertainty for Sri Lankan exports and global trade."
        },
        {
            "date": "2025-11-28",
            "label": "Cyclone Ditwah",
            "category": "Natural Disaster",
            "description": "Devastating cyclone hits Sri Lanka, causing widespread damage to infrastructure and agriculture."
        },
        {
            "date": "2026-03-01",
            "label": "US-Iran Conflict Escalation",
            "category": "Geopolitical Shock",
            "description": "Escalation in the Middle East disrupts global oil supply chains, spiking fuel costs and impacting tourism."
        },
        {
            "date": "2026-05-16",
            "label": "Vehicle Import Liberalization",
            "category": "Policy Reform",
            "description": "Government relaxes strict vehicle import bans, signaling economic normalization and forex stability."
        }
    ]
    
    # Convert to DataFrame
    df_events = pd.DataFrame(events)
    
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Save to CSV
    df_events.to_csv(OUTPUT_PATH, index=False)
    
    print(f"\n✅ Success! Saved event annotations to {OUTPUT_PATH}")
    print("\n📊 Preview of Key Events:")
    print(df_events.to_string(index=False))
    
    return df_events

if __name__ == "__main__":
    build_event_annotations()