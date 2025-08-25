import json
import time
import random
import curl_cffi

"""

I used the network tab in the browser to find the API endpoint and the parameters used to fetch the data displayed in the browser.

"""


def scrape_olx(search_term, max_pages=3):
    base_url = "https://www.olx.in/api/relevance/v4/search"
    all_listings = []
    
    print(f"Searching for: {search_term}")
    print("-" * 40)
    
    for page in range(1, max_pages + 1):
        print(f"Scraping page {page}...")
        
        # Build parameters
        params = {
            'facet_limit': 1000,
            'lang': 'en-IN',
            'location': '1000001',
            'location_facet_limit': 40,
            'page': page,
            'platform': 'web-desktop',
            'pttEnabled': 'true',
            'query': search_term,
            'relaxedFilters': 'true',
            'size': 40,
            'spellcheck': 'true',
            'user': '0324793783949441'
        }
        
        try:
            # Make request with curl_cffi
            response = curl_cffi.get(base_url, params=params, impersonate="chrome")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                
                # The listings are directly in the 'data' list
                if 'data' in data and isinstance(data['data'], list):
                    page_listings = data['data']
                    all_listings.extend(page_listings)
                    print(f"Found {len(page_listings)} listings on page {page}")
                    
                    if len(page_listings) == 0:
                        print("No more listings found.")
                        break
                else:
                    print("No listings found in response")
                    break
            else:
                print(f"Request failed with status code: {response.status_code}")
                break
                
        except Exception as e:
            print(f"Error on page {page}: {str(e)}")
            break
        
        # Wait between requests
        if page < max_pages:
            time.sleep(random.uniform(1, 3))
    
    return all_listings

def extract_listing_data(listing):
    """Extract all relevant data from a listing"""
    try:
        # Basic info
        title = listing.get('title', 'N/A')
        description = listing.get('description', 'N/A')
        ad_id = listing.get('ad_id', 'N/A')
        
        # Price info
        price_info = listing.get('price', {})
        price = price_info.get('value', {}).get('display', 'N/A')
        
        # Seller info
        seller_name = listing.get('user_name', 'N/A')
        user_type = listing.get('user_type', 'N/A')
        
        # Location info
        location_data = listing.get('locations_resolved', {})
        city = location_data.get('ADMIN_LEVEL_3_name', 'N/A')
        state = location_data.get('ADMIN_LEVEL_1_name', 'N/A')
        area = location_data.get('SUBLOCALITY_LEVEL_1_name', 'N/A')
        
        # Additional info
        created_at = listing.get('created_at', 'N/A')
        
        # Parameters/Attributes
        attributes = {}
        for param in listing.get('parameters', []):
            key = param.get('key_name', param.get('key', 'unknown'))
            value = param.get('formatted_value', param.get('value_name', param.get('value', 'N/A')))
            attributes[key] = value
        
        return {
            'ad_id': ad_id,
            'title': title,
            'description': description,
            'price': price,
            'seller_name': seller_name,
            'user_type': user_type,
            'city': city,
            'state': state,
            'area': area,
            'created_at': created_at,
            'attributes': attributes
        }
    except Exception as e:
        print(f"Error extracting listing data: {str(e)}")
        return None

def display_results(listings, search_term):
    print(f"\nResults for '{search_term}':")
    print("=" * 70)
    print(f"Total listings found: {len(listings)}")
    print()
    
    for i, listing in enumerate(listings[:10], 1):
        extracted = extract_listing_data(listing)
        if extracted:
            print(f"{i}. {extracted['title']}")
            print(f"   Price: {extracted['price']}")
            print(f"   Seller: {extracted['seller_name']} ({extracted['user_type']})")
            print(f"   Location: {extracted['area']}, {extracted['city']}, {extracted['state']}")
            print(f"   Posted: {extracted['created_at']}")
            if extracted['attributes']:
                print(f"   Attributes: {len(extracted['attributes'])} available")
            print(f"   Description: {extracted['description'][:100]}...")
            print()
    
    if len(listings) > 10:
        print(f"... and {len(listings) - 10} more listings")

def save_results(listings, search_term):
    filename = f"olx_results_{search_term.replace(' ', '_').lower()}.json"
    
    # Extract clean data from all listings
    extracted_listings = []
    for listing in listings:
        extracted = extract_listing_data(listing)
        if extracted:
            extracted_listings.append(extracted)
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'search_term': search_term,
                'total_results': len(extracted_listings),
                'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'listings': extracted_listings
            }, f, indent=2, ensure_ascii=False)
        print(f"Clean results saved to: {filename}")
        print(f"Extracted {len(extracted_listings)} listings with full details")
    except Exception as e:
        print(f"Error saving file: {str(e)}")

def main():
    search_term = "Car Cover"
    
    print("Starting OLX scraper...")
    listings = scrape_olx(search_term, max_pages=3)
    
    display_results(listings, search_term)
    save_results(listings, search_term)
    
    print("Scraping completed.")

if __name__ == "__main__":
    main()
