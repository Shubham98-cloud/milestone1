import os
import pandas as pd
from datasets import load_dataset
from sqlalchemy import create_engine

# 1. Extraction: Load dataset from HuggingFace
def extract_data():
    print("Downloading dataset from HuggingFace...")
    dataset = load_dataset('ManikaSaini/zomato-restaurant-recommendation')
    df = dataset['train'].to_pandas()
    return df

# 2. Transformation: Clean and structure data
def transform_data(df):
    print("Transforming dataset...")
    
    print(f"Columns found: {list(df.columns)}")
    
    col_lower = {c: c.lower() for c in df.columns}
    
    final_df = pd.DataFrame()
    for c, lower in col_lower.items():
        if 'name' in lower and 'id' not in lower:
            final_df['name'] = df[c]
        elif 'location' in lower or 'city' in lower or 'locality' in lower:
            final_df['location'] = df[c].astype(str).str.lower().str.strip()
        elif 'cuisine' in lower:
            final_df['cuisine'] = df[c].astype(str).str.lower().str.strip()
        elif 'cost' in lower:
            final_df['cost'] = df[c].astype(str).str.replace(',', '', regex=False).str.extract(r'(\d+)').astype(float)
        elif 'rate' in lower or 'rating' in lower:
            final_df['rating'] = df[c].astype(str).str.extract(r'(\d+\.\d+|\d+)').astype(float)
            
    # Fallback to None if not matched
    for req_col in ['name', 'location', 'cuisine', 'cost', 'rating']:
        if req_col not in final_df.columns:
            final_df[req_col] = None

    # Handle Missing Values based on critical requirement (name)
    if 'name' in final_df.columns:
        final_df = final_df.dropna(subset=['name'])
    
    print("Sample Data:")
    print(final_df.head(5))
    return final_df

# 3. Storage: Save data to SQLite Local Database
def load_data_to_db(df, db_path='sqlite:///restaurants.db'):
    print(f"Loading data into {db_path}...")
    engine = create_engine(db_path)
    
    df.to_sql('restaurants', con=engine, if_exists='replace', index=True, index_label='id')
    print("Data loaded to database successfully.")
    
def main():
    try:
        df_raw = extract_data()
        df_clean = transform_data(df_raw)
        load_data_to_db(df_clean)
        print("Phase 1 implementation complete: Database is ready.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
