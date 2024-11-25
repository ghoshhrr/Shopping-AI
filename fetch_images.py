import requests
import json
import os
import time

# Set up your API key and paths
UNSPLASH_API_KEY = 'BdmwediH7hn2mkEvuAhJBk1dyvVv6HFK9-MtDajumLw'
image_folder = 'images' # Folder to save images
MAX_REQUESTS_PER_HOUR = 50

# Ensure the main images folder exists
if not os.path.exists(image_folder):
    os.makedirs(image_folder)

# Load JSON data
with open("grocery_data.json", "r") as file:
    data = json.load(file)

# Function to download images with error handling
def download_image(search_term, file_path):
    url = f"https://api.unsplash.com/photos/random?query={search_term}&client_id={UNSPLASH_API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        img_url = response.json().get("urls", {}).get("small")
        
        if img_url:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Download and save the image
            img_data = requests.get(img_url).content
            with open(file_path, "wb") as img_file:
                img_file.write(img_data)
            print(f"Image for '{search_term}' downloaded successfully.")
            return file_path  # Return the file path if successful
        else:
            print(f"No image URL found for '{search_term}'.")
    except requests.exceptions.RequestException as e:
        print(f"Request failed for '{search_term}': {e}")
    return None

# Update JSON data with downloaded image names only
request_count = 0
for aisle, items in data.items():
    for item in items:
        image_name = item["item_details"].get("image", "")
        
        # Skip if image already exists and is not a placeholder
        if image_name != "placeholder.jpg" and image_name:
            print(f"Skipping '{item['item_details']['name']}' as it already has an image.")
            continue
        
        # Prepare search term and file path
        raw_name = item["item_details"]["name"]  # Original name with spaces
        search_term = raw_name  # Use spaces in search term
        file_safe_name = raw_name.replace(" ", "_").lower()  # Convert to safe filename
        image_path = os.path.join(image_folder, f"{file_safe_name}.jpg")
        
        # Download image if limit has not been reached
        if request_count < MAX_REQUESTS_PER_HOUR:
            downloaded_image_path = download_image(search_term, image_path)
            request_count += 1
            
            # Update JSON with just the image name
            if downloaded_image_path:
                item["item_details"]["image"] = f"{file_safe_name}.jpg"
            else:
                item["item_details"]["image"] = "placeholder.jpg"
        else:
            # Wait for an hour before resuming
            print("Rate limit reached. Pausing for one hour...")
            time.sleep(3600)  # Pause for 1 hour (3600 seconds)
            request_count = 0  # Reset the request count

# Save the updated JSON data with new image paths
with open("grocery_data.json", "w") as file:
    json.dump(data, file, indent=4)

print("JSON file updated with image names only.")