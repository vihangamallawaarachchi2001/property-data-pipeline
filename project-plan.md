# Property Data Intelligence Pipeline
Phase 1 – Project Vision & Scope Definition

---

## 1. Project Goal

The goal of this project is to build a data collection system that scrapes a minimum of 2000 property listings from a dummy property listing website.

The system should collect listings including:
- Rental houses
- Boarding places
- Annexes
- Apartments

For each listing, the system must extract:
- Title
- Location
- Amenities
- Description
- Contact details
- Any available metadata
- At least 5 images per listing

The final objective is to enable structured data analysis and categorization such as:
- Categorization by area
- Categorization by closest university
- Property type grouping
- Future filtering and analysis use cases

---

## 2. Required Data Fields

Each listing must include the following structured fields:

- Listing ID (unique identifier)
- Title
- Property Type (house, annex, boarding, apartment)
- Price
- Location
- Description
- Amenities
- Contact Information
- Image URLs (minimum 5 per listing)
- Scraped Timestamp

Optional fields (if available):
- Bedrooms
- Bathrooms
- Area (sqft)
- Listing Posted Date
- Nearby Landmarks

---

## 3. Estimated Scale

- Minimum Listings Target: 2000
- Images per Listing: At least 5
- Total Estimated Images: 10,000+

This means the system must handle:
- Structured metadata for 2000+ records
- Local storage for 10,000+ image files

---

## 4. Scraping Frequency

- Scraping will run once every 24 hours.

This ensures:
- Data refresh
- Capture of new listings
- Regular updates

---

## 5. Data Update & Duplication Strategy

- No duplicate listings should be stored.
- Listings must be uniquely identified using Listing ID or URL.
- If a listing already exists:
    - Do NOT insert duplicate data.
    - Changes in pricing or other fields will be ignored for now.
- The system focuses on collecting new listings only.

---

## 6. Storage Strategy

To keep the system minimal and simple:

1. Metadata Storage:
   - Stored in a structured Excel file (.xlsx)
   - Each row represents one listing

2. Image Storage:
   - Stored locally in a structured folder system:

     /storage/
         /images/
             /<listing_id>/
                 image1.jpg
                 image2.jpg
                 image3.jpg
                 image4.jpg
                 image5.jpg

This ensures:
- Organized storage
- Easy lookup
- Clean separation of listings

---

## 7. Success Criteria for Phase 1

Phase 1 is considered complete when:

- Project goal is clearly defined
- Required data fields are finalized
- Estimated data scale is calculated
- Scraping frequency is decided
- Deduplication strategy is defined
- Storage approach is finalized

---

End of Phase 1
