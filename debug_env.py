from decouple import config
try:
    sid = config('TWILIO_ACCOUNT_SID', default='MISSING')
    token = config('TWILIO_AUTH_TOKEN', default='MISSING')
    service = config('TWILIO_VERIFY_SERVICE_SID', default='MISSING')
    
    print(f"SID Found: {sid != 'MISSING'}")
    print(f"Token Found: {token != 'MISSING'}")
    print(f"Service Found: {service != 'MISSING'}")
    
    if sid != 'MISSING':
        print(f"SID Start: {sid[:4]}...")
except Exception as e:
    print(f"Error reading config: {e}")
