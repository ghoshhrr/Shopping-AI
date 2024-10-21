import csv
import json

# Define the Item class
class Item:
    def __init__(self, name, price, image="placeholder.jpg"):
        self.name = name
        self.details = {
            "price": price,
            "image": image
        }

# Function to read CSV, process data, and write to JSON
def process_items(csv_file, json_file):
    aisle_dict = {}

    # Read the CSV file
    with open(csv_file, mode='r') as file:
        csv_reader = csv.DictReader(file)

        for row in csv_reader:
            item_description = row['itemDescription']
            item_aisle = row['itemAisle']
            item_price = 0

            # Create a new item object
            item = Item(item_description, item_price).__dict__

            # Add item to the corresponding aisle
            if item_aisle not in aisle_dict:
                aisle_dict[item_aisle] = [item]
            else:
                # Only add unique items by description
                if all(existing_item['name'] != item_description for existing_item in aisle_dict[item_aisle]):
                    aisle_dict[item_aisle].append(item)

    # Write the aisle dictionary to a JSON file
    with open(json_file, mode='w') as json_file:
        json.dump(aisle_dict, json_file, indent=4)

# Example usage
csv_file = 'Groceries_dataset_improved.csv'
json_file = 'grocery_data.json'
process_items(csv_file, json_file)
