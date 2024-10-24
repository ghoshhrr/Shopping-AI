let cart = [];
let aisle_data = "";
const ITEM_CONTAINER = document.getElementById("items");
const ITEM_HTML = ``;

function readJSON() {
  fetch("static/grocery_data.json")
    .then((response) => response.json())
    .then((data) => {
      console.log(data);
      aisle_data = data;
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}

// Called when aisle selector is changed, calls aisle page generator with appropriate aisle value
function handleSelectChange() {
  const selectElement = document.getElementById("aisles_select");
  let val = selectElement.value;
  generateAislePage(val);
}

// Generates an Aisle Page from JSON data
function generateAislePage(aisle) {
  if (aisle == "")
    // No aisle selected has null value
    return;
  ITEM_CONTAINER.innerHTML = "";
  console.log(aisle);
  for (let item in aisle_data[aisle]) {
    let currItem = aisle_data[aisle][item]["item_details"];
    generateItemBlock(currItem["name"], currItem["price"], currItem["image"]);
  }
}

function generateItemBlock(name, price, img) {
  console.log(name, price, img);
  // Create a div element for the new item block to hold the item
  const itemBlock = document.createElement("div");
  itemBlock.classList.add("item"); // Add a class for styling later on
  let path = "static/images/" + img; // Get path for image, images should be ideally named <exact_item_name>.jpg
  let cartImage = "static/images/cart.png"
  // Generate the HTML content for the item block
  itemBlock.innerHTML = `
      <li>
       <img src="${path}" alt="${name}" class="item-image">
       <p class="item-name">${name}</p>
       <p class="item-price"> $${price}</p>
      <img type="button" src="${cartImage}"id="addtocart" onclick="addToCart('${name}')"/>
      </li>
   `;

  // Append the new item block to the container
  ITEM_CONTAINER.appendChild(itemBlock);
}

function addToCart(item) {
  if (!cart.includes(item)) {
    cart.push(item);
    document.getElementById("user_cart").value = cart.join(", ");
  }
}
