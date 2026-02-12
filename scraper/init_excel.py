import pandas as pd
import os

file_path = "../storage/listings.xlsx"

columns = [
   "listing_id",
    "source_url",
    "title",
    "property_type",
    "price",
    "currency",
    "location",
    "area",
    "nearest_university",
    "bedrooms",
    "bathrooms",
    "area_sqft",
    "amenities",
    "description",
    "contact_name",
    "contact_phone",
    "image_folder",
    "scraped_date"
]

if not os.path.exists(file_path):
    df = pd.DataFrame(columns=columns)
    df.to_excel(file_path, index=False)
    print("Excel file initialized successfully.")
else:
    print("Excel file already exists.")