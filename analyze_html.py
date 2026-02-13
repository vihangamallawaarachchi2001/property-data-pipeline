from bs4 import BeautifulSoup

file_path = "scraper/ikman_property.html"

with open(file_path, "r", encoding="utf-8") as f:
    html_content = f.read()

soup = BeautifulSoup(html_content, "html.parser")

# Find all script tags and print their content if it contains window.__
scripts = soup.find_all("script")
for script in scripts:
    if script.string and "window.__" in script.string:
        print("Found window.__ script:")
        print(script.string[:500]) # Print first 500 chars
        print("...")

# Try to find listing items
# Look for common classes
listings = soup.find_all("li", class_=lambda x: x and "normal--2QYVk" in x)
if not listings:
    listings = soup.find_all("li", class_=lambda x: x and "top-ads-container--1Jeos" in x)

print(f"Found {len(listings)} listings (potential)")

if not listings:
    # Try generic search for list items
    all_lis = soup.find_all("li")
    print(f"Total li elements: {len(all_lis)}")
    # Print classes of first 10 lis
    for i, li in enumerate(all_lis[:10]):
        print(f"Li {i} classes: {li.get('class')}")
else:
    first_listing = listings[0]
    print("First listing HTML:")
    print(first_listing.prettify())
