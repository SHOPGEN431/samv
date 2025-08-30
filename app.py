from flask import Flask, render_template, request, jsonify, make_response
import csv
import re
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path
import os

app = Flask(__name__)

# Global data storage
businesses_data = []
states_data = defaultdict(list)
cities_data = defaultdict(list)

def load_data_from_csv():
    """Load business data from CSV file"""
    # Check if running on Vercel (production) or local development
    if os.environ.get('VERCEL_ENV'):
        # For Vercel deployment, use the CSV file in the repository
        csv_file = "LLC Data.csv"
    else:
        # Local development - use current directory
        csv_file = "LLC Data.csv"

    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            for row in reader:
                business = {
                    'name': row.get('name', '').strip(),
                    'phone': format_phone(row.get('phone', '')),
                    'full_address': row.get('full_address', '').strip(),
                    'city': row.get('city', '').strip(),
                    'postal_code': row.get('postal_code', '').strip(),
                    'state': row.get('state', '').strip(),
                    'rating': row.get('rating', ''),
                    'reviews': row.get('reviews', ''),
                    'site': row.get('site', ''),
                    'category': row.get('category', ''),
                    'type': row.get('type', '')
                }

                # Skip if missing essential data
                if not business['name'] or not business['state']:
                    continue

                businesses_data.append(business)

                # Organize by state
                states_data[business['state']].append(business)

                # Organize by city (within state)
                city_key = f"{business['city']}_{business['state']}"
                cities_data[city_key].append(business)
        
        print(f"Loaded {len(businesses_data)} businesses")
        print(f"States: {len(states_data)}")
        print(f"Cities: {len(cities_data)}")

    except FileNotFoundError:
        print(f"Error: CSV file not found at {csv_file}")
        create_sample_data()
    except Exception as e:
        print(f"Error processing CSV: {e}")
        create_sample_data()

    # If no data was loaded, create sample data
    if not businesses_data:
        print("No business data loaded, creating sample data")
        create_sample_data()

def create_sample_data():
    """Create sample data for Vercel deployment"""
    sample_businesses = [
        {
            'name': 'ABC Legal Services',
            'phone': '+1 (555) 123-4567',
            'full_address': '123 Main St, Los Angeles, CA 90210',
            'city': 'Los Angeles',
            'postal_code': '90210',
            'state': 'CA',
            'rating': '4.8',
            'reviews': '150',
            'site': 'https://abclegal.com',
            'category': 'certified public accountant',
            'type': 'Professional Service'
        },
        {
            'name': 'XYZ Business Solutions',
            'phone': '+1 (555) 987-6543',
            'full_address': '456 Oak Ave, New York, NY 10001',
            'city': 'New York',
            'postal_code': '10001',
            'state': 'NY',
            'rating': '4.7',
            'reviews': '120',
            'site': 'https://xyzbusiness.com',
            'category': 'business management consultant',
            'type': 'Business Consultant'
        },
        {
            'name': 'Best LLC Services',
            'phone': '+1 (555) 456-7890',
            'full_address': '789 Pine St, Chicago, IL 60601',
            'city': 'Chicago',
            'postal_code': '60601',
            'state': 'IL',
            'rating': '4.9',
            'reviews': '200',
            'site': 'https://bestllc.com',
            'category': 'legal services',
            'type': 'Legal Service'
        }
    ]

    for business in sample_businesses:
        businesses_data.append(business)
        states_data[business['state']].append(business)
        city_key = f"{business['city']}_{business['state']}"
        cities_data[city_key].append(business)

    print(f"Created {len(businesses_data)} sample businesses")

def format_phone(phone):
    """Format phone number for display"""
    if not phone:
        return ""
    # Remove all non-digits
    digits = re.sub(r'\D', '', str(phone))
    if len(digits) == 11 and digits.startswith('1'):
        digits = digits[1:]
    if len(digits) == 10:
        return f"+1 ({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    return str(phone)

def clean_text(text):
    """Clean and format text for URLs"""
    if not text:
        return ""
    # Remove special characters and replace spaces with hyphens
    cleaned = re.sub(r'[^a-zA-Z0-9\s-]', '', str(text))
    cleaned = re.sub(r'\s+', '-', cleaned.strip())
    return cleaned.lower()

def get_state_full_name(state_code):
    """Convert state code to full name"""
    state_names = {
        'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California',
        'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia',
        'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa',
        'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
        'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi', 'MO': 'Missouri',
        'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada', 'NH': 'New Hampshire', 'NJ': 'New Jersey',
        'NM': 'New Mexico', 'NY': 'New York', 'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio',
        'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
        'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VT': 'Vermont',
        'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming',
        'DC': 'District of Columbia'
    }
    return state_names.get(state_code.upper(), state_code)

# Load data when app starts
load_data_from_csv()

@app.route('/')
def index():
    """Homepage - serve static HTML like ramzan repository"""
    return app.send_static_file('index.html')

@app.route('/index.html')
def index_html():
    """Alternative route for index.html"""
    return app.send_static_file('index.html')

@app.route('/about/')
def about():
    """About Us page"""
    total_businesses = len(businesses_data)
    return render_template('about.html', total_businesses=total_businesses)

@app.route('/contact/')
def contact():
    """Contact Us page"""
    return render_template('contact.html')

@app.route('/privacy/')
def privacy():
    """Privacy Policy page"""
    return render_template('privacy.html')

@app.route('/disclosure/')
def disclosure():
    """Disclosure page"""
    return render_template('disclosure.html')

@app.route('/terms/')
def terms():
    """Terms and Conditions page"""
    return render_template('terms.html')

@app.route('/sitemap.xml')
def sitemap():
    """XML Sitemap"""
    return render_template('sitemap.xml'), 200, {'Content-Type': 'application/xml'}

@app.route('/use-cases/<category>/')
def use_case_hub(category):
    """Use case hub page"""
    # Get businesses for this category
    category_businesses = []
    for business in businesses_data:
        if business.get('category', '').lower() == category.lower():
            category_businesses.append(business)
    
    # Get states for this category
    category_states = defaultdict(list)
    for business in category_businesses:
        category_states[business['state']].append(business)
    
    # Convert to list of tuples for template
    states_list = [(state, businesses) for state, businesses in category_states.items()]
    states_list.sort(key=lambda x: len(x[1]), reverse=True)
    
    return render_template('use_case_hub.html',
                         category=category,
                         businesses=category_businesses,
                         states=states_list,
                         total_businesses=len(category_businesses))

@app.route('/use-cases/<category>/<state>/')
def use_case_state(category, state):
    """Use case state page"""
    # Get businesses for this category and state
    state_businesses = []
    for business in businesses_data:
        if (business.get('category', '').lower() == category.lower() and 
            business.get('state', '').upper() == state.upper()):
            state_businesses.append(business)
    
    # Get cities for this category and state
    cities = defaultdict(list)
    for business in state_businesses:
        if business['city']:
            cities[business['city']].append(business)
    
    # Convert to list of tuples for template
    cities_list = [(city, businesses) for city, businesses in cities.items()]
    cities_list.sort(key=lambda x: len(x[1]), reverse=True)
    
    return render_template('use_case_state.html',
                         category=category,
                         state=state,
                         businesses=state_businesses,
                         cities=cities_list,
                         total_businesses=len(state_businesses))

# For Vercel deployment
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
