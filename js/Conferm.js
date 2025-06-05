
const paymentImageInput = document.getElementById("paymentImage");
const imageCanvas = document.getElementById("imageCanvas");
const ctx = imageCanvas.getContext("2d");

let base64Image = "";

paymentImageInput.addEventListener("change", function (event) {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function (e) {
        const img = new Image();
        img.onload = function () {
            imageCanvas.width = img.width;
            imageCanvas.height = img.height;
            ctx.drawImage(img, 0, 0);

            // Add payment method text overlay
            ctx.font = "30px Arial";
            ctx.fillStyle = "red";
            ctx.fillText("InstaPay", 20, 40);
            ctx.fillText("@maged.sportclub12", 20, 80);

            imageCanvas.style.display = "block";

            // Convert canvas to base64
            base64Image = imageCanvas.toDataURL("image/png");
        };
        img.src = e.target.result;
    };
    reader.readAsDataURL(file);
});

document.getElementById("confirmButton").addEventListener("click", function () {
    const reservationId = document.getElementById("reservationId").value;
    const stadiumName = document.getElementById("stadiumName").value;
    const reservationDay = document.getElementById("reservationDay").value;
    const reservationDate = document.getElementById("reservationDate").value;
    const reservationTime = document.getElementById("reservationTime").value;
    const additionalTime = document.getElementById("additionalTime").value;
    const mobileNumber = document.getElementById("mobileNumber").value;

    if (!base64Image) {
        alert("Please upload a payment image.");
        return;
    }

    fetch("http://127.0.0.1:5000/confirm", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            reservationId,
            stadiumName,
            reservationDay,
            reservationDate,
            reservationTime,
            additionalTime,
            mobileNumber,
            paymentMethod: "InstaPay",
            paymentName: "@maged.sportclub12",
            paymentImage: base64Image
        })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("message").innerText = data.message;
    })
    .catch(error => console.error("Error:", error));
});
