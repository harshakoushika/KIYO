import requests

def get_public_ip():
    """Gets the public IP address of the user."""
    try:
        # Using a reliable service to get the IP
        return requests.get("https://api64.ipify.org?format=json", timeout=5).json()["ip"]
    except Exception as e:
        print(f"Error getting public IP: {e}")
        return None

def get_state_from_ip(ip):
    """Gets the state/region and country from the public IP using ip-api.com."""
    try:
        url = f"http://ip-api.com/json/{ip}?fields=status,message,regionName,country"
        res = requests.get(url, timeout=5).json()
        if res.get("status") == "success":
            return res.get("regionName"), res.get("country")
    except Exception as e:
        print(f"Error getting state from IP: {e}")
    return None, None

def get_language_from_state(state):
    """Returns the official language for the detected Indian state."""
    state_languages = {
        "Telangana": "Telugu",
        "Andhra Pradesh": "Telugu",
        "Tamil Nadu": "Tamil",
        "Karnataka": "Kannada",
        "Kerala": "Malayalam",
        "Maharashtra": "Marathi",
        "West Bengal": "Bengali",
        "Uttar Pradesh": "Hindi",
        "Delhi": "Hindi",
        "Punjab": "Punjabi",
        "Gujarat": "Gujarati",
        "Rajasthan": "Hindi",
        "Bihar": "Hindi",
        "Odisha": "Odia",
        "Assam": "Assamese",
        "Madhya Pradesh": "Hindi",
        "Jharkhand": "Hindi",
        "Haryana": "Hindi",
        "Chhattisgarh": "Hindi",
        "Goa": "Konkani",
        "Manipur": "Meitei (Manipuri)",
        "Meghalaya": "English",
        "Mizoram": "Mizo",
        "Nagaland": "English",
        "Tripura": "Bengali",
        "Sikkim": "Nepali",
        "Arunachal Pradesh": "English",
        "Jammu and Kashmir": "Urdu",
        "Ladakh": "Ladakhi",
    }
    return state_languages.get(state, "English")

# This part is for testing the module independently.
if __name__ == "__main__":
    ip = get_public_ip()
    if ip:
        print("Your Public IP:", ip)
        state, country = get_state_from_ip(ip)
        if state:
            print("Detected State:", state)
            if country == "India":
                language = get_language_from_state(state)
            else:
                language = "English"
            print("Suggested Language:", language)
        else:
            print("Could not detect state.")
    else:
        print("Could not get public IP.")
