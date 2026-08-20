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

        priceFilter.value = 'All';

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

    const placeDetails = document.getElementById('place-details');
    const addReviewSection = document.getElementById('add-review');

    if (placeDetails) {
        const placeId = getPlaceIdFromURL();

        if (addReviewSection) {
            if (token) {
                addReviewSection.style.display = 'block';
            } else {
                addReviewSection.style.display = 'none';
            }
        }

        if (placeId) {
            fetchPlaceDetails(token, placeId);
        }
    }

    const reviewForm = document.getElementById('review-form');

    if (
        reviewForm &&
        window.location.pathname.endsWith('add_review.html')
    ) {
        if (!token) {
            window.location.href = 'index.html';
            return;
        }

        const placeId = getPlaceIdFromURL();

        reviewForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            const reviewText =
                document.getElementById('review').value;

            const rating =
                Number(document.getElementById('rating').value);

            await submitReview(
                token,
                placeId,
                reviewText,
                rating,
                reviewForm
            );
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


function getPlaceIdFromURL() {
    const params = new URLSearchParams(window.location.search);

    return params.get('id');
}


async function fetchPlaceDetails(token, placeId) {
    const headers = {};

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(
        `http://127.0.0.1:5005/api/v1/places/${placeId}`,
        {
            method: 'GET',
            headers: headers
        }
    );

    if (response.ok) {
        const place = await response.json();

        displayPlaceDetails(place);
    } else {
        console.error('Failed to fetch place details');
    }
}


function displayPlaceDetails(place) {
    const placeDetails = document.getElementById('place-details');
    const reviewsSection = document.getElementById('reviews');

    const host = place.owner
        ? `${place.owner.first_name} ${place.owner.last_name}`
        : 'Unknown';

    const amenities = place.amenities.length > 0
        ? place.amenities
            .map((amenity) => amenity.name)
            .join(', ')
        : 'None';

    placeDetails.innerHTML = `
        <h1>${place.title}</h1>

        <div class="place-info">
            <p><strong>Host:</strong> ${host}</p>
            <p>
                <strong>Price per night:</strong>
                $${place.price}
            </p>
            <p>
                <strong>Description:</strong>
                ${place.description || 'No description available.'}
            </p>
            <p>
                <strong>Amenities:</strong>
                ${amenities}
            </p>
        </div>
    `;

    reviewsSection.innerHTML = '<h2>Reviews</h2>';

    if (place.reviews.length === 0) {
        const noReviews = document.createElement('p');

        noReviews.textContent = 'No reviews yet.';
        reviewsSection.appendChild(noReviews);
    } else {
        place.reviews.forEach((review) => {
            const reviewCard = document.createElement('div');

            reviewCard.className = 'review-card';

            reviewCard.innerHTML = `
                <p>
                    <strong>Comment:</strong>
                    ${review.text}
                </p>
                <p>
                    <strong>Rating:</strong>
                    ${review.rating}/5
                </p>
            `;

            reviewsSection.appendChild(reviewCard);
        });
    }
}


async function submitReview(
    token,
    placeId,
    reviewText,
    rating,
    reviewForm
) {
    const response = await fetch(
        'http://127.0.0.1:5005/api/v1/reviews/',
        {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                text: reviewText,
                rating: rating,
                place_id: placeId
            })
        }
    );

    if (response.ok) {
        alert('Review submitted successfully!');
        reviewForm.reset();
    } else {
        alert('Failed to submit review');
    }
}