import requests
import io

def test_api():
    base_url = "http://127.0.0.1:8000"
    
    # 1. Health check
    health = requests.get(f"{base_url}/")
    print("Health Check:", health.json())

    # 2. Test the API with our local image
    img_path = "test.png"
    print(f"Testing API with local image: {img_path}...")
    
    try:
        with open(img_path, "rb") as f:
            file_bytes = f.read()

        print("Sending to API for measurement extraction...")
        # Prepare the file payload
        files = {
            "file": ("test.png", file_bytes, "image/png")
        }
        # Provide a reference height (e.g., 180 cm)
        data = {
            "reference_height_cm": 180.0
        }
        
        # POST to the measurements endpoint
        api_resp = requests.post(f"{base_url}/measurements/", files=files, data=data)
        
        if api_resp.status_code == 200:
            print("\nAPI Response:")
            print(api_resp.json())
        else:
            print(f"Error from API: {api_resp.status_code}")
            print(api_resp.text)
    except FileNotFoundError:
        print(f"Error: Could not find {img_path}")

if __name__ == "__main__":
    test_api()
