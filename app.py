from flask import Flask, render_template, request, jsonify
import pandas as pd
import os
from collections import defaultdict
import re

app = Flask(__name__)

# Load and process the CSV data
def load_data():
    csv_path = os.path.join(os.path.dirname(__file__), 'LLC Data.csv')
    df = pd.read_csv(csv_path)
    
    # Clean and filter data
    df = df.dropna(subset=['name', 'city', 'state', 'rating'])
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
    df = df[df['rating'] > 0]  # Only businesses with ratings
    
    # Clean city and state names
    df['city'] = df['city'].str.strip()
    df['state'] = df['state'].str.strip()
    
    return df

# Load data once at startup
try:
    data = load_data()
    print(f"Loaded {len(data)} business records")
except Exception as e:
    print(f"Error loading data: {e}")
    data = pd.DataFrame()

def get_unique_states():
    """Get list of unique states"""
    return sorted(data['state'].unique().tolist())



def get_state_full_name(state_abbr):
    """Convert state abbreviation to full name"""
    state_mapping = {
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
    return state_mapping.get(state_abbr.upper(), state_abbr)

def get_state_llc_costs():
    """Get LLC formation costs for each state"""
    return {
        'AL': {'filing_fee': 200, 'annual_report': 100, 'registered_agent': 50, 'total_first_year': 250, 'gov_website': 'https://www.sos.alabama.gov/business-entities'},
        'AK': {'filing_fee': 250, 'annual_report': 100, 'registered_agent': 50, 'total_first_year': 300, 'gov_website': 'https://www.commerce.alaska.gov/web/cbpl/businesslicensing/businessentities.aspx'},
        'AZ': {'filing_fee': 50, 'annual_report': 0, 'registered_agent': 50, 'total_first_year': 100, 'gov_website': 'https://azcc.gov/divisions/corporations'},
        'AR': {'filing_fee': 45, 'annual_report': 150, 'registered_agent': 50, 'total_first_year': 95, 'gov_website': 'https://www.sos.arkansas.gov/business-commercial-services'},
        'CA': {'filing_fee': 70, 'annual_report': 20, 'registered_agent': 50, 'total_first_year': 120, 'gov_website': 'https://www.sos.ca.gov/business-programs/business-entities'},
        'CO': {'filing_fee': 50, 'annual_report': 10, 'registered_agent': 50, 'total_first_year': 100, 'gov_website': 'https://www.coloradosos.gov/business/business-entities'},
        'CT': {'filing_fee': 120, 'annual_report': 80, 'registered_agent': 50, 'total_first_year': 170, 'gov_website': 'https://portal.ct.gov/sots'},
        'DE': {'filing_fee': 90, 'annual_report': 300, 'registered_agent': 50, 'total_first_year': 140, 'gov_website': 'https://corp.delaware.gov'},
        'FL': {'filing_fee': 125, 'annual_report': 138.75, 'registered_agent': 50, 'total_first_year': 175, 'gov_website': 'https://dos.myflorida.com/sunbiz'},
        'GA': {'filing_fee': 100, 'annual_report': 50, 'registered_agent': 50, 'total_first_year': 150, 'gov_website': 'https://sos.ga.gov/corporations'},
        'HI': {'filing_fee': 50, 'annual_report': 15, 'registered_agent': 50, 'total_first_year': 100, 'gov_website': 'https://cca.hawaii.gov/breg'},
        'ID': {'filing_fee': 100, 'annual_report': 0, 'registered_agent': 50, 'total_first_year': 150, 'gov_website': 'https://sos.idaho.gov/business'},
        'IL': {'filing_fee': 150, 'annual_report': 75, 'registered_agent': 50, 'total_first_year': 200, 'gov_website': 'https://www.ilsos.gov/businessservices'},
        'IN': {'filing_fee': 90, 'annual_report': 30, 'registered_agent': 50, 'total_first_year': 140, 'gov_website': 'https://www.in.gov/sos/business'},
        'IA': {'filing_fee': 50, 'annual_report': 60, 'registered_agent': 50, 'total_first_year': 100, 'gov_website': 'https://sos.iowa.gov/business'},
        'KS': {'filing_fee': 160, 'annual_report': 55, 'registered_agent': 50, 'total_first_year': 210, 'gov_website': 'https://www.kssos.org/business'},
        'KY': {'filing_fee': 40, 'annual_report': 15, 'registered_agent': 50, 'total_first_year': 90, 'gov_website': 'https://sos.ky.gov/business'},
        'LA': {'filing_fee': 100, 'annual_report': 30, 'registered_agent': 50, 'total_first_year': 150, 'gov_website': 'https://www.sos.la.gov/businessservices'},
        'ME': {'filing_fee': 175, 'annual_report': 85, 'registered_agent': 50, 'total_first_year': 225, 'gov_website': 'https://www.maine.gov/sos/cec/corp'},
        'MD': {'filing_fee': 100, 'annual_report': 300, 'registered_agent': 50, 'total_first_year': 150, 'gov_website': 'https://sos.maryland.gov/Pages/default.aspx'},
        'MA': {'filing_fee': 500, 'annual_report': 500, 'registered_agent': 50, 'total_first_year': 550, 'gov_website': 'https://www.sec.state.ma.us/cor'},
        'MI': {'filing_fee': 50, 'annual_report': 25, 'registered_agent': 50, 'total_first_year': 100, 'gov_website': 'https://www.michigan.gov/lara/bureau-list/csc'},
        'MN': {'filing_fee': 155, 'annual_report': 0, 'registered_agent': 50, 'total_first_year': 205, 'gov_website': 'https://www.sos.state.mn.us/business-liens'},
        'MS': {'filing_fee': 50, 'annual_report': 25, 'registered_agent': 50, 'total_first_year': 100, 'gov_website': 'https://www.sos.ms.gov/business-services'},
        'MO': {'filing_fee': 50, 'annual_report': 0, 'registered_agent': 50, 'total_first_year': 100, 'gov_website': 'https://www.sos.mo.gov/business'},
        'MT': {'filing_fee': 70, 'annual_report': 20, 'registered_agent': 50, 'total_first_year': 120, 'gov_website': 'https://sosmt.gov/business'},
        'NE': {'filing_fee': 105, 'annual_report': 13, 'registered_agent': 50, 'total_first_year': 155, 'gov_website': 'https://sos.nebraska.gov/business-services'},
        'NV': {'filing_fee': 75, 'annual_report': 150, 'registered_agent': 50, 'total_first_year': 125, 'gov_website': 'https://www.nvsos.gov/sos/business-services'},
        'NH': {'filing_fee': 100, 'annual_report': 100, 'registered_agent': 50, 'total_first_year': 150, 'gov_website': 'https://sos.nh.gov/business-services'},
        'NJ': {'filing_fee': 125, 'annual_report': 75, 'registered_agent': 50, 'total_first_year': 175, 'gov_website': 'https://www.nj.gov/state/business'},
        'NM': {'filing_fee': 50, 'annual_report': 0, 'registered_agent': 50, 'total_first_year': 100, 'gov_website': 'https://www.sos.state.nm.us/business-services'},
        'NY': {'filing_fee': 200, 'annual_report': 9, 'registered_agent': 50, 'total_first_year': 250, 'gov_website': 'https://dos.ny.gov/business-services'},
        'NC': {'filing_fee': 125, 'annual_report': 200, 'registered_agent': 50, 'total_first_year': 175, 'gov_website': 'https://www.sosnc.gov/business'},
        'ND': {'filing_fee': 135, 'annual_report': 25, 'registered_agent': 50, 'total_first_year': 185, 'gov_website': 'https://sos.nd.gov/business-services'},
        'OH': {'filing_fee': 99, 'annual_report': 0, 'registered_agent': 50, 'total_first_year': 149, 'gov_website': 'https://www.sos.state.oh.us/businesses'},
        'OK': {'filing_fee': 100, 'annual_report': 25, 'registered_agent': 50, 'total_first_year': 150, 'gov_website': 'https://www.sos.ok.gov/business'},
        'OR': {'filing_fee': 100, 'annual_report': 100, 'registered_agent': 50, 'total_first_year': 150, 'gov_website': 'https://sos.oregon.gov/business'},
        'PA': {'filing_fee': 125, 'annual_report': 70, 'registered_agent': 50, 'total_first_year': 175, 'gov_website': 'https://www.dos.pa.gov/businesschar'},
        'RI': {'filing_fee': 150, 'annual_report': 50, 'registered_agent': 50, 'total_first_year': 200, 'gov_website': 'https://sos.ri.gov/business'},
        'SC': {'filing_fee': 110, 'annual_report': 0, 'registered_agent': 50, 'total_first_year': 160, 'gov_website': 'https://www.scsos.com/business-services'},
        'SD': {'filing_fee': 150, 'annual_report': 50, 'registered_agent': 50, 'total_first_year': 200, 'gov_website': 'https://sdsos.gov/business-services'},
        'TN': {'filing_fee': 300, 'annual_report': 300, 'registered_agent': 50, 'total_first_year': 350, 'gov_website': 'https://sos.tn.gov/business-services'},
        'TX': {'filing_fee': 300, 'annual_report': 0, 'registered_agent': 50, 'total_first_year': 350, 'gov_website': 'https://www.sos.state.tx.us/corp'},
        'UT': {'filing_fee': 70, 'annual_report': 20, 'registered_agent': 50, 'total_first_year': 120, 'gov_website': 'https://corporations.utah.gov'},
        'VT': {'filing_fee': 125, 'annual_report': 35, 'registered_agent': 50, 'total_first_year': 175, 'gov_website': 'https://sos.vermont.gov/corporations'},
        'VA': {'filing_fee': 100, 'annual_report': 50, 'registered_agent': 50, 'total_first_year': 150, 'gov_website': 'https://www.scc.virginia.gov/clk/business.aspx'},
        'WA': {'filing_fee': 200, 'annual_report': 60, 'registered_agent': 50, 'total_first_year': 250, 'gov_website': 'https://www.sos.wa.gov/corps'},
        'WV': {'filing_fee': 100, 'annual_report': 25, 'registered_agent': 50, 'total_first_year': 150, 'gov_website': 'https://sos.wv.gov/business-licensing'},
        'WI': {'filing_fee': 130, 'annual_report': 25, 'registered_agent': 50, 'total_first_year': 180, 'gov_website': 'https://www.wdfi.org'},
        'WY': {'filing_fee': 100, 'annual_report': 50, 'registered_agent': 50, 'total_first_year': 150, 'gov_website': 'https://sos.wyo.gov/business-services'},
        'DC': {'filing_fee': 99, 'annual_report': 300, 'registered_agent': 50, 'total_first_year': 149, 'gov_website': 'https://corponline.dcra.dc.gov'}
    }

def get_top_3_llc_services():
    """Get top 3 LLC formation services with pricing and features"""
    return {
        'northwest_registered_agent': {
            'name': 'Northwest Registered Agent',
            'formation_cost': '$39 + state filing fee',
            'formation_includes': 'A fully-formed business, registered agent service, business address, business email, domain name, custom website, mail forwarding, Privacy by Default®, and Corporate Guide® Service',
            'renewal_cost': '$125/year',
            'renewal_note': 'Firm rate that never increases',
            'community_feedback': 'Rated 4.7/5 stars by 1645 clients on Google. Ridiculously good customer service. Services are very reasonably priced. They\'re so great.',
            'rating': 4.7,
            'reviews': 1645,
            'website': 'https://consumer-champion.org/LLCwebsite',
            'phone': '1-800-140-7189',
            'description': 'Northwest Registered Agent has been helping entrepreneurs form businesses since 1998. Their $39 formation service includes everything you need to get your business up and running, with exceptional customer service and a commitment to not being annoying. They provide comprehensive business formation services with privacy protection and ongoing support.',
            'popularity': 'Most Popular'
        },
        'incfile': {
            'name': 'Incfile (now Bizee)',
            'formation_cost': '$0 + state fee',
            'formation_includes': 'Free formation including one year of registered agent service, business formation documents, and compliance alerts',
            'renewal_cost': '$119/year',
            'renewal_note': 'After the first free year',
            'community_feedback': 'Often referred to as a "free formation" with solid basic services for new entrepreneurs',
            'rating': 4.6,
            'reviews': 1800,
            'website': 'https://www.incfile.com',
            'phone': '1-855-981-7200',
            'description': 'Incfile, now rebranded as Bizee, offers a completely free LLC formation service that covers all state filing fees. They provide essential business formation documents and compliance monitoring. While their free tier is basic, it\'s perfect for entrepreneurs who want to get started without upfront costs.',
            'popularity': 'Best Value'
        },
        'zenbusiness': {
            'name': 'ZenBusiness',
            'formation_packages': {
                'starter': {
                    'name': 'Starter',
                    'cost': '$0 + state fee',
                    'description': 'Entry-level formation only'
                },
                'pro': {
                    'name': 'Pro',
                    'cost': '$199 + state fee',
                    'description': 'Includes EIN, operating agreement, "Worry‑Free Compliance," and expedited filing'
                },
                'premium': {
                    'name': 'Premium',
                    'cost': '$299 + state fee',
                    'description': 'Adds website, domain, email, documents, plus Pro features'
                }
            },
            'renewal_cost': '$199/year',
            'renewal_note': 'If included, auto-renews at $199/year. Standalone registered agent service also starts at $199/year',
            'community_feedback': 'Comprehensive packages with worry-free compliance and excellent customer support',
            'rating': 4.7,
            'reviews': 2200,
            'website': 'https://www.zenbusiness.com',
            'phone': '1-844-493-6249',
            'description': 'ZenBusiness offers three comprehensive formation packages designed to grow with your business. Their "Worry-Free Compliance" service automatically handles annual reports and other compliance requirements. They focus on helping small businesses succeed with ongoing support and educational resources.',
            'popularity': 'Most Comprehensive'
        }
    }

def get_category_info():
    """Get category information for all LLC service types"""
    return {
        'doctors': {
            'title': 'LLC Registration Services for Doctors',
            'description': 'Professional LLC formation and business services specifically for medical professionals and healthcare practices.'
        },
        'rental-properties': {
            'title': 'LLC Registration Services for Rental Properties',
            'description': 'LLC formation and property management services for real estate investors and landlords.'
        },
        'vending-machines': {
            'title': 'LLC Registration Services for Vending Machines',
            'description': 'LLC formation and business services for vending machine operators and automated retail businesses.'
        },
        'realtors': {
            'title': 'LLC Registration Services for Realtors',
            'description': 'LLC formation and business services for real estate agents, brokers, and real estate professionals.'
        },
        'small-business': {
            'title': 'LLC Registration Services for Small Business',
            'description': 'LLC formation and comprehensive business services for small business owners and entrepreneurs.'
        },
        'airbnb': {
            'title': 'LLC Registration Services for Airbnb',
            'description': 'LLC formation and business services for Airbnb hosts, vacation rental owners, and short-term rental businesses.'
        },
        'trucking': {
            'title': 'LLC Registration Services for Trucking',
            'description': 'LLC formation and business services for trucking companies, transportation businesses, and logistics operations.'
        },
        'cannabis': {
            'title': 'LLC Registration Services for Cannabis',
            'description': 'LLC formation and specialized business services for cannabis dispensaries, marijuana businesses, and cannabis-related operations.'
        },
        'hair-salon': {
            'title': 'LLC Registration Services for Hair Salon',
            'description': 'LLC formation and business services for hair salons, beauty salons, and cosmetology businesses.'
        },
        'etsy': {
            'title': 'LLC Registration Services for Etsy',
            'description': 'LLC formation and business services for Etsy sellers, online craft businesses, and ecommerce entrepreneurs.'
        },
        'amazon-fba': {
            'title': 'LLC Registration Services for Amazon FBA',
            'description': 'LLC formation and business services for Amazon FBA sellers, fulfillment businesses, and ecommerce operations.'
        },
        'bakery': {
            'title': 'LLC Registration Services for Bakery',
            'description': 'LLC formation and business services for bakeries, food service businesses, and culinary entrepreneurs.'
        },
        'investment-property': {
            'title': 'LLC Registration Services for Investment Property',
            'description': 'LLC formation and business services for real estate investors, property management companies, and investment portfolios.'
        },
        'clothing-brand': {
            'title': 'LLC Registration Services for Clothing Brand',
            'description': 'LLC formation and business services for clothing brands, fashion businesses, and apparel companies.'
        },
        'dropshipping': {
            'title': 'LLC Registration Services for Dropshipping',
            'description': 'LLC formation and business services for dropshipping businesses, ecommerce entrepreneurs, and online retailers.'
        },
        'contractor': {
            'title': 'LLC Registration Services for Contractor',
            'description': 'LLC formation and business services for contractors, construction companies, and home improvement businesses.'
        },
        'roofers': {
            'title': 'LLC Registration Services for Roofers',
            'description': 'LLC formation and business services for roofing companies, construction contractors, and home improvement specialists.'
        },
        'ecommerce': {
            'title': 'LLC Registration Services for Ecommerce',
            'description': 'LLC formation and business services for ecommerce businesses, online retailers, and digital commerce operations.'
        },
        'photographer': {
            'title': 'LLC Registration Services for Photographer',
            'description': 'LLC formation and business services for photographers, photography studios, and creative professionals.'
        },
        'shopify': {
            'title': 'LLC Registration Services for Shopify',
            'description': 'LLC formation and business services for Shopify store owners, ecommerce entrepreneurs, and online retailers.'
        },
        'handyman': {
            'title': 'LLC Registration Services for Handyman',
            'description': 'LLC formation and business services for handyman services, home repair businesses, and maintenance contractors.'
        },
        'uber': {
            'title': 'LLC Registration Services for Uber',
            'description': 'LLC formation and business services for Uber drivers, ride-sharing entrepreneurs, and transportation businesses.'
        },
        'lyft': {
            'title': 'LLC Registration Services for Lyft',
            'description': 'LLC formation and business services for Lyft drivers, ride-sharing entrepreneurs, and transportation businesses.'
        },
        'limo': {
            'title': 'LLC Registration Services for Limo',
            'description': 'LLC formation and business services for limousine companies, luxury transportation services, and chauffeur businesses.'
        },
        'handymen': {
            'title': 'LLC Registration Services for Handymen',
            'description': 'LLC formation and business services for handymen services, home repair businesses, and maintenance contractors.'
        },
        'electricians': {
            'title': 'LLC Registration Services for Electricians',
            'description': 'LLC formation and business services for electricians, electrical contractors, and electrical service businesses.'
        },
        'plumbers': {
            'title': 'LLC Registration Services for Plumbers',
            'description': 'LLC formation and business services for plumbers, plumbing contractors, and plumbing service businesses.'
        },
        'landscapers': {
            'title': 'LLC Registration Services for Landscapers',
            'description': 'LLC formation and business services for landscapers, landscaping companies, and outdoor service businesses.'
        },
        'cleaning-businesses': {
            'title': 'LLC Registration Services for Cleaning Businesses',
            'description': 'LLC formation and business services for cleaning companies, janitorial services, and maintenance businesses.'
        },
        'painters': {
            'title': 'LLC Registration Services for Painters',
            'description': 'LLC formation and business services for painters, painting contractors, and residential/commercial painting businesses.'
        },
        'hvac-technicians': {
            'title': 'LLC Registration Services for HVAC Technicians',
            'description': 'LLC formation and business services for HVAC technicians, heating and cooling contractors, and climate control businesses.'
        },
        'dentists': {
            'title': 'LLC Registration Services for Dentists',
            'description': 'LLC formation and business services for dentists, dental practices, and oral healthcare professionals.'
        },
        'chiropractors': {
            'title': 'LLC Registration Services for Chiropractors',
            'description': 'LLC formation and business services for chiropractors, chiropractic clinics, and spinal health professionals.'
        },
        'therapists': {
            'title': 'LLC Registration Services for Therapists',
            'description': 'LLC formation and business services for therapists, counseling practices, and mental health professionals.'
        },
        'nutritionists': {
            'title': 'LLC Registration Services for Nutritionists',
            'description': 'LLC formation and business services for nutritionists, dietitians, and nutritional consulting businesses.'
        },
        'personal-trainers': {
            'title': 'LLC Registration Services for Personal Trainers',
            'description': 'LLC formation and business services for personal trainers, fitness coaches, and wellness professionals.'
        },
        'landlords': {
            'title': 'LLC Registration Services for Landlords',
            'description': 'LLC formation and business services for landlords, property owners, and rental property management.'
        },
        'airbnb-hosts': {
            'title': 'LLC Registration Services for Airbnb Hosts',
            'description': 'LLC formation and business services for Airbnb hosts, vacation rental owners, and short-term rental businesses.'
        },
        'real-estate-agents': {
            'title': 'LLC Registration Services for Real Estate Agents',
            'description': 'LLC formation and business services for real estate agents, brokers, and real estate professionals.'
        },
        'property-management': {
            'title': 'LLC Registration Services for Property Management',
            'description': 'LLC formation and business services for property management companies, real estate management, and rental services.'
        },
        'house-flippers': {
            'title': 'LLC Registration Services for House Flippers',
            'description': 'LLC formation and business services for house flippers, real estate investors, and property renovation businesses.'
        },
        'e-commerce': {
            'title': 'LLC Registration Services for E-commerce',
            'description': 'LLC formation and business services for e-commerce businesses, online retailers, and digital commerce operations.'
        },
        'freelancers': {
            'title': 'LLC Registration Services for Freelancers',
            'description': 'LLC formation and business services for freelancers, independent contractors, and self-employed professionals.'
        },
        'consultants': {
            'title': 'LLC Registration Services for Consultants',
            'description': 'LLC formation and business services for consultants, consulting firms, and professional advisory businesses.'
        },
        'social-media-influencers': {
            'title': 'LLC Registration Services for Social Media Influencers',
            'description': 'LLC formation and business services for social media influencers, content creators, and digital marketing professionals.'
        },
        'online-coaches': {
            'title': 'LLC Registration Services for Online Coaches',
            'description': 'LLC formation and business services for online coaches, life coaches, and professional development consultants.'
        },
        'content-creators': {
            'title': 'LLC Registration Services for Content Creators',
            'description': 'LLC formation and business services for content creators, digital media professionals, and creative entrepreneurs.'
        },
        'stock-trading': {
            'title': 'LLC Registration Services for Stock Trading',
            'description': 'LLC formation and business services for stock traders, investment professionals, and securities trading businesses.'
        },
        'day-trading': {
            'title': 'LLC Registration Services for Day Trading',
            'description': 'LLC formation and business services for day traders, active traders, and short-term investment businesses.'
        },
        'crypto-trading': {
            'title': 'LLC Registration Services for Crypto Trading',
            'description': 'LLC formation and business services for cryptocurrency traders, blockchain businesses, and digital asset trading.'
        },
        'financial-advisors': {
            'title': 'LLC Registration Services for Financial Advisors',
            'description': 'LLC formation and business services for financial advisors, wealth managers, and investment consultants.'
        },
        'rideshare-drivers': {
            'title': 'LLC Registration Services for Rideshare Drivers',
            'description': 'LLC formation and business services for rideshare drivers, transportation entrepreneurs, and mobility service providers.'
        },
        'restaurants': {
            'title': 'LLC Registration Services for Restaurants',
            'description': 'LLC formation and business services for restaurants, food service businesses, and culinary establishments.'
        },
        'food-trucks': {
            'title': 'LLC Registration Services for Food Trucks',
            'description': 'LLC formation and business services for food trucks, mobile food vendors, and street food businesses.'
        },
        'salons': {
            'title': 'LLC Registration Services for Salons',
            'description': 'LLC formation and business services for salons, beauty businesses, and cosmetology establishments.'
        },
        'barbers': {
            'title': 'LLC Registration Services for Barbers',
            'description': 'LLC formation and business services for barbers, barbershops, and men\'s grooming businesses.'
        },
        'event-planners': {
            'title': 'LLC Registration Services for Event Planners',
            'description': 'LLC formation and business services for event planners, wedding coordinators, and special event management.'
        },
        'drywall-installers': {
            'title': 'LLC Registration Services for Drywall Installers',
            'description': 'LLC formation and business services for drywall installers, construction contractors, and interior finishing specialists.'
        },
        'window-installers': {
            'title': 'LLC Registration Services for Window Installers',
            'description': 'LLC formation and business services for window installers, glazing contractors, and home improvement specialists.'
        },
        'insulation-companies': {
            'title': 'LLC Registration Services for Insulation Companies',
            'description': 'LLC formation and business services for insulation companies, energy efficiency contractors, and building envelope specialists.'
        },
        'solar-panel-installers': {
            'title': 'LLC Registration Services for Solar Panel Installers',
            'description': 'LLC formation and business services for solar panel installers, renewable energy contractors, and green technology specialists.'
        },
        'fencing-companies': {
            'title': 'LLC Registration Services for Fencing Companies',
            'description': 'LLC formation and business services for fencing companies, outdoor construction contractors, and property enclosure specialists.'
        },
        'videographers': {
            'title': 'LLC Registration Services for Videographers',
            'description': 'LLC formation and business services for videographers, video production companies, and multimedia professionals.'
        },
        'podcasters': {
            'title': 'LLC Registration Services for Podcasters',
            'description': 'LLC formation and business services for podcasters, audio content creators, and digital media entrepreneurs.'
        },
        'marketing-agencies': {
            'title': 'LLC Registration Services for Marketing Agencies',
            'description': 'LLC formation and business services for marketing agencies, advertising firms, and brand management companies.'
        },
        'seo-consultants': {
            'title': 'LLC Registration Services for SEO Consultants',
            'description': 'LLC formation and business services for SEO consultants, digital marketing specialists, and search engine optimization experts.'
        },
        'pr-firms': {
            'title': 'LLC Registration Services for PR Firms',
            'description': 'LLC formation and business services for PR firms, public relations agencies, and communications consultants.'
        },
        'it-consultants': {
            'title': 'LLC Registration Services for IT Consultants',
            'description': 'LLC formation and business services for IT consultants, technology advisors, and information systems specialists.'
        },
        'software-developers': {
            'title': 'LLC Registration Services for Software Developers',
            'description': 'LLC formation and business services for software developers, programming consultants, and technology entrepreneurs.'
        },
        'cybersecurity-firms': {
            'title': 'LLC Registration Services for Cybersecurity Firms',
            'description': 'LLC formation and business services for cybersecurity firms, information security consultants, and digital protection specialists.'
        },
        'msps': {
            'title': 'LLC Registration Services for MSPs',
            'description': 'LLC formation and business services for managed service providers, IT support companies, and technology management firms.'
        },
        'saas-businesses': {
            'title': 'LLC Registration Services for SaaS Businesses',
            'description': 'LLC formation and business services for SaaS businesses, software-as-a-service companies, and subscription-based technology firms.'
        },
        'woodworking-businesses': {
            'title': 'LLC Registration Services for Woodworking Businesses',
            'description': 'LLC formation and business services for woodworking businesses, custom furniture makers, and artisanal craftsmen.'
        },
        'jewelry-makers': {
            'title': 'LLC Registration Services for Jewelry Makers',
            'description': 'LLC formation and business services for jewelry makers, custom jewelry designers, and precious metal artisans.'
        },
        'candle-makers': {
            'title': 'LLC Registration Services for Candle Makers',
            'description': 'LLC formation and business services for candle makers, artisanal product manufacturers, and home goods entrepreneurs.'
        },
        'soap-makers': {
            'title': 'LLC Registration Services for Soap Makers',
            'description': 'LLC formation and business services for soap makers, natural product manufacturers, and personal care artisans.'
        },
        'farmers': {
            'title': 'LLC Registration Services for Farmers',
            'description': 'LLC formation and business services for farmers, agricultural businesses, and crop production operations.'
        },
        'ranchers': {
            'title': 'LLC Registration Services for Ranchers',
            'description': 'LLC formation and business services for ranchers, livestock operations, and animal husbandry businesses.'
        },
        'beekeepers': {
            'title': 'LLC Registration Services for Beekeepers',
            'description': 'LLC formation and business services for beekeepers, honey producers, and apiary management businesses.'
        },
        'greenhouse-businesses': {
            'title': 'LLC Registration Services for Greenhouse Businesses',
            'description': 'LLC formation and business services for greenhouse businesses, controlled environment agriculture, and specialty crop production.'
        },
        'landscaping-supply-companies': {
            'title': 'LLC Registration Services for Landscaping Supply Companies',
            'description': 'LLC formation and business services for landscaping supply companies, garden centers, and outdoor material suppliers.'
        },
        'driving-schools': {
            'title': 'LLC Registration Services for Driving Schools',
            'description': 'LLC formation and business services for driving schools, driver education programs, and transportation training businesses.'
        },
        'test-prep-tutors': {
            'title': 'LLC Registration Services for Test Prep Tutors',
            'description': 'LLC formation and business services for test prep tutors, educational consultants, and academic preparation specialists.'
        },
        'language-instructors': {
            'title': 'LLC Registration Services for Language Instructors',
            'description': 'LLC formation and business services for language instructors, foreign language teachers, and linguistic education specialists.'
        },
        'career-coaches': {
            'title': 'LLC Registration Services for Career Coaches',
            'description': 'LLC formation and business services for career coaches, professional development consultants, and job search specialists.'
        },
        'corporate-trainers': {
            'title': 'LLC Registration Services for Corporate Trainers',
            'description': 'LLC formation and business services for corporate trainers, workplace education specialists, and professional development consultants.'
        },
        'charter-bus-companies': {
            'title': 'LLC Registration Services for Charter Bus Companies',
            'description': 'LLC formation and business services for charter bus companies, group transportation services, and passenger transport businesses.'
        },
        'boat-rental-businesses': {
            'title': 'LLC Registration Services for Boat Rental Businesses',
            'description': 'LLC formation and business services for boat rental businesses, marine recreation services, and watercraft rental operations.'
        },
        'trucking-dispatchers': {
            'title': 'LLC Registration Services for Trucking Dispatchers',
            'description': 'LLC formation and business services for trucking dispatchers, logistics coordinators, and transportation management specialists.'
        },
        'tour-guides': {
            'title': 'LLC Registration Services for Tour Guides',
            'description': 'LLC formation and business services for tour guides, travel services, and tourism experience providers.'
        },
        'llc-registration': {
            'title': 'LLC Registration Services',
            'description': 'Complete LLC formation and business registration services for all business types.'
        },
        'llc-services': {
            'title': 'LLC Services',
            'description': 'Comprehensive LLC services including formation, compliance, and ongoing support.'
        }
    }

def get_businesses_by_location(state=None, city=None, limit=50):
    """Get businesses filtered by state and/or city"""
    filtered_data = data.copy()
    
    if state:
        filtered_data = filtered_data[filtered_data['state'] == state]
    if city:
        filtered_data = filtered_data[filtered_data['city'] == city]
    
    # Sort by rating (descending) and number of reviews
    filtered_data = filtered_data.sort_values(['rating', 'reviews'], ascending=[False, False])
    
    return filtered_data.head(limit).to_dict('records')

def get_businesses_by_category(category, state=None, city=None, limit=50, use_fallback=True):
    """Get businesses by category (use case)"""
    filtered_data = data.copy()
    
    # Define category mappings for LLC registration services
    category_mappings = {
        'doctors': ['certified public accountant', 'accountant', 'tax preparation', 'business management consultant', 'financial consultant', 'medical', 'healthcare', 'doctor', 'physician'],
        'rental-properties': ['real estate', 'property management', 'business management consultant', 'accountant', 'tax preparation', 'rental', 'landlord'],
        'vending-machines': ['vending machine', 'vending', 'automated retail', 'business management consultant', 'accountant', 'tax preparation'],
        'realtors': ['real estate', 'real estate agent', 'real estate broker', 'property management', 'business management consultant', 'accountant', 'tax preparation'],
        'small-business': ['small business', 'business management consultant', 'accountant', 'tax preparation', 'financial consultant', 'legal services'],
        'airbnb': ['real estate', 'property management', 'vacation rental', 'business management consultant', 'accountant', 'tax preparation', 'airbnb', 'short term rental'],
        'trucking': ['trucking', 'transportation', 'logistics', 'business management consultant', 'accountant', 'tax preparation'],
        'cannabis': ['cannabis', 'marijuana', 'dispensary', 'business management consultant', 'legal services', 'accountant', 'tax preparation'],
        'hair-salon': ['hair salon', 'beauty salon', 'cosmetology', 'business management consultant', 'accountant', 'tax preparation'],
        'etsy': ['etsy', 'ecommerce', 'online retail', 'business management consultant', 'accountant', 'tax preparation'],
        'amazon-fba': ['amazon fba', 'fulfillment by amazon', 'ecommerce', 'online retail', 'business management consultant', 'accountant', 'tax preparation'],
        'bakery': ['bakery', 'food service', 'restaurant', 'business management consultant', 'accountant', 'tax preparation'],
        'investment-property': ['real estate', 'property management', 'investment', 'business management consultant', 'accountant', 'tax preparation'],
        'clothing-brand': ['clothing', 'fashion', 'apparel', 'business management consultant', 'accountant', 'tax preparation'],
        'dropshipping': ['dropshipping', 'ecommerce', 'online retail', 'business management consultant', 'accountant', 'tax preparation'],
        'contractor': ['contractor', 'construction', 'home improvement', 'business management consultant', 'accountant', 'tax preparation'],
        'roofers': ['roofer', 'roofing', 'construction', 'business management consultant', 'accountant', 'tax preparation'],
        'ecommerce': ['ecommerce', 'online retail', 'business management consultant', 'accountant', 'tax preparation'],
        'photographer': ['photographer', 'photography', 'business management consultant', 'accountant', 'tax preparation'],
        'shopify': ['shopify', 'ecommerce', 'online retail', 'business management consultant', 'accountant', 'tax preparation'],
        'handyman': ['handyman', 'home repair', 'maintenance', 'business management consultant', 'accountant', 'tax preparation'],
        'uber': ['uber', 'ride sharing', 'transportation', 'business management consultant', 'accountant', 'tax preparation'],
        'lyft': ['lyft', 'ride sharing', 'transportation', 'business management consultant', 'accountant', 'tax preparation'],
        'limo': ['limo', 'limousine', 'transportation', 'business management consultant', 'accountant', 'tax preparation'],
        'handymen': ['handymen', 'home repair', 'maintenance', 'business management consultant', 'accountant', 'tax preparation'],
        'electricians': ['electrician', 'electrical', 'business management consultant', 'accountant', 'tax preparation'],
        'plumbers': ['plumber', 'plumbing', 'business management consultant', 'accountant', 'tax preparation'],
        'landscapers': ['landscaper', 'landscaping', 'business management consultant', 'accountant', 'tax preparation'],
        'cleaning-businesses': ['cleaning', 'janitorial', 'business management consultant', 'accountant', 'tax preparation'],
        'painters': ['painter', 'painting', 'business management consultant', 'accountant', 'tax preparation'],
        'hvac-technicians': ['hvac', 'heating', 'cooling', 'business management consultant', 'accountant', 'tax preparation'],
        'dentists': ['dentist', 'dental', 'business management consultant', 'accountant', 'tax preparation'],
        'chiropractors': ['chiropractor', 'chiropractic', 'business management consultant', 'accountant', 'tax preparation'],
        'therapists': ['therapist', 'therapy', 'counseling', 'business management consultant', 'accountant', 'tax preparation'],
        'nutritionists': ['nutritionist', 'nutrition', 'dietitian', 'business management consultant', 'accountant', 'tax preparation'],
        'personal-trainers': ['personal trainer', 'fitness', 'business management consultant', 'accountant', 'tax preparation'],
        'landlords': ['landlord', 'property management', 'business management consultant', 'accountant', 'tax preparation'],
        'airbnb-hosts': ['airbnb', 'vacation rental', 'business management consultant', 'accountant', 'tax preparation'],
        'real-estate-agents': ['real estate agent', 'real estate broker', 'business management consultant', 'accountant', 'tax preparation'],
        'property-management': ['property management', 'business management consultant', 'accountant', 'tax preparation'],
        'house-flippers': ['house flipper', 'real estate investment', 'business management consultant', 'accountant', 'tax preparation'],
        'e-commerce': ['ecommerce', 'online retail', 'business management consultant', 'accountant', 'tax preparation'],
        'freelancers': ['freelancer', 'independent contractor', 'business management consultant', 'accountant', 'tax preparation'],
        'consultants': ['consultant', 'consulting', 'business management consultant', 'accountant', 'tax preparation'],
        'social-media-influencers': ['social media', 'influencer', 'business management consultant', 'accountant', 'tax preparation'],
        'online-coaches': ['coach', 'coaching', 'business management consultant', 'accountant', 'tax preparation'],
        'content-creators': ['content creator', 'digital media', 'business management consultant', 'accountant', 'tax preparation'],
        'stock-trading': ['stock trading', 'investment', 'business management consultant', 'accountant', 'tax preparation'],
        'day-trading': ['day trading', 'investment', 'business management consultant', 'accountant', 'tax preparation'],
        'crypto-trading': ['crypto', 'cryptocurrency', 'business management consultant', 'accountant', 'tax preparation'],
        'financial-advisors': ['financial advisor', 'financial consultant', 'business management consultant', 'accountant', 'tax preparation'],
        'rideshare-drivers': ['rideshare', 'transportation', 'business management consultant', 'accountant', 'tax preparation'],
        'restaurants': ['restaurant', 'food service', 'business management consultant', 'accountant', 'tax preparation'],
        'food-trucks': ['food truck', 'mobile food', 'business management consultant', 'accountant', 'tax preparation'],
        'salons': ['salon', 'beauty salon', 'business management consultant', 'accountant', 'tax preparation'],
        'barbers': ['barber', 'barbershop', 'business management consultant', 'accountant', 'tax preparation'],
        'event-planners': ['event planner', 'event planning', 'business management consultant', 'accountant', 'tax preparation'],
        'drywall-installers': ['drywall', 'construction', 'interior finishing', 'business management consultant', 'accountant', 'tax preparation'],
        'window-installers': ['window', 'glazing', 'construction', 'business management consultant', 'accountant', 'tax preparation'],
        'insulation-companies': ['insulation', 'energy efficiency', 'construction', 'business management consultant', 'accountant', 'tax preparation'],
        'solar-panel-installers': ['solar', 'renewable energy', 'green technology', 'business management consultant', 'accountant', 'tax preparation'],
        'fencing-companies': ['fencing', 'outdoor construction', 'business management consultant', 'accountant', 'tax preparation'],
        'videographers': ['videographer', 'video production', 'multimedia', 'business management consultant', 'accountant', 'tax preparation'],
        'podcasters': ['podcaster', 'audio content', 'digital media', 'business management consultant', 'accountant', 'tax preparation'],
        'marketing-agencies': ['marketing agency', 'advertising', 'brand management', 'business management consultant', 'accountant', 'tax preparation'],
        'seo-consultants': ['seo', 'digital marketing', 'search engine optimization', 'business management consultant', 'accountant', 'tax preparation'],
        'pr-firms': ['pr firm', 'public relations', 'communications', 'business management consultant', 'accountant', 'tax preparation'],
        'it-consultants': ['it consultant', 'technology advisor', 'information systems', 'business management consultant', 'accountant', 'tax preparation'],
        'software-developers': ['software developer', 'programming', 'technology', 'business management consultant', 'accountant', 'tax preparation'],
        'cybersecurity-firms': ['cybersecurity', 'information security', 'digital protection', 'business management consultant', 'accountant', 'tax preparation'],
        'msps': ['msp', 'managed service provider', 'it support', 'business management consultant', 'accountant', 'tax preparation'],
        'saas-businesses': ['saas', 'software-as-a-service', 'subscription technology', 'business management consultant', 'accountant', 'tax preparation'],
        'woodworking-businesses': ['woodworking', 'custom furniture', 'artisanal crafts', 'business management consultant', 'accountant', 'tax preparation'],
        'jewelry-makers': ['jewelry maker', 'custom jewelry', 'precious metals', 'business management consultant', 'accountant', 'tax preparation'],
        'candle-makers': ['candle maker', 'artisanal products', 'home goods', 'business management consultant', 'accountant', 'tax preparation'],
        'soap-makers': ['soap maker', 'natural products', 'personal care', 'business management consultant', 'accountant', 'tax preparation'],
        'farmers': ['farmer', 'agriculture', 'crop production', 'business management consultant', 'accountant', 'tax preparation'],
        'ranchers': ['rancher', 'livestock', 'animal husbandry', 'business management consultant', 'accountant', 'tax preparation'],
        'beekeepers': ['beekeeper', 'honey production', 'apiary', 'business management consultant', 'accountant', 'tax preparation'],
        'greenhouse-businesses': ['greenhouse', 'controlled environment agriculture', 'specialty crops', 'business management consultant', 'accountant', 'tax preparation'],
        'landscaping-supply-companies': ['landscaping supply', 'garden center', 'outdoor materials', 'business management consultant', 'accountant', 'tax preparation'],
        'driving-schools': ['driving school', 'driver education', 'transportation training', 'business management consultant', 'accountant', 'tax preparation'],
        'test-prep-tutors': ['test prep', 'educational consultant', 'academic preparation', 'business management consultant', 'accountant', 'tax preparation'],
        'language-instructors': ['language instructor', 'foreign language', 'linguistic education', 'business management consultant', 'accountant', 'tax preparation'],
        'career-coaches': ['career coach', 'professional development', 'job search', 'business management consultant', 'accountant', 'tax preparation'],
        'corporate-trainers': ['corporate trainer', 'workplace education', 'professional development', 'business management consultant', 'accountant', 'tax preparation'],
        'charter-bus-companies': ['charter bus', 'group transportation', 'passenger transport', 'business management consultant', 'accountant', 'tax preparation'],
        'boat-rental-businesses': ['boat rental', 'marine recreation', 'watercraft rental', 'business management consultant', 'accountant', 'tax preparation'],
        'trucking-dispatchers': ['trucking dispatcher', 'logistics coordinator', 'transportation management', 'business management consultant', 'accountant', 'tax preparation'],
        'tour-guides': ['tour guide', 'travel services', 'tourism', 'business management consultant', 'accountant', 'tax preparation'],
        'llc-registration': ['certified public accountant', 'accountant', 'business management consultant', 'legal services', 'tax preparation'],
        'llc-services': ['certified public accountant', 'accountant', 'business management consultant', 'legal services', 'tax preparation']
    }
    
    # Filter by category (case insensitive)
    if category in category_mappings:
        search_terms = category_mappings[category]
        # Create a more comprehensive search mask
        mask = (
            filtered_data['category'].str.contains('|'.join(search_terms), case=False, na=False) |
            filtered_data['type'].str.contains('|'.join(search_terms), case=False, na=False) |
            filtered_data['name'].str.contains('|'.join(search_terms), case=False, na=False)
        )
        filtered_data = filtered_data[mask]
    elif category:
        # Fallback search for categories not in mappings
        search_term = category.replace('-', ' ').replace('_', ' ')
        mask = (
            filtered_data['category'].str.contains(search_term, case=False, na=False) |
            filtered_data['type'].str.contains(search_term, case=False, na=False) |
            filtered_data['name'].str.contains(search_term, case=False, na=False)
        )
        filtered_data = filtered_data[mask]
    
    if state:
        filtered_data = filtered_data[filtered_data['state'] == state]
    if city:
        filtered_data = filtered_data[filtered_data['city'] == city]
    
    # Sort by rating
    filtered_data = filtered_data.sort_values(['rating', 'reviews'], ascending=[False, False])
    
    # If no results found, try to show general business services
    if len(filtered_data) == 0 and use_fallback and category != 'llc-registration' and category != 'llc-services':
        print(f"No specific results for {category}, showing general business services")
        # Reset and show general business services
        filtered_data = data.copy()
        if state:
            filtered_data = filtered_data[filtered_data['state'] == state]
        if city:
            filtered_data = filtered_data[filtered_data['city'] == city]
        
        # Filter for general business services
        general_terms = ['business management consultant', 'accountant', 'tax preparation', 'legal services', 'financial consultant']
        mask = (
            filtered_data['category'].str.contains('|'.join(general_terms), case=False, na=False) |
            filtered_data['type'].str.contains('|'.join(general_terms), case=False, na=False)
        )
        filtered_data = filtered_data[mask]
        filtered_data = filtered_data.sort_values(['rating', 'reviews'], ascending=[False, False])
    
    return filtered_data.head(limit).to_dict('records')

@app.route('/')
def home():
    """Home page with overview"""
    total_businesses = len(data)
    states = get_unique_states()
    top_rated = data.nlargest(10, 'rating')[['name', 'city', 'state', 'rating', 'reviews']].to_dict('records')
    
    return render_template('home.html', 
                         total_businesses=total_businesses,
                         states=states,
                         states_count=51,  # 50 states + DC
                         top_rated=top_rated,
                         get_state_full_name=get_state_full_name)

@app.route('/about/')
def about():
    """About Us page"""
    total_businesses = len(data)
    
    return render_template('about.html', 
                         total_businesses=total_businesses)

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
    """Use-case hub page"""
    businesses = get_businesses_by_category(category, limit=100)
    states = get_unique_states()
    category_info = get_category_info()
    top_llc_services = get_top_3_llc_services()
    
    return render_template('use_case_hub.html',
                         category=category,
                         businesses=businesses,
                         states=states,
                         category_info=category_info.get(category, {}),
                         top_llc_services=top_llc_services,
                         get_state_full_name=get_state_full_name)

@app.route('/use-cases/<category>/<state>/')
def use_case_state(category, state):
    """Use-case × State page"""
    businesses = get_businesses_by_category(category, state=state, limit=500)
    state_full_name = get_state_full_name(state)
    category_info = get_category_info()
    top_llc_services = get_top_3_llc_services()
    state_costs = get_state_llc_costs().get(state.upper(), {
        'filing_fee': 100, 'annual_report': 50, 'registered_agent': 50, 
        'total_first_year': 150, 'gov_website': 'https://www.sos.gov'
    })
    
    # Check if we're showing fallback results
    original_search = get_businesses_by_category(category, state=state, limit=500, use_fallback=False)
    showing_fallback = len(original_search) == 0 and len(businesses) > 0
    
    # Debug: Print some info about the data
    print(f"Category: {category}, State: {state}")
    print(f"Found {len(businesses)} businesses")
    if businesses:
        print(f"Sample business: {businesses[0]}")
    if showing_fallback:
        print(f"Showing fallback results for {category}")
    
    return render_template('use_case_state.html',
                         category=category,
                         state=state,
                         state_full_name=state_full_name,
                         businesses=businesses,
                         category_info=category_info.get(category, {}),
                         top_llc_services=top_llc_services,
                         state_costs=state_costs,
                         showing_fallback=showing_fallback,
                         get_state_full_name=get_state_full_name)



@app.route('/best/<category>-services-for-<use_case>/')
def best_for_use_case(category, use_case):
    """Best for X lists page"""
    businesses = get_businesses_by_category(use_case, limit=50)
    
    return render_template('best_for_use_case.html',
                         category=category,
                         use_case=use_case,
                         businesses=businesses)

@app.route('/cost/<state>-<category>/')
def cost_guide(state, category):
    """Cost & Guides page"""
    businesses = get_businesses_by_category(category, state=state, limit=50)
    
    return render_template('cost_guide.html',
                         state=state,
                         category=category,
                         businesses=businesses)

@app.route('/tools/<tool_name>/')
def tools_calculators(tool_name):
    """Tools/Calculators page"""
    return render_template('tools.html', tool_name=tool_name)

@app.route('/api/businesses')
def api_businesses():
    """API endpoint for businesses"""
    state = request.args.get('state')
    city = request.args.get('city')
    category = request.args.get('category')
    limit = int(request.args.get('limit', 50))
    
    if category:
        businesses = get_businesses_by_category(category, state=state, city=city, limit=limit)
    else:
        businesses = get_businesses_by_location(state=state, city=city, limit=limit)
    
    return jsonify(businesses)

@app.route('/api/states')
def api_states():
    """API endpoint for states"""
    return jsonify(get_unique_states())



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
