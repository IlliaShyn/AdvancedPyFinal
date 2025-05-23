import pdfplumber
from geopy.geocoders import Nominatim
import re
import requests
from duckduckgo_search import DDGS
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def file_parser(file):
    coord = ''
    #  PDF parser to text variable
    with pdfplumber.open(file) as pdf_coords:
        for i in pdf_coords.pages:
            coord += i.extract_text()
        return coord


def dms_str_to_decimal(result):
    pattern = r"(\d+)°(\d+)'([\d.]+)\"?([NSEW])"
    matches = re.findall(pattern, result)
    if len(matches) != 2:
        raise ValueError("Input must contain both latitude and longitude in DMS format.")
    def convert(deg, minute, sec, dir):
        dec = int(deg) + int(minute) / 60 + float(sec) / 3600
        if dir in ['S', 'W']:
            dec *= -1
        return dec

    lat = convert(*matches[0])
    lon = convert(*matches[1])
    return lat, lon


# Location search with Nominatim
def loc_search(lat, long):
    # print(f"Latitude: {lat}, Longitude: {long}")
    geolocator = Nominatim(user_agent="tutorial")
    location = geolocator.reverse((lat, long), exactly_one=True)
    return location.address if location else "Location not found"

def save_inline_svg(svg_code, filename="logo.svg"):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(svg_code)
    print(f"Logo saved as: {filename}")

def business_scraper(address):
    place_name = address.split(',')[0].strip()

    with DDGS() as ddgs:
        results = list(ddgs.text(place_name + " official site"))
        if not results:
            return "No website found."
        homepage_url = results[0]['href']

    print(f"Found website: {homepage_url}")

    try:
        response = requests.get(homepage_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        svg_logo = soup.select_one('[class*="cko-logo cko-logo--compact"] svg')
        if svg_logo:
            svg_code = str(svg_logo)
            save_inline_svg(svg_code, f"{place_name}_logo.svg")
            return f"Inline SVG logo found and saved as {place_name}_logo.svg"

    except Exception as e:
        return f"Error fetching or parsing: {e}"

    return "No SVG logo found."


# Main method
def main():
    result = file_parser('circlek.pdf')
    print("Extracted Coord:\n", result)
    try:
        lat, long = dms_str_to_decimal(result)
        print(f"Coordinates:\n Latitude: {lat}, Longitude: {long}")
        address = loc_search(lat, long)
        print(f"Address:\n {address}")
        business = business_scraper(address)
        print(f"Business details:\n {business}")
    except ValueError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()






