document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.getElementById("loginForm");

    loginForm.addEventListener("submit", (event) => {
        event.preventDefault();

        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;
        const authButton = document.querySelector(".auth_btn");

        authButton.textContent = "Logging in...";
        authButton.disabled = true;

        setTimeout(() => {
            if (email === "admin@hotel.com" && password === "admin123") {
                window.location.href = "frontpage.html";
            } else {
                showAlert("Invalid email or password.");
                authButton.textContent = "Login";
                authButton.disabled = false;
            }
        }, 1500);
    });

    function showAlert(message) {
        // Create the modal elements
        const alertOverlay = document.createElement("div");
        const alertBox = document.createElement("div");
        const alertMessage = document.createElement("p");
        const closeButton = document.createElement("button");

        // Style the overlay
        alertOverlay.style.position = "fixed";
        alertOverlay.style.top = 0;
        alertOverlay.style.left = 0;
        alertOverlay.style.width = "100%";
        alertOverlay.style.height = "100%";
        alertOverlay.style.backgroundColor = "rgba(0, 0, 0, 0.5)";
        alertOverlay.style.display = "flex";
        alertOverlay.style.alignItems = "center";
        alertOverlay.style.justifyContent = "center";
        alertOverlay.style.zIndex = 1000;

        // Style the alert box
        alertBox.style.backgroundColor = "#fff";
        alertBox.style.padding = "20px";
        alertBox.style.borderRadius = "8px";
        alertBox.style.boxShadow = "0 4px 8px rgba(0, 0, 0, 0.2)";
        alertBox.style.textAlign = "center";

        // Style the message
        alertMessage.textContent = message;
        alertMessage.style.marginBottom = "20px";

        // Style the close button
        closeButton.textContent = "OK";
        closeButton.style.padding = "10px 20px";
        closeButton.style.backgroundColor = "#007bff";
        closeButton.style.color = "#fff";
        closeButton.style.border = "none";
        closeButton.style.borderRadius = "5px";
        closeButton.style.cursor = "pointer";

        // Add event listener to close button
        closeButton.addEventListener("click", () => {
            document.body.removeChild(alertOverlay);
        });

        // Append elements to the alert box and overlay
        alertBox.appendChild(alertMessage);
        alertBox.appendChild(closeButton);
        alertOverlay.appendChild(alertBox);

        // Add the overlay to the body
        document.body.appendChild(alertOverlay);
    }
});
