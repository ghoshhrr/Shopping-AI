      let cart = [];

      function addToCart(item) {
        if (!cart.includes(item)) {
          cart.push(item);
          document.getElementById("user_cart").value = cart.join(", ");
        }
      }