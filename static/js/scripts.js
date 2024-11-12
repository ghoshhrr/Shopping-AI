let cart = [];
let aisle_data = "";
const ITEM_CONTAINER = document.getElementById("items");

let currAisle;

function readJSON() {
  fetch(".././static/grocery_data.json")
    .then((response) => response.json())
    .then((data) => {
      console.log(data);
      aisle_data = data;
      currAisle = document.querySelector(".selected");
      generateAislePage(currAisle.textContent);
      getAisleRecommendations(currAisle.textContent);
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}

// Called when aisle selector is changed, calls aisle page generator with appropriate aisle value
function handleSelectChange(aisle) {
  currAisle = document.getElementById(aisle);
  document.querySelector(".selected").classList.remove("selected");
  currAisle.classList.add("selected");
  generateAislePage(currAisle.textContent);
  getAisleRecommendations(currAisle.textContent);
}

// Generates an Aisle Page from JSON data
function generateAislePage(aisle) {
  if (!aisle || !aisle_data[aisle]) return;
  ITEM_CONTAINER.innerHTML = "";

  // Loop through each item in the array for the selected aisle
  aisle_data[aisle].forEach((item) => {
    let currItem = item["item_details"];
    generateItemBlock(currItem["name"], currItem["price"], currItem["image"]);
  });
}

function generateItemBlock(name, price, img) {
  console.log(name, price, img);
  const itemBlock = document.createElement("div");
  itemBlock.classList.add("item");
  let path = "../static/images/" + img;
  let cartImage = "../static/images/cart.png";

  itemBlock.innerHTML = `
    <li>
      <img src="${path}" alt="${name}" class="item-image">
      <p class="item-name">${name}</p>
      <div class="price-add">
        <p class="item-price"> $${price}</p>
        <img type="button" src="${cartImage}" id="addtocart" onclick="addToCart('${name}', '${price}', '${img}')"/>
      </div>
    </li>
  `;

  ITEM_CONTAINER.appendChild(itemBlock);
}

function addToCart(name, price, img) {
  let found = cart.find((item) => item.name === name);
  if (found) {
    found.quantity += 1;
  } else {
    cart.push({ name: name, price: price, img: img, quantity: 1 });
  }
  cartDisplay();
  getAisleRecommendations(currAisle.textContent);
}

function cartDisplay() {
  const cartContainer = document.getElementById("cart_items");
  cartContainer.innerHTML = "<h2>Your Cart</h2>";

  if (cart.length === 0) {
    cartContainer.innerHTML += "<p>Your cart is empty.</p>";
    return;
  }

  cart.forEach((item) => {
    const cartItem = document.createElement("div");
    cartItem.classList.add("cart-item");
    let img = "../static/images/" + item.img;

    cartItem.innerHTML = `
      <div class="cart-item-content">
        <img src="${img}" alt="${item.name}" class="cart-item-image">
        <div class="cart-item-details">
          <p class="cart-item-name">${item.name}</p>
          <p class="cart-item-price">Price: $${item.price}</p>
          <p class="cart-item-quantity">Quantity: ${item.quantity}</p>
          <button class="cart-remove" onclick="removeFromCart('${item.name}')">Remove</button>
        </div>
      </div>
    `;
    cartContainer.appendChild(cartItem);
  });
}

function removeFromCart(name) {
  cart = cart.filter((item) => item.name !== name);
  cartDisplay();
}

function getRecommendations() {
  const userCart = cart.map((item) => item.name.toLowerCase().trim());

  fetch("/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ user_cart: userCart }),
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      return response.json();
    })
    .then((data) => {
      displayRecommendations(data);
    })
    .catch((error) => console.error("Error:", error));
}

function getAisleRecommendations(aisleName) {
  fetch("/aisle_recommendations", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ aisle_name: aisleName, user_cart: cart }),
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      return response.json();
    })
    .then((data) => {
      displayAisleRecommendations(data);
    })
    .catch((error) => console.error("Error:", error));
}

function displayRecommendations(data) {
  const recommendationsList = document.getElementById("recommendationsList");
  const messageElement = document.getElementById("message");

  recommendationsList.innerHTML = "";
  messageElement.textContent = "";

  if (data.message) {
    messageElement.textContent = data.message;
  }

  if (data.recommendations) {
    data.recommendations.forEach((item) => {
      const li = document.createElement("li");
      li.textContent = item;
      recommendationsList.appendChild(li);
    });
  }

  if (data.aisle_recommendations) {
    data.aisle_recommendations.forEach((item) => {
      const li = document.createElement("li");
      li.textContent = item;
      aisleRecommendationsList.appendChild(li);
    });
  }
}

function displayAisleRecommendations(data) {
  const aisleRecommendationsList = document.getElementById(
    "aisleRecommendationsList"
  );
  aisleRecommendationsList.innerHTML = "";

  if (data.aisle_recommendations) {
    data.aisle_recommendations.forEach((item) => {
      const li = document.createElement("li");
      li.textContent = item;
      aisleRecommendationsList.appendChild(li);
    });
  }
}
