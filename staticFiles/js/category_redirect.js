$(document).ready(function () {
    console.log("✅ category_redirect.js loaded");

    // Hover to load sets for a category
    $(".category-item").on("mouseenter", function (e) {
        e.preventDefault();

        const categoryId = $(this).data("id");
        const setsMenu = $(`#sets-${categoryId}`);

        // Load only once per hover (to avoid repeated AJAX calls)
        if (setsMenu.children().length === 0) {
            console.log("📡 Fetching sets for category:", categoryId);

            $.ajax({
                url: `/category/${categoryId}/sets/`,
                type: "GET",
                success: function (data) {
                    console.log("✅ Data received: ", data);
                    setsMenu.empty();  // Clear previous sets

                    // For testing purposes, hardcode a set of items
                    setsMenu.append('<li><a class="dropdown-item set-link" href="#">SET_EASY</a></li>');

                    if (data.length === 0) {
                        setsMenu.append('<li><a class="dropdown-item disabled">No sets available</a></li>');
                    } else {
                        data.forEach(set => {
                            setsMenu.append(
                                `<li><a class="dropdown-item set-link" href="/set/${set.id}/">${set.name}</a></li>`
                            );
                        });
                    }
            

                },
                error: function () {
                    setsMenu.empty().append('<li><a class="dropdown-item disabled">Error loading sets</a></li>');
                }
            });
        }
    });

    // Prevent dropdown from closing when a category is clicked
    // Show submenu on hover/click
    $(".category-item").on("mouseenter click", function (e) {
        e.preventDefault();
        const submenu = $(this).next(".dropdown-menu");
        $(".dropdown-menu.show").removeClass("show"); // close others
        submenu.addClass("show"); // show this one
    });


    // ✅ Handle click on a set → navigate
    $(document).on("click", ".set-link", function (e) {
        e.preventDefault();
        const url = $(this).attr("href");
        console.log("➡ Redirecting to set:", url);
        window.location.href = url;  // Force navigation
    });
});
