// document.addEventListener("DOMContentLoaded", () => {
//     const loginForm = document.getElementById("loginForm");

//     loginForm.addEventListener("submit", (event) => {
//         event.preventDefault();

//         const email = document.getElementById("email").value;
//         const password = document.getElementById("password").value;
//         const authButton = document.querySelector(".auth_btn");

//         authButton.textContent = "Logging in...";
//         authButton.disabled = true;

//         setTimeout(() => {
//             if (email === "admin@hotel.com" && password === "admin123") {
//                 window.location.href = "frontpage.html";
//             } else {
//                 showAlert("Invalid email or password.");
//                 authButton.textContent = "Login";
//                 authButton.disabled = false;
//             }
//         }, 1500);
//     });
document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.querySelector(".signinBx form");
    const registerForm = document.querySelector(".signupBx form");
    const forgotPasswordForm = document.querySelector(".forgot-password-form form");

    // Login form submission handler
    loginForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const email = loginForm.querySelector("input[type='email']").value;
        const password = loginForm.querySelector("input[type='password']").value;

        try {
            const response = await fetch("http://127.0.0.1:5000/admin/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password })
            });
            const result = await response.json();

            if (response.ok) {
                window.location.href = result.redirect || "frontpage.html";
            } else {
                showAlert(result.error || "Login failed");
            }
        } catch (error) {
            showAlert("An error occurred: " + error.message);
        }
    });

    // Registration form submission handler
    registerForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const email = registerForm.querySelector("input[placeholder='Email ']").value;
        const password = registerForm.querySelector("input[placeholder=' Password']").value;
        const confirmPassword = registerForm.querySelector("input[placeholder='Confirm Password']").value;

        try {
            const response = await fetch("http://127.0.0.1:5000/admin/register", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password, confirm_password: confirmPassword })
            });
            const result = await response.json();

            if (response.ok) {
                showAlert(result.message || "Registration successful");
                showLoginForm(); // Show login form after successful registration
            } else {
                showAlert(result.error || "Registration failed");
            }
        } catch (error) {
            showAlert("An error occurred: " + error.message);
        }
    });

    // Forgot password form submission handler
    forgotPasswordForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const email = forgotPasswordForm.querySelector("input[placeholder='Email ']").value;
        const newPassword = forgotPasswordForm.querySelector("input[placeholder=' New Password']").value;
        const confirmPassword = forgotPasswordForm.querySelector("input[placeholder='Confirm New Password']").value;

        try {
            const response = await fetch("http://127.0.0.1:5000/admin/forgot-password", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, new_password: newPassword, confirm_password: confirmPassword })
            });
            const result = await response.json();

            if (response.ok) {
                showAlert(result.message || "Password reset successful");
                showLoginForm();
            } else {
                showAlert(result.error || "Password reset failed");
            }
        } catch (error) {
            showAlert("An error occurred: " + error.message);
        }
    });

    // Utility function to show alert modal
    function showAlert(message) {
        const alertOverlay = document.createElement("div");
        const alertBox = document.createElement("div");
        const alertMessage = document.createElement("p");
        const closeButton = document.createElement("button");

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

        alertBox.style.backgroundColor = "#fff";
        alertBox.style.padding = "20px";
        alertBox.style.borderRadius = "8px";
        alertBox.style.boxShadow = "0 4px 8px rgba(0, 0, 0, 0.2)";
        alertBox.style.textAlign = "center";

        alertMessage.textContent = message;
        alertMessage.style.marginBottom = "20px";

        closeButton.textContent = "OK";
        closeButton.style.padding = "10px 20px";
        closeButton.style.backgroundColor = "#007bff";
        closeButton.style.color = "#fff";
        closeButton.style.border = "none";
        closeButton.style.borderRadius = "5px";
        closeButton.style.cursor = "pointer";

        closeButton.addEventListener("click", () => {
            document.body.removeChild(alertOverlay);
        });

        alertBox.appendChild(alertMessage);
        alertBox.appendChild(closeButton);
        alertOverlay.appendChild(alertBox);

        document.body.appendChild(alertOverlay);
    }

    // Utility function to show the login form (if required)
    function showLoginForm() {
        document.querySelector(".signinBx").style.display = "block";
        document.querySelector(".signupBx").style.display = "none";
        document.querySelector(".forgot-password-form").style.display = "none";
    }
});

     // Function to show the login form
  function showLoginForm() {
    const loginForm = document.querySelector('.signinBx');
    const registerForm = document.querySelector('.signupBx');
    loginForm.classList.add('active');
    registerForm.classList.remove('active');
    hideForgotPasswordForm();
  }

  // Function to show the register form
  function showRegisterForm() {
    const loginForm = document.querySelector('.signinBx');
    const registerForm = document.querySelector('.signupBx');
    registerForm.classList.add('active');
    loginForm.classList.remove('active');
    hideForgotPasswordForm();
  }

  // Function to show the Forgot Password form
  function showForgotPasswordForm() {
    const forgotPasswordForm = document.querySelector('.forgot-password-form');
    forgotPasswordForm.style.display = 'block';
    const container = document.querySelector('.container');
    container.style.display = 'none';
  }

  // Function to hide the Forgot Password form
  function hideForgotPasswordForm() {
    const forgotPasswordForm = document.querySelector('.forgot-password-form');
    forgotPasswordForm.style.display = 'none';
    const container = document.querySelector('.container');
    container.style.display = 'flex';
  }

  showLoginForm();
