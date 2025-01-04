/* Frontend: JavaScript (scripts.js) */
document.addEventListener("DOMContentLoaded", () => {
    console.log("Hotel Management System Initialized");

    // Example: Form Validation
    const reservationForm = document.querySelector(".reservation-form");
    if (reservationForm) {
        reservationForm.addEventListener("submit", (e) => {
            e.preventDefault(); // Prevent default form submission
            alert("Reservation submitted successfully!");
        });
    }

    // Example: Highlight Active Sidebar Link
    const links = document.querySelectorAll(".sidebar ul li a");
    links.forEach((link) => {
        if (link.href === window.location.href) {
            link.classList.add("active");
        }
    });
});
//ID number 
document.addEventListener("DOMContentLoaded", () => {
    console.log("Hotel Management System Initialized");

    const reservationForm = document.querySelector(".reservation-form");
    const contactNumberInput = document.getElementById("contact-number");
    const idProofType = document.getElementById("id-proof");
    const idProofNumberInput = document.getElementById("id-proof-number");

    if (reservationForm) {
        reservationForm.addEventListener("submit", (e) => {
            e.preventDefault();
            alert("Reservation submitted successfully!");
        });
    }

    contactNumberInput.addEventListener("input", () => {
        const value = contactNumberInput.value;
        if (value.length > 10) {
            contactNumberInput.value = value.slice(0, 10);
        }
    });

    idProofType.addEventListener("change", () => {
        idProofNumberInput.value = ""; // Reset the input when ID type changes
        idProofNumberInput.placeholder =
            idProofType.value === "aadhar"
                ? "Enter 12-digit Aadhar number"
                : idProofType.value === "pan"
                ? "Enter 10-digit PAN number" 
                : idProofType.value === "passport"
                ?"Enter 8-digit PAN number" 
                : "Enter ID proof number";
    });

    idProofNumberInput.addEventListener("input", () => {
        const maxLength = idProofType.value === "aadhar" ? 12 : idProofType.value === "pan" ? 10 :idProofType.value === "passport" ? 8 : Infinity;
        const value = idProofNumberInput.value;
        if (value.length > maxLength) {
            idProofNumberInput.value = value.slice(0, maxLength);
        }
    });

    const links = document.querySelectorAll(".sidebar ul li a");
    links.forEach((link) => {
        if (link.href === window.location.href) {
            link.classList.add("active");
        }
    });
});


//reservation table code 
// JavaScript for Reservations Table

// document.addEventListener("DOMContentLoaded", () => {
//     console.log("Reservations Table Initialized");

//     // Add search functionality
//     const searchInput = document.createElement("input");
//     searchInput.type = "text";
//     searchInput.placeholder = "Search Reservations...";
//     searchInput.style.marginBottom = "20px";
//     searchInput.style.padding = "10px";
//     searchInput.style.width = "100%";
//     searchInput.style.boxSizing = "border-box";
//     const tableSection = document.querySelector("section");
//     tableSection.insertBefore(searchInput, tableSection.querySelector("table"));

//     searchInput.addEventListener("input", () => {
//         const filter = searchInput.value.toLowerCase();
//         const rows = document.querySelectorAll("tbody tr");
//         rows.forEach(row => {
//             const rowText = row.textContent.toLowerCase();
//             row.style.display = rowText.includes(filter) ? "" : "none";
//         });
//     });

//     // Add row highlighting
//     const rows = document.querySelectorAll("tbody tr");
//     rows.forEach(row => {
//         row.addEventListener("mouseover", () => {
//             row.style.backgroundColor = "#e9ecef";
//         });
//         row.addEventListener("mouseout", () => {
//             row.style.backgroundColor = "";
//         });
//     });

//     // Add sorting functionality
//     const headers = document.querySelectorAll("thead th");
//     headers.forEach((header, index) => {
//         header.style.cursor = "pointer";
//         header.addEventListener("click", () => {
//             const rowsArray = Array.from(rows);
//             const isAscending = header.classList.toggle("ascending");
//             rowsArray.sort((a, b) => {
//                 const aText = a.children[index].textContent.trim().toLowerCase();
//                 const bText = b.children[index].textContent.trim().toLowerCase();
//                 return isAscending ? aText.localeCompare(bText) : bText.localeCompare(aText);
//             });
//             rowsArray.forEach(row => row.parentNode.appendChild(row));
//         });
//     });

    //Add delete functionality
    // rows.forEach(row => {
    //     const deleteButton = document.createElement("button");
    //     deleteButton.textContent = "Delete";
    //     deleteButton.style.marginLeft = "10px";
    //     deleteButton.style.padding = "5px 10px";
    //     deleteButton.style.backgroundColor = "#dc3545";
    //     deleteButton.style.color = "#fff";
    //     deleteButton.style.border = "none";
    //     deleteButton.style.borderRadius = "5px";
    //     deleteButton.style.cursor = "pointer";

    //     deleteButton.addEventListener("click", () => {
    //         if (confirm("Are you sure you want to delete this reservation?")) {
    //             row.remove();
    //             console.log("Reservation deleted");
    //         }
    //     });

    //     const lastCell = row.lastElementChild;
    //     lastCell.appendChild(deleteButton);
    // });
// });