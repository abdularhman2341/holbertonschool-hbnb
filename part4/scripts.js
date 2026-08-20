document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');

    if (loginForm) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            const response = await fetch(
                'http://127.0.0.1:5005/api/v1/auth/login',
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ email, password })
                }
            );

            if (response.ok) {
                const data = await response.json();

                document.cookie =
                    `token=${data.access_token}; path=/`;

                window.location.href = 'index.html';
            } else {
                alert('Login failed: ' + response.statusText);
            }
        });
    }

    const token = getCookie('token');
    const loginLink = document.getElementById('login-link');

    if (loginLink) {
        if (token) {
            loginLink.style.display = 'none';
        } else {
            loginLink.style.display = 'block';
        }
    }

    const placesList = document.getElementById('places-list');

    if (placesList) {
        fetchPlaces(token);
    }

    const priceFilter = document.getElementById('price-filter');

    if (priceFilter) {
        const prices = [10, 50, 100, 'All'];

        prices.forEach((price) => {
            const option = document.createElement('option');

            option.value = price;
            option.textContent = price;

            priceFilter.appendChild(option);
        });

        priceFilter.addEventListener('change', (event) => {
            const selectedPrice = event.target.value;
            const placeCards =
                document.querySelectorAll('.place-card');

            placeCards.forEach((card) => {
                const price = Number(card.dataset.price);

                if (
                    selectedPrice === 'All' ||
                    price <= Number(selectedPrice)
                ) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }
});


function getCookie(name) {
    const cookies = document.cookie.split(';');

    for (let cookie of cookies) {
        cookie = cookie.trim();

        if (cookie.startsWith(name + '=')) {
            return cookie.substring(name.length + 1);
        }
    }

    return null;
}


async function fetchPlaces(token) {
    const headers = {};

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(
        'http://127.0.0.1:5005/api/v1/places/',
        {
            method: 'GET',
            headers: headers
        }
    );

    if (response.ok) {
        const places = await response.json();

        displayPlaces(places);
    } else {
        console.error('Failed to fetch places');
    }
}


function displayPlaces(places) {
    const placesList = document.getElementById('places-list');

    placesList.innerHTML = '';

    places.forEach((place) => {
        const placeCard = document.createElement('div');

        placeCard.className = 'place-card';
        placeCard.dataset.price = place.price;

        placeCard.innerHTML = `
            <h2>${place.title}</h2>
            <p>Price per night: $${place.price}</p>
            <a href="place.html?id=${place.id}"
               class="details-button">
                View Details
            </a>
        `;

        placesList.appendChild(placeCard);
    });
}