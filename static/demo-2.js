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