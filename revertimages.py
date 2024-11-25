import json

# Load JSON data
with open("grocery_data.json", "r") as file:
    data = json.load(file)

# Update all image paths to "placeholder.jpg"
for aisle, items in data.items():
    for item in items:
        item["item_details"]["image"] = "placeholder.jpg"

# Save the updated JSON data
with open("grocery_data.json", "w") as file:
    json.dump(data, file, indent=4)

print("All image paths reset to 'placeholder.jpg'.")
