#!/usr/bin/env python3
"""
CSV Optimization Script for Vercel Deployment
This script processes the large CSV file and creates an optimized version
"""

import pandas as pd
import os

def optimize_csv():
    """Optimize the CSV file for Vercel deployment"""
    try:
        # Load the original CSV
        print("Loading original CSV file...")
        df = pd.read_csv('LLC Data.csv', low_memory=False)
        print(f"Original CSV: {len(df)} rows, {len(df.columns)} columns")
        
        # Clean the data
        print("Cleaning data...")
        df = df.dropna(subset=['name', 'city', 'state'])
        
        # Convert ratings to numeric
        if 'rating' in df.columns:
            df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
            df = df[df['rating'] > 0]  # Only businesses with ratings
        
        # Clean text fields
        df['city'] = df['city'].str.strip()
        df['state'] = df['state'].str.strip()
        df['name'] = df['name'].str.strip()
        
        # Select only essential columns
        essential_columns = ['name', 'city', 'state', 'rating', 'reviews', 'phone', 'full_address', 'site', 'category', 'type']
        available_columns = [col for col in essential_columns if col in df.columns]
        
        df_optimized = df[available_columns].copy()
        
        # Remove duplicates
        df_optimized = df_optimized.drop_duplicates()
        
        # Limit to top 1000 businesses by rating
        if 'rating' in df_optimized.columns:
            df_optimized = df_optimized.sort_values('rating', ascending=False).head(1000)
        
        print(f"Optimized CSV: {len(df_optimized)} rows, {len(df_optimized.columns)} columns")
        
        # Save optimized version
        df_optimized.to_csv('LLC_Data_Optimized.csv', index=False)
        print("Saved optimized CSV as 'LLC_Data_Optimized.csv'")
        
        # Also save as JSON for easier loading
        df_optimized.to_json('LLC_Data_Optimized.json', orient='records')
        print("Saved optimized data as 'LLC_Data_Optimized.json'")
        
        return True
        
    except Exception as e:
        print(f"Error optimizing CSV: {e}")
        return False

if __name__ == "__main__":
    optimize_csv()
