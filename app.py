import pandas as pd
from flask import Flask, jsonify, render_template, request
from mlxtend.frequent_patterns import apriori, association_rules

app = Flask(__name__)

# Load the grocery dataset and use one-hot encoding
grocery_data = pd.read_csv('Groceries_dataset_improved.csv')
grocery_data['Date'] = pd.to_datetime(grocery_data['Date'])
baskets = grocery_data.groupby(['Member_number', 'itemDescription'])['itemDescription'].count().unstack().fillna(0).reset_index()
baskets_encoded = baskets.iloc[:, 1:].applymap(lambda count: 1 if count > 0 else 0)

# Set minimum support threshold
support_threshold = 0.005

# Find itemsets using Apriori, then use association rules to get rules based on lift
rules = association_rules(apriori(baskets_encoded, min_support=support_threshold, use_colnames=True), metric="lift", min_threshold=1)

# Find relevant rules based on current cart
def find_relevant_rules(cart, rules):
    cart_set = set(cart)
    relevant = rules[rules['antecedents'].apply(lambda x: set(x).issubset(cart_set))]
    relevant = relevant[relevant['consequents'].apply(lambda x: not set(x).issubset(cart_set))]
    relevant = relevant[relevant['consequents'].apply(lambda x: set(x).isdisjoint(cart_set))]
    return relevant

# Get top "N" items; can be user-selected if needed
def get_top_consequents(rules, top_n=5):
    all_consequents = [item for sublist in rules['consequents'].tolist() for item in sublist]
    counts = pd.Series(all_consequents).value_counts()
    return counts.head(top_n).index.tolist()

def find_aisle_recommendations(aisle_name, grocery_data, cart):
    aisle_items = grocery_data[grocery_data['itemAisle'] == aisle_name]
    aisle_items = aisle_items[~aisle_items['itemDescription'].str.lower().isin([item.lower() for item in cart])]
    return aisle_items['itemDescription'].value_counts().head(5).index.tolist()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST': 
        if not request.is_json:
            return jsonify({"error": "Invalid Content-Type. Expected 'application/json'."}), 415

        data = request.get_json()
        user_cart = set(item.strip().lower() for item in data.get("user_cart", []))

        valid_items = set(item.strip().lower() for item in baskets_encoded.columns)
        message = ""
        recommendations = []
        
        if not user_cart.issubset(valid_items):
            message = "Invalid items found"
        else:
            relevant_rules = find_relevant_rules(user_cart, rules)
            if relevant_rules.empty:
                message = "No recommendations found"
            else:
                sorted_rules = relevant_rules[['antecedents', 'consequents', 'support', 'confidence', 'lift']].sort_values('lift', ascending=False)
                recommendations = get_top_consequents(sorted_rules)
                aisle_name = "Dairy"  # Example aisle; replace with dynamic aisle if needed
        
        return jsonify({
            "message": message,
            "recommendations": recommendations,
        })
    
    return render_template('index.html')

@app.route('/aisle_recommendations', methods=['POST'])
def aisle_recommendations():
    if not request.is_json:
        return jsonify({"error": "Invalid Content-Type. Expected 'application/json'."}), 415

    data = request.get_json()
    aisle_name = data.get("aisle_name")
    user_cart = set(item["name"].strip().lower() for item in data.get("user_cart", []) if "name" in item)
    aisle_recommendations = find_aisle_recommendations(aisle_name, grocery_data, user_cart)

    return jsonify({
        "aisle_recommendations": aisle_recommendations
    })

if __name__ == '__main__':
    app.run(debug=True)
