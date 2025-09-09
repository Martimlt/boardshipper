# Utility functions and constants for BoardShipper

import os
import requests
import base64
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Country name to ISO code mapping for EasyPost
COUNTRY_CODE_MAP = {
    'United States': 'US',
    'Canada': 'CA',
    'Mexico': 'MX',
    'Australia': 'AU',
    'New Zealand': 'NZ',
    'United Kingdom': 'GB',
    'France': 'FR',
    'Spain': 'ES',
    'Portugal': 'PT',
    'Brazil': 'BR',
    'Argentina': 'AR',
    'Chile': 'CL',
    'Peru': 'PE',
    'Ecuador': 'EC',
    'Costa Rica': 'CR',
    'Panama': 'PA',
    'Nicaragua': 'NI',
    'El Salvador': 'SV',
    'Guatemala': 'GT',
    'Japan': 'JP',
    'Indonesia': 'ID',
    'Philippines': 'PH',
    'Thailand': 'TH',
    'Malaysia': 'MY',
    'Singapore': 'SG',
    'South Africa': 'ZA',
    'Morocco': 'MA',
    'Ireland': 'IE',
    'Germany': 'DE',
    'Italy': 'IT',
    'Netherlands': 'NL',
    'Belgium': 'BE',
    'Switzerland': 'CH',
    'Austria': 'AT',
    'Norway': 'NO',
    'Sweden': 'SE',
    'Denmark': 'DK',
    'Finland': 'FI',
}

# Box size mapping for different board types
BOX_SIZE_MAP = {
    'shortboard':  {'length': 76, 'width': 22, 'height': 5},   # 76 × 22 × 5 in
    'midlength': {'length': 90, 'width': 23, 'height': 7},     # 90 × 23 × 7 in
    'longboard':  {'length': 120, 'width': 24, 'height': 7},   # 120 × 24 × 7 in
}

# EasyPost API Key - loaded from .env file or environment variables
EASYPOST_API_KEY = os.getenv('EASYPOST_API_KEY', '')

def create_easypost_shipment(sender_profile, booking):
    """
    Create a shipment with EasyPost and purchase a shipping label.
    
    Args:
        sender_profile: UserProfile object with sender's address information
        booking: Booking object with recipient info and package details
    
    Returns:
        dict with shipment_id, label_url, and tracking_url
    """
    if not EASYPOST_API_KEY:
        raise ValueError("EASYPOST_API_KEY not configured. Please set it in environment variables.")
    
    is_test_mode = EASYPOST_API_KEY.startswith('EZTK')
    
    parcel_info = BOX_SIZE_MAP.get(booking.box_size, BOX_SIZE_MAP['shortboard'])
    
    recipient_country_code = COUNTRY_CODE_MAP.get(booking.recipient_country, 'US')
    sender_country_code = COUNTRY_CODE_MAP.get(sender_profile.country, 'US')
    to_address = {
        "name": f"{booking.recipient_first_name} {booking.recipient_last_name}",
        "street1": booking.recipient_street,
        "city": booking.recipient_city,
        "state": booking.recipient_state,
        "zip": booking.recipient_zip,
        "country": recipient_country_code,
        "email": booking.recipient_email,
        "phone": booking.recipient_phone
    }
    from_address = {
        "name": sender_profile.business_name or "Sender Name",
        "street1": sender_profile.street_address,
        "city": sender_profile.city,
        "state": sender_profile.state,
        "zip": sender_profile.zip_code,
        "country": sender_country_code,
        "email": sender_profile.user.email or "sender@example.com",
        "phone": "555-555-5555"
    }
    
    payload = {
        "shipment": {
            "to_address": to_address,
            "from_address": from_address,
            "parcel": {
                "length": float(parcel_info['length']),
                "width": float(parcel_info['width']),
                "height": float(parcel_info['height']),
                "weight": float(booking.weight) * 16,  # Convert pounds to ounces
            }
        }
    }
    
    # Prepare authentication headers
    headers = {
        'Authorization': 'Basic ' + base64.b64encode(f"{EASYPOST_API_KEY}:".encode()).decode(),
        'Content-Type': 'application/json'
    }
    
    # Create shipment with EasyPost
    try:
        resp = requests.post(
            'https://api.easypost.com/v2/shipments',
            json=payload,
            headers=headers
        )
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise Exception(f"EasyPost API Error creating shipment: {str(e)}")
    
    if resp.status_code != 200 and resp.status_code != 201:
        raise Exception(f"EasyPost Error: {resp.text}")
    
    shipment = resp.json()
    
    if not shipment.get('rates'):
        if is_test_mode:
            raise Exception("No shipping rates available. Test mode is using fixed test addresses.")
        else:
            raise Exception("No shipping rates available for this shipment. Please verify the addresses are valid.")
    
    rates = shipment.get('rates', [])
    gso_rates = [rate for rate in rates if rate.get('carrier') == 'GSO']
    
    if not gso_rates:
        raise Exception("No shipping rate available for this location. Contact admin.")
    
    cheapest_rate = min(gso_rates, key=lambda x: float(x.get('rate', float('inf'))))
    rate_id = cheapest_rate['id']
    
    try:
        buy_resp = requests.post(
            f"https://api.easypost.com/v2/shipments/{shipment['id']}/buy",
            json={'rate': {'id': rate_id}, 'insurance': '500.00'},
            headers=headers
        )
        buy_resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise Exception(f"EasyPost API Error purchasing label: {str(e)}")
    
    if buy_resp.status_code != 200 and buy_resp.status_code != 201:
        raise Exception(f"EasyPost Buy Error: {buy_resp.text}")
    
    bought_shipment = buy_resp.json()
    
    selected_rate = bought_shipment.get('selected_rate', {})
    return {
        'shipment_id': bought_shipment['id'],
        'label_url': bought_shipment.get('postage_label', {}).get('label_url', ''),
        'tracking_url': bought_shipment.get('tracker', {}).get('public_url', ''),
        'tracking_code': bought_shipment.get('tracking_code', ''),
        'carrier': selected_rate.get('carrier', ''),
        'service': selected_rate.get('service', ''),
        'rate': selected_rate.get('rate', 0),
        'selected_rate': selected_rate
    }
