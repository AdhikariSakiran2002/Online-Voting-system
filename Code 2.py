# MVP: Carbon Footprint Optimizer using Agentic AI
# Purpose: Estimate and reduce carbon emissions from CI/CD deployments

import os
import time
import json
import requests
from datetime import datetime
from typing import Dict, Any

# ========== CONFIG ==========
CLOUD_REGION = "us-east-1"
DEPLOY_DURATION_MINUTES = 10
GITHUB_REPO = "org/repo"
ELECTRICITY_MAPS_TOKEN = os.getenv("ELECTRICITY_MAPS_API_TOKEN")

# Sample static emissions data for prototype
CLOUD_REGION_EMISSIONS = {
    "us-east-1": 0.393,  # kg CO2 per kWh
    "us-west-1": 0.201,
    "eu-west-1": 0.078,
    "ap-southeast-1": 0.482
}

# Power consumption estimate (kW) during a typical deployment
DEPLOY_POWER_USAGE_KW = 0.5

# ========== CARBON TRACKER MODULE ==========
def estimate_emissions(region: str, duration_minutes: int) -> float:
    """Estimate carbon emissions based on region and duration."""
    kwh_used = (DEPLOY_POWER_USAGE_KW * duration_minutes) / 60
    emissions_factor = CLOUD_REGION_EMISSIONS.get(region, 0.4)
    return round(kwh_used * emissions_factor, 4)

# ========== ELECTRICITY MAPS API ==========
def get_live_carbon_intensity(zone: str = "US-NE") -> float:
    url = f"https://api.electricitymap.org/v3/carbon-intensity/latest?zone={zone}"
    headers = {"auth-token": ELECTRICITY_MAPS_TOKEN}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data['carbonIntensity']['forecast']
    return 400  # default fallback value

# ========== AGENTIC AI SUGGESTION ENGINE ==========
def suggest_optimized_deployment() -> Dict[str, Any]:
    current_emissions = estimate_emissions(CLOUD_REGION, DEPLOY_DURATION_MINUTES)
    suggestions = []

    for region, factor in CLOUD_REGION_EMISSIONS.items():
        alt_emission = estimate_emissions(region, DEPLOY_DURATION_MINUTES)
        if alt_emission < current_emissions:
            suggestions.append({
                "region": region,
                "estimated_kg_co2": alt_emission,
                "saving_percent": round(100 * (current_emissions - alt_emission) / current_emissions, 2)
            })

    return {
        "current_emission_kg": current_emissions,
        "better_regions": sorted(suggestions, key=lambda x: x['estimated_kg_co2'])
    }

# ========== OUTPUT REPORT ==========
def report_emissions():
    print("\n🚀 Deployment Carbon Optimization Report")
    print("====================================")
    results = suggest_optimized_deployment()
    print(f"Current Region: {CLOUD_REGION}")
    print(f"Estimated Emissions: {results['current_emission_kg']} kg CO₂\n")
    if results['better_regions']:
        print("Better Regions Suggestions:")
        for region in results['better_regions']:
            print(f"- {region['region']} => {region['estimated_kg_co2']} kg CO₂ (↓ {region['saving_percent']}%)")
    else:
        print("✅ Current region is optimal.")

# ========== MAIN ==========
if __name__ == "__main__":
    report_emissions()
