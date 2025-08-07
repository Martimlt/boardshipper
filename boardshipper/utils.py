# Utility functions and constants for BoardShipper

import os
import requests
import base64
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

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
    
    # Get parcel dimensions based on board type
    # Note: booking.box_size now contains 'shortboard', 'midlength', or 'longboard'
    parcel_info = BOX_SIZE_MAP.get(booking.box_size, BOX_SIZE_MAP['shortboard'])
    
    # Construct EasyPost payload
    payload = {
        "shipment": {
            "to_address": {
                "name": f"{booking.recipient_first_name} {booking.recipient_last_name}",
                "street1": booking.recipient_street,
                "city": booking.recipient_city,
                "state": booking.recipient_state,
                "zip": booking.recipient_zip,
                "country": booking.recipient_country,
                "phone": "",  # Add phone field if available in booking
                "email": ""   # Add email field if available in booking
            },
            "from_address": {
                "name": sender_profile.business_name,
                "street1": sender_profile.street_address,
                "city": sender_profile.city,
                "state": sender_profile.state,
                "zip": sender_profile.zip_code,
                "country": sender_profile.country,
                "phone": "",  # Add phone field if available in profile
                "email": sender_profile.user.email  # Get email from associated user
            },
            "parcel": {
                "length": parcel_info['length'],
                "width": parcel_info['width'],
                "height": parcel_info['height'],
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
    
    # Check if rates are available
    if not shipment.get('rates'):
        raise Exception("No shipping rates available for this shipment")
    
    # Select a rate (using the first one for now - you might want to add logic to select specific carrier/service)
    # In production, you might want to filter by carrier (USPS, FedEx, UPS) or service type
    rate_id = shipment['rates'][0]['id']
    
    # Purchase the shipping label
    try:
        buy_resp = requests.post(
            f"https://api.easypost.com/v2/shipments/{shipment['id']}/buy",
            json={'rate': {'id': rate_id}},
            headers=headers
        )
        buy_resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise Exception(f"EasyPost API Error purchasing label: {str(e)}")
    
    if buy_resp.status_code != 200 and buy_resp.status_code != 201:
        raise Exception(f"EasyPost Buy Error: {buy_resp.text}")
    
    bought_shipment = buy_resp.json()
    
    # Extract the relevant information
    return {
        'shipment_id': bought_shipment['id'],
        'label_url': bought_shipment.get('postage_label', {}).get('label_url', ''),
        'tracking_url': bought_shipment.get('tracker', {}).get('public_url', ''),
        'tracking_code': bought_shipment.get('tracking_code', ''),
        'selected_rate': bought_shipment.get('selected_rate', {})
    }


def get_easypost_rates(sender_profile, booking):
    """
    Get shipping rates from EasyPost without purchasing.
    Useful for showing rates to customers before finalizing.
    
    Args:
        sender_profile: UserProfile object with sender's address information
        booking: Booking object with recipient info and package details
    
    Returns:
        list of available rates
    """
    
    if not EASYPOST_API_KEY:
        raise ValueError("EASYPOST_API_KEY not configured. Please set it in environment variables.")
    
    # Get parcel dimensions based on board type
    parcel_info = BOX_SIZE_MAP.get(booking.box_size, BOX_SIZE_MAP['shortboard'])
    
    # Construct EasyPost payload
    payload = {
        "shipment": {
            "to_address": {
                "name": f"{booking.recipient_first_name} {booking.recipient_last_name}",
                "street1": booking.recipient_street,
                "city": booking.recipient_city,
                "state": booking.recipient_state,
                "zip": booking.recipient_zip,
                "country": booking.recipient_country,
            },
            "from_address": {
                "name": sender_profile.business_name,
                "street1": sender_profile.street_address,
                "city": sender_profile.city,
                "state": sender_profile.state,
                "zip": sender_profile.zip_code,
                "country": sender_profile.country,
                "email": sender_profile.user.email
            },
            "parcel": {
                "length": parcel_info['length'],
                "width": parcel_info['width'],
                "height": parcel_info['height'],
                "weight": float(booking.weight) * 16,  # Convert pounds to ounces
            }
        }
    }
    
    # Prepare authentication headers
    headers = {
        'Authorization': 'Basic ' + base64.b64encode(f"{EASYPOST_API_KEY}:".encode()).decode(),
        'Content-Type': 'application/json'
    }
    
    # Create shipment to get rates
    try:
        resp = requests.post(
            'https://api.easypost.com/v2/shipments',
            json=payload,
            headers=headers
        )
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise Exception(f"EasyPost API Error getting rates: {str(e)}")
    
    if resp.status_code != 200 and resp.status_code != 201:
        raise Exception(f"EasyPost Error: {resp.text}")
    
    shipment = resp.json()
    
    # Return the rates for display/selection
    return shipment.get('rates', [])