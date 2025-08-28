
// function addToCart(bookId) {
//     $.ajax({
//         url: `/cart/add/${bookId}/`,
//         method: "POST",
//         data: {
//             csrfmiddlewaretoken: getCookie("csrftoken")  // if CSRF is enabled
//         },
//         success: function (response) {
//             $("#acknowledge").text("Book added successfully! Cart items: " + response.cart_count)
//                 .css("color", "green")
//                 .fadeIn().delay(2000).fadeOut();
//         },
//         error: function (xhr) {
//             let errorMsg = xhr.responseJSON?.error || "Failed to add book to cart.";
//             $("#acknowledge").text(errorMsg)
//                 .css("color", "red")
//                 .fadeIn().delay(2000).fadeOut();
//         }
//     });
// }

// // Helper to fetch CSRF token if you are using CSRF with JWT
// function getCookie(name) {
//     let cookieValue = null;
//     if (document.cookie && document.cookie !== '') {
//         const cookies = document.cookie.split(';');
//         for (let i = 0; i < cookies.length; i++) {
//             const cookie = cookies[i].trim();
//             if (cookie.substring(0, name.length + 1) === (name + '=')) {
//                 cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
//                 break;
//             }
//         }
//     }
//     return cookieValue;
// }


// <div id="acknowledge" style="display:none;"></div>

