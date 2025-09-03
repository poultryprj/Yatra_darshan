document.addEventListener("DOMContentLoaded", function () {
    const backButton = document.querySelector(".headerButton.goBack");
    if (backButton) {
        backButton.addEventListener("click", function () {
            const loader = document.getElementById("loader");
            if (loader) {
                loader.style.display = "flex";
                setTimeout(() => {
                    loader.style.display = "none";
                }, 5000);
            }
        });
    }
});