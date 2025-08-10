import os
import requests

# Read from .env file
env_path = '.env'
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        for line in f:
            if line.startswith('EASYPOST_API_KEY='):
                api_key = line.strip().split('=', 1)[1]
                break
else:
    api_key = os.environ.get('EASYPOST_API_KEY')
    
if not api_key:
    print("ERROR: EASYPOST_API_KEY not found")
    exit(1)

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# Test shipment from San Diego to New York
def test_rates(box_type, dimensions):
    print(f"\n{'='*50}")
    print(f"Testing {box_type}")
    print(f"{'='*50}")
    
    shipment_data = {
        "shipment": {
            "from_address": {
                "name": "Test Sender",
                "street1": "1234 Surf Street",
                "city": "San Diego",
                "state": "CA",
                "zip": "92101",
                "country": "US",
                "phone": "555-123-4567"
            },
            "to_address": {
                "name": "Test Recipient",
                "street1": "5678 Broadway",
                "city": "New York",
                "state": "NY",
                "zip": "10001",
                "country": "US",
                "phone": "555-987-6543"
            },
            "parcel": {
                "length": dimensions["length"],
                "width": dimensions["width"],
                "height": dimensions["height"],
                "weight": dimensions["weight"]
            }
        }
    }
    
    # Create shipment
    response = requests.post(
        "https://api.easypost.com/v2/shipments",
        json=shipment_data,
        headers=headers
    )
    
    if response.status_code != 201:
        print(f"Error creating shipment: {response.status_code}")
        print(response.json())
        return
    
    shipment = response.json()
    rates = shipment.get('rates', [])
    
    print(f"From: San Diego, CA")
    print(f"To: New York, NY")
    print(f"Dimensions: {dimensions['length']}x{dimensions['width']}x{dimensions['height']} inches")
    print(f"Weight: {dimensions['weight']} oz")
    print(f"\nAvailable rates:")
    print("-" * 50)
    
    # Sort rates by price
    rates.sort(key=lambda x: float(x.get('rate', 0)))
    
    for rate in rates:
        carrier = rate.get('carrier', 'Unknown')
        service = rate.get('service', 'Unknown')
        price = rate.get('rate', 'N/A')
        delivery_days = rate.get('delivery_days', 'N/A')
        
        print(f"{carrier:10} | {service:30} | ${price:8} | {delivery_days} days")
    
    # Find GSO/GLS rates if available
    gso_rates = [r for r in rates if r.get('carrier', '').upper() in ['GSO', 'GLS']]
    if gso_rates:
        print(f"\n*** GSO/GLS Rate Found: ${gso_rates[0].get('rate')} ***")
    
    # Show what customer would pay with our pricing
    if box_type == "Shortboard":
        customer_price = 95  # NY is "other state"
    elif box_type == "Midlength":
        customer_price = 195  # NY is "other state"
    else:  # Longboard
        customer_price = "Not Available"  # Not available for NY
    
    print(f"\n*** Customer Price: ${customer_price} ***")
    
    if gso_rates and customer_price != "Not Available":
        margin = customer_price - float(gso_rates[0].get('rate'))
        print(f"*** Your Margin: ${margin:.2f} ***")

# Board dimensions
boards = {
    "Shortboard": {
        "length": 84,
        "width": 23,
        "height": 6,
        "weight": 240  # 15 lbs in oz
    },
    "Midlength": {
        "length": 96,
        "width": 26,
        "height": 6,
        "weight": 320  # 20 lbs in oz
    },
    "Longboard": {
        "length": 120,
        "width": 26,
        "height": 6,
        "weight": 400  # 25 lbs in oz
    }
}

# Test only shortboard and midlength
for board_type in ["Shortboard", "Midlength"]:
    test_rates(board_type, boards[board_type])