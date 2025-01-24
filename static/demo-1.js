// Appointment Data
const appointments = [
    {
        date: "2025-01-25",
        time: "2:00 PM",
        reason: "Routine Check-up"
    }
];

// Generate the Calendar
function generateCalendar(year, month) {
    const calendarBody = document.getElementById("calendarBody");
    calendarBody.innerHTML = ""; // Clear previous calendar

    const firstDay = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();

    let date = 1;

    // Create rows for weeks
    for (let i = 0; i < 6; i++) {
        const row = document.createElement("tr");

        for (let j = 0; j < 7; j++) {
            const cell = document.createElement("td");
            cell.classList.add("calendar-cell");

            if (i === 0 && j < firstDay) {
                cell.innerHTML = ""; // Empty cells before first day
            } else if (date > daysInMonth) {
                break; // Stop if all days are added
            } else {
                cell.innerHTML = date;

                // Check if the date has an appointment
                const appointment = appointments.find(app => {
                    const appDate = new Date(app.date);
                    return (
                        appDate.getFullYear() === year &&
                        appDate.getMonth() === month &&
                        appDate.getDate() === date
                    );
                });

                if (appointment) {
                    cell.classList.add("appointment-day");
                    cell.title = `${appointment.time} - ${appointment.reason}`;
                    cell.addEventListener("click", () => {
                        document.getElementById("appointmentDetails").innerHTML = `
                            <strong>Appointment:</strong> ${appointment.date}, ${appointment.time} - ${appointment.reason}
                        `;
                    });
                }

                date++;
            }

            row.appendChild(cell);
        }

        calendarBody.appendChild(row);
    }
}

// Initialize the calendar
const today = new Date();
generateCalendar(today.getFullYear(), today.getMonth());

window.onload = function () {
    getLocation(); // Fetch and display the location when the page loads
};

// Function to convert decimal degrees to DMS (Degrees, Minutes, Seconds)
function decimalToDMS(degrees) {
    const d = Math.floor(degrees);
    const m = Math.floor((degrees - d) * 60);
    const s = ((degrees - d - m / 60) * 3600).toFixed(1);
    return { degrees: d, minutes: m, seconds: s };
}

// Function to convert latitude and longitude to DMS format
function convertCoordinates(lat, lon) {
    const latDMS = decimalToDMS(Math.abs(lat));
    const lonDMS = decimalToDMS(Math.abs(lon));
    const latDirection = lat >= 0 ? 'N' : 'S';
    const lonDirection = lon >= 0 ? 'E' : 'W';
    return {
        latitude: `${latDMS.degrees}°${latDMS.minutes}'${latDMS.seconds}"${latDirection}`,
        longitude: `${lonDMS.degrees}°${lonDMS.minutes}'${lonDMS.seconds}"${lonDirection}`
    };
}

// Function to get the current location
function getLocation() {
    const locationDiv = document.getElementById('mapContainer');
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(showPosition, showError);
    } else {
        locationDiv.innerHTML = "Geolocation is not supported by this browser.";
    }
}

// Function to display the position once geolocation is fetched
function showPosition(position) {
    const dmsCoordinates = convertCoordinates(position.coords.latitude, position.coords.longitude);
    const locationDiv = document.getElementById('mapContainer');
    locationDiv.innerHTML = `<iframe
        src="https://www.google.com/maps?q=${position.coords.latitude},${position.coords.longitude}&output=embed"
        width="100%" height="250"
        style="border: 0; border-radius: 6px;"
        allowfullscreen=""
        loading="lazy"
        referrerpolicy="no-referrer-when-downgrade"></iframe>`;
}

// Function to handle errors when geolocation fails
function showError(error) {
    const locationDiv = document.getElementById('mapContainer');
    switch (error.code) {
        case error.PERMISSION_DENIED:
            locationDiv.innerHTML = "Permission denied for Geolocation.";
            break;
        case error.POSITION_UNAVAILABLE:
            locationDiv.innerHTML = "Location information is unavailable.";
            break;
        case error.TIMEOUT:
            locationDiv.innerHTML = "Request timed out.";
            break;
        case error.UNKNOWN_ERROR:
            locationDiv.innerHTML = "An unknown error occurred.";
            break;
    }
}