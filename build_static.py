#!/usr/bin/env python3
"""
Static site generator for BizLLCFinder
Converts Flask app to static HTML files for Vercel deployment
"""

import os
import shutil
from flask import Flask
from app import app as flask_app
import requests
from urllib.parse import urljoin

def create_static_app():
    """Create a static version of the Flask app"""
    static_app = Flask(__name__)
    
    # Copy all routes from the main app
    for rule in flask_app.url_map.iter_rules():
        if rule.endpoint != 'static':
            static_app.add_url_rule(
                rule.rule,
                rule.endpoint,
                flask_app.view_functions[rule.endpoint],
                methods=rule.methods
            )
    
    return static_app

def generate_static_files():
    """Generate static HTML files"""
    print("🚀 Generating static files for Vercel deployment...")
    
    # Create static app
    static_app = create_static_app()
    
    # Create output directory
    output_dir = "static_site"
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)
    
    # Copy static assets
    if os.path.exists("static"):
        shutil.copytree("static", os.path.join(output_dir, "static"))
    
    # Copy templates
    if os.path.exists("templates"):
        shutil.copytree("templates", os.path.join(output_dir, "templates"))
    
    # Copy data files
    data_files = ["LLC Data.csv", "LLC_Data_Optimized.csv", "LLC_Data_Optimized.json"]
    for file in data_files:
        if os.path.exists(file):
            shutil.copy2(file, output_dir)
    
    # Copy other necessary files
    files_to_copy = ["requirements.txt", "README.md", "vercel.json", "runtime.txt"]
    for file in files_to_copy:
        if os.path.exists(file):
            shutil.copy2(file, output_dir)
    
    # Create index.html (homepage)
    with static_app.test_client() as client:
        response = client.get('/')
        if response.status_code == 200:
            with open(os.path.join(output_dir, "index.html"), "w", encoding="utf-8") as f:
                f.write(response.data.decode("utf-8"))
            print("✅ Generated index.html")
    
    # Create about page
    with static_app.test_client() as client:
        response = client.get('/about/')
        if response.status_code == 200:
            os.makedirs(os.path.join(output_dir, "about"), exist_ok=True)
            with open(os.path.join(output_dir, "about", "index.html"), "w", encoding="utf-8") as f:
                f.write(response.data.decode("utf-8"))
            print("✅ Generated about/index.html")
    
    # Create contact page
    with static_app.test_client() as client:
        response = client.get('/contact/')
        if response.status_code == 200:
            os.makedirs(os.path.join(output_dir, "contact"), exist_ok=True)
            with open(os.path.join(output_dir, "contact", "index.html"), "w", encoding="utf-8") as f:
                f.write(response.data.decode("utf-8"))
            print("✅ Generated contact/index.html")
    
    # Create legal pages
    legal_pages = ['privacy', 'disclosure', 'terms']
    for page in legal_pages:
        with static_app.test_client() as client:
            response = client.get(f'/{page}/')
            if response.status_code == 200:
                os.makedirs(os.path.join(output_dir, page), exist_ok=True)
                with open(os.path.join(output_dir, page, "index.html"), "w", encoding="utf-8") as f:
                    f.write(response.data.decode("utf-8"))
                print(f"✅ Generated {page}/index.html")
    
    # Create tools pages
    tools_pages = ['llc-cost-by-state', 'foreign-qualification-cost', 'llc-vs-s-corp-tax-savings']
    for tool in tools_pages:
        with static_app.test_client() as client:
            response = client.get(f'/tools/{tool}/')
            if response.status_code == 200:
                os.makedirs(os.path.join(output_dir, "tools", tool), exist_ok=True)
                with open(os.path.join(output_dir, "tools", tool, "index.html"), "w", encoding="utf-8") as f:
                    f.write(response.data.decode("utf-8"))
                print(f"✅ Generated tools/{tool}/index.html")
    
    # Create use case hub pages
    use_cases = [
        'doctors', 'rental-properties', 'ecommerce', 'contractor', 'vending-machines',
        'realtors', 'small-business', 'airbnb', 'trucking', 'cannabis', 'hair-salon',
        'etsy', 'amazon-fba', 'bakery', 'investment-property', 'clothing-brand',
        'dropshipping', 'roofers', 'photographer', 'shopify', 'handyman', 'uber',
        'lyft', 'limo', 'handymen', 'electricians', 'plumbers', 'landscapers',
        'cleaning-businesses', 'painters', 'hvac-technicians', 'dentists',
        'chiropractors', 'therapists', 'nutritionists', 'personal-trainers',
        'landlords', 'airbnb-hosts', 'real-estate-agents', 'property-management',
        'house-flippers', 'e-commerce', 'freelancers', 'consultants',
        'social-media-influencers', 'online-coaches', 'content-creators',
        'stock-trading', 'day-trading', 'crypto-trading', 'financial-advisors',
        'rideshare-drivers', 'restaurants', 'food-trucks', 'salons', 'barbers',
        'event-planners', 'drywall-installers', 'window-installers',
        'insulation-companies', 'solar-panel-installers', 'fencing-companies',
        'videographers', 'podcasters', 'marketing-agencies', 'seo-consultants',
        'pr-firms', 'it-consultants', 'software-developers', 'cybersecurity-firms',
        'msps', 'saas-businesses', 'woodworking-businesses', 'jewelry-makers',
        'candle-makers', 'soap-makers', 'farmers', 'ranchers', 'beekeepers',
        'greenhouse-businesses', 'landscaping-supply-companies', 'driving-schools',
        'test-prep-tutors', 'language-instructors', 'career-coaches',
        'corporate-trainers', 'charter-bus-companies', 'boat-rental-businesses',
        'trucking-dispatchers', 'tour-guides', 'llc-registration', 'accounting', 'legal'
    ]
    
    for use_case in use_cases:
        with static_app.test_client() as client:
            response = client.get(f'/use-cases/{use_case}/')
            if response.status_code == 200:
                os.makedirs(os.path.join(output_dir, "use-cases", use_case), exist_ok=True)
                with open(os.path.join(output_dir, "use-cases", use_case, "index.html"), "w", encoding="utf-8") as f:
                    f.write(response.data.decode("utf-8"))
                print(f"✅ Generated use-cases/{use_case}/index.html")
    
    # Create sitemap
    with static_app.test_client() as client:
        response = client.get('/sitemap.xml')
        if response.status_code == 200:
            with open(os.path.join(output_dir, "sitemap.xml"), "w", encoding="utf-8") as f:
                f.write(response.data.decode("utf-8"))
            print("✅ Generated sitemap.xml")
    
    print(f"\n🎉 Static site generated successfully in '{output_dir}' directory!")
    print("📁 Ready for Vercel deployment!")
    
    return output_dir

if __name__ == "__main__":
    generate_static_files()
