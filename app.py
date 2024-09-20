import pandas as pd
from flask import Flask, render_template, request
from mlxtend.frequent_patterns import apriori, association_rules

app = Flask(__name__)
#Test push and pull
# Load the grocery dataset and use one-hot encoding
grocery_data = pd.read_csv('Groceries_dataset_improved.csv')
grocery_data['Date'] = pd.to_datetime(grocery_data['Date'])
baskets = grocery_data.groupby(['Member_number', 'itemDescription'])['itemDescription'].count().unstack().fillna(0).reset_index()
baskets_encoded = baskets.iloc[:, 1:].applymap(lambda count: 1 if count > 0 else 0)

# Set min support
support_threshold = 0.005

# Find itemsets using apriori then use association rules to get rules based on lift
rules = association_rules(apriori(baskets_encoded, min_support=support_threshold, use_colnames=True), metric="lift", min_threshold=1)

# Find relevant rules based on current cart
def find_relevant_rules(cart, rules):
    # Turn cart into set (faster)
    cart_set = set(cart)
    # Check for rules that have only cart items in the antecedents
    relevant = rules[rules['antecedents'].apply(lambda x: set(x).issubset(cart_set))]
    # Remove rules that have cart items in the consequents and ensure set is disjoint
    relevant = relevant[relevant['consequents'].apply(lambda x: not set(x).issubset(cart_set))]
    relevant = relevant[relevant['consequents'].apply(lambda x: set(x).isdisjoint(cart_set))]
    return relevant

# Get top "N" items can be user selected if we want
def get_top_consequents(rules, top_n=5):
    # Loop through consequents and counts them to get top results
    all_consequents = [item for sublist in rules['consequents'].tolist() for item in sublist]
    counts = pd.Series(all_consequents).value_counts()
    return counts.head(top_n).index.tolist()

# Currently using get and post requests, can change if better method found 
@app.route('/', methods=['GET', 'POST'])
def index():
    recommendations = []
    message = ""
    if request.method == 'POST':
        # Takes users cart as input and finds rules for it
        user_cart_input = request.form['user_cart']
        user_cart = set(item.strip() for item in user_cart_input.split(','))

        # Check if the users cart is full of valid items
        if not user_cart.issubset(set(baskets_encoded.columns)):
            message = "Invalid items found"
        else:
            relevant_rules = find_relevant_rules(user_cart, rules)
        
            if relevant_rules.empty:
                message = "No recommendations found"
            else:
                # Sorts the rules based on lift and gets top "N" recommended items
                sorted_rules = relevant_rules[['antecedents', 'consequents', 'support', 'confidence', 'lift']].sort_values('lift', ascending=False)
                recommendations = get_top_consequents(sorted_rules, 100)
                
    # Uses the recommendations found to populate the html
    return render_template('index.html', recommendations=recommendations, message=message)

if __name__ == '__main__':
    app.run(debug=True)
