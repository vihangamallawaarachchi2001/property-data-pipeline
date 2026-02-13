from bs4 import BeautifulSoup
import json

file_path = "scraper/ikman_detail.html"

with open(file_path, "r", encoding="utf-8") as f:
    html_content = f.read()

soup = BeautifulSoup(html_content, "html.parser")

# Check for JSON-LD
json_ld_scripts = soup.find_all("script", type="application/ld+json")
for script in json_ld_scripts:
    try:
        data = json.loads(script.string)
        print("Found JSON-LD data:")
        print(json.dumps(data, indent=2)[:500])
    except:
        pass

# Check for title, price, description, images
title = soup.find("h1", class_=lambda x: x and "title" in x)
if title:
    print(f"Title: {title.get_text(strip=True)}")
    print(f"Title classes: {title.get('class')}")

price = soup.find("div", class_=lambda x: x and "amount" in x) # 'amount' is common for price
if price:
    print(f"Price: {price.get_text(strip=True)}")
    print(f"Price classes: {price.get('class')}")

desc = soup.find("div", class_=lambda x: x and "description" in x)
if desc:
    print(f"Description found. Classes: {desc.get('class')}")
    print(desc.get_text(strip=True)[:100])

# Images
images = soup.find_all("img", class_=lambda x: x and "gallery" in x) # commonly 'gallery'
print(f"Found {len(images)} gallery images (potential)")

# Attributes (beds, baths, etc)
# Look for dl, dt, dd or similar lists
dls = soup.find_all("dl")
for dl in dls:
    print("Found DL list:")
    print(dl.prettify()[:500])

# Try to find specific keys like "Bedrooms"
bed_label = soup.find(string="Bedrooms:")
if bed_label:
    print(f"Bedrooms label found in: {bed_label.parent}")
