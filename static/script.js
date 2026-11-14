const form = document.getElementById("search-form");
const button = document.getElementById("search-button");
const emptyState = document.getElementById("empty-state");

async function getWeather() {
    const city = document.getElementById("city").value.trim();
    const message = document.getElementById("message");
    const result = document.getElementById("weather-result");

    message.classList.remove("error");
    if (!city) {
        message.textContent = "Enter a city name to get started.";
        message.classList.add("error");
        document.getElementById("city").focus();
        return;
    }

    button.disabled = true;
    button.textContent = "Searching…";
    message.textContent = "Checking the weather…";
    result.setAttribute("aria-busy", "true");

    try {
        const response = await fetch(`/weather?city=${encodeURIComponent(city)}`);
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || "Unable to fetch weather. Please try again.");

        for (const [id, value] of Object.entries({
            "city-name": data.city,
            "temperature": `${data.temperature}°C`,
            "description": data.description,
            "feels-like": `${data.feels_like}°C`,
            "humidity": `${data.humidity}%`,
            "wind-speed": `${data.wind_speed} km/h`,
            "conditions": data.conditions,
            "summary": data.summary
        })) document.getElementById(id).textContent = value;

        const weather = String(data.description || "").toLowerCase();
        let icon = "🌤️";
        if (weather.includes("thunder")) icon = "⛈️";
        else if (weather.includes("rain") || weather.includes("drizzl")) icon = "🌧️";
        else if (weather.includes("snow")) icon = "❄️";
        else if (weather.includes("cloud")) icon = "☁️";
        else if (weather.includes("clear") || weather.includes("sun")) icon = "☀️";
        else if (weather.includes("fog")) icon = "🌫️";
        document.getElementById("weather-icon").textContent = icon;

        message.textContent = "";
        emptyState.hidden = true;
        result.hidden = false;
    } catch (error) {
        message.textContent = error.message || "Unable to fetch weather. Please try again.";
        message.classList.add("error");
    } finally {
        result.removeAttribute("aria-busy");
        button.disabled = false;
        button.innerHTML = 'Search <span aria-hidden="true">&rarr;</span>';
    }
}

form.addEventListener("submit", (event) => {
    event.preventDefault();
    if (!button.disabled) getWeather();
});
