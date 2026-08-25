const API_BASE_URL = 'http://127.0.0.1:5005/api/v1';

const userNameCache = new Map();


document.addEventListener('DOMContentLoaded', () => {
    const token = getCookie('token');

    updateAuthenticationUI(token);
    setupLoginForm();
    setupIndexPage(token);
    setupPlacePage(token);
    setupReviewPage(token);
});


function getCookie(name) {
    const cookies = document.cookie.split(';');

    for (let cookie of cookies) {
        cookie = cookie.trim();

        if (cookie.startsWith(`${name}=`)) {
            return decodeURIComponent(
                cookie.substring(name.length + 1)
            );
        }
    }

    return null;
}


function updateAuthenticationUI(token) {
    const loginLink = document.getElementById('login-link');

    if (!loginLink) {
        return;
    }

    if (token) {
        loginLink.style.display = 'none';
    } else {
        loginLink.style.display = 'inline-block';
    }
}


function setMessage(elementId, message) {
    const element = document.getElementById(elementId);

    if (element) {
        element.textContent = message;
    }
}


function escapeHTML(value) {
    const text = String(value ?? '');

    return text
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#039;');
}


function formatPrice(value) {
    const price = Number(value);

    if (Number.isNaN(price)) {
        return value;
    }

    if (Number.isInteger(price)) {
        return price.toString();
    }

    return price.toFixed(2);
}


async function readResponse(response) {
    try {
        return await response.json();
    } catch (error) {
        return {};
    }
}


/* Login page */

function setupLoginForm() {
    const loginForm = document.getElementById('login-form');

    if (!loginForm) {
        return;
    }

    loginForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        const email =
            document.getElementById('email').value.trim();

        const password =
            document.getElementById('password').value;

        const submitButton =
            loginForm.querySelector('button[type="submit"]');

        setMessage('login-message', 'Signing in...');

        if (submitButton) {
            submitButton.disabled = true;
        }

        try {
            const response = await fetch(
                `${API_BASE_URL}/auth/login`,
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        email: email,
                        password: password
                    })
                }
            );

            const data = await readResponse(response);

            if (!response.ok) {
                setMessage(
                    'login-message',
                    data.error || 'Invalid email or password.'
                );
                return;
            }

            if (!data.access_token) {
                setMessage(
                    'login-message',
                    'Login succeeded but no token was returned.'
                );
                return;
            }

            document.cookie =
                `token=${encodeURIComponent(data.access_token)}; ` +
                'path=/; SameSite=Lax';

            window.location.href = 'index.html';
        } catch (error) {
            setMessage(
                'login-message',
                'Unable to connect to the HBnB API.'
            );
        } finally {
            if (submitButton) {
                submitButton.disabled = false;
            }
        }
    });
}


/* Index page */

function setupIndexPage(token) {
    const placesList =
        document.getElementById('places-list');

    if (!placesList) {
        return;
    }

    setupPriceFilter();

    setMessage(
        'places-message',
        'Loading available places...'
    );

    fetchPlaces(token);
}


function setupPriceFilter() {
    const priceFilter =
        document.getElementById('price-filter');

    if (!priceFilter) {
        return;
    }

    priceFilter.innerHTML = '';

    const prices = [10, 50, 100, 'All'];

    prices.forEach((price) => {
        const option =
            document.createElement('option');

        option.value = price;
        option.textContent = price;

        priceFilter.appendChild(option);
    });

    priceFilter.value = 'All';

    priceFilter.addEventListener('change', (event) => {
        filterPlaces(event.target.value);
    });
}


async function fetchPlaces(token) {
    const headers = {};

    if (token) {
        headers.Authorization = `Bearer ${token}`;
    }

    try {
        const response = await fetch(
            `${API_BASE_URL}/places/`,
            {
                method: 'GET',
                headers: headers
            }
        );

        const data = await readResponse(response);

        if (!response.ok) {
            setMessage(
                'places-message',
                data.error || 'Unable to load places.'
            );
            return;
        }

        displayPlaces(data);
    } catch (error) {
        setMessage(
            'places-message',
            'Unable to connect to the HBnB API.'
        );
    }
}


function displayPlaces(places) {
    const placesList =
        document.getElementById('places-list');

    if (!placesList) {
        return;
    }

    placesList.innerHTML = '';

    if (!Array.isArray(places) || places.length === 0) {
        setMessage(
            'places-message',
            'No places are currently available.'
        );
        return;
    }

    places.forEach((place) => {
        const placeCard =
            document.createElement('article');

        placeCard.className = 'place-card';
        placeCard.dataset.price = place.price;

        placeCard.innerHTML = `
            <h2>${escapeHTML(place.title)}</h2>
            <p>
                Price per night:
                <strong>
                    $${escapeHTML(formatPrice(place.price))}
                </strong>
            </p>
            <a
                href="place.html?id=${encodeURIComponent(place.id)}"
                class="details-button"
            >
                View Details
            </a>
        `;

        placesList.appendChild(placeCard);
    });

    setMessage('places-message', '');

    const priceFilter =
        document.getElementById('price-filter');

    if (priceFilter) {
        filterPlaces(priceFilter.value);
    }
}


function filterPlaces(selectedPrice) {
    const placeCards =
        document.querySelectorAll('.place-card');

    let visiblePlaces = 0;

    placeCards.forEach((card) => {
        const placePrice =
            Number(card.dataset.price);

        const shouldShow =
            selectedPrice === 'All' ||
            placePrice <= Number(selectedPrice);

        card.style.display = shouldShow ? '' : 'none';

        if (shouldShow) {
            visiblePlaces += 1;
        }
    });

    if (
        placeCards.length > 0 &&
        visiblePlaces === 0
    ) {
        setMessage(
            'places-message',
            'No places match the selected price.'
        );
    } else {
        setMessage('places-message', '');
    }
}


/* Place details page */

function setupPlacePage(token) {
    const placeDetails =
        document.getElementById('place-details');

    if (!placeDetails) {
        return;
    }

    const placeId = getPlaceIdFromURL();

    const addReviewSection =
        document.getElementById('add-review');

    const addReviewLink =
        document.getElementById('add-review-link');

    if (addReviewSection) {
        addReviewSection.hidden = !token;
    }

    if (addReviewLink && placeId) {
        addReviewLink.href =
            `add_review.html?id=${encodeURIComponent(placeId)}`;
    }

    if (!placeId) {
        placeDetails.innerHTML =
            '<p>Invalid place ID.</p>';

        clearReviews();

        if (addReviewSection) {
            addReviewSection.hidden = true;
        }

        return;
    }

    loadPlacePage(token, placeId);
}


function getPlaceIdFromURL() {
    const params =
        new URLSearchParams(window.location.search);

    return params.get('id');
}


async function fetchPlaceDetails(token, placeId) {
    const headers = {};

    if (token) {
        headers.Authorization = `Bearer ${token}`;
    }

    const response = await fetch(
        `${API_BASE_URL}/places/${encodeURIComponent(placeId)}`,
        {
            method: 'GET',
            headers: headers
        }
    );

    const data = await readResponse(response);

    if (!response.ok) {
        throw new Error(
            data.error || 'Unable to load place details.'
        );
    }

    return data;
}


async function loadPlacePage(token, placeId) {
    try {
        const place =
            await fetchPlaceDetails(token, placeId);

        displayPlaceDetails(place);

        await displayReviews(
            Array.isArray(place.reviews)
                ? place.reviews
                : []
        );

        setMessage('place-message', '');
    } catch (error) {
        const placeDetails =
            document.getElementById('place-details');

        if (placeDetails) {
            placeDetails.innerHTML = `
                <p>
                    ${escapeHTML(error.message)}
                </p>
            `;
        }

        clearReviews();

        setMessage(
            'place-message',
            error.message
        );
    }
}


function displayPlaceDetails(place) {
    const placeDetails =
        document.getElementById('place-details');

    if (!placeDetails) {
        return;
    }

    const owner = place.owner
        ? `${place.owner.first_name || ''} ` +
          `${place.owner.last_name || ''}`
        : 'Unknown';

    const amenities =
        Array.isArray(place.amenities) &&
        place.amenities.length > 0
            ? place.amenities
                .map((amenity) => amenity.name)
                .filter(Boolean)
                .join(', ')
            : 'None';

    const description =
        place.description ||
        'No description available.';

    placeDetails.innerHTML = `
        <h1>${escapeHTML(place.title)}</h1>

        <div class="place-info">
            <p>
                <strong>Host:</strong>
                ${escapeHTML(owner.trim())}
            </p>

            <p>
                <strong>Price per night:</strong>
                $${escapeHTML(formatPrice(place.price))}
            </p>

            <p>
                <strong>Description:</strong>
                ${escapeHTML(description)}
            </p>

            <p>
                <strong>Amenities:</strong>
                ${escapeHTML(amenities)}
            </p>
        </div>
    `;
}


function clearReviews() {
    const reviewsSection =
        document.getElementById('reviews');

    if (!reviewsSection) {
        return;
    }

    reviewsSection
        .querySelectorAll(
            '.loading-message, ' +
            '.review-card, ' +
            '.empty-message'
        )
        .forEach((element) => element.remove());
}


async function displayReviews(reviews) {
    const reviewsSection =
        document.getElementById('reviews');

    if (!reviewsSection) {
        return;
    }

    clearReviews();

    if (reviews.length === 0) {
        const noReviews =
            document.createElement('p');

        noReviews.className =
            'empty-message status-message';

        noReviews.textContent =
            'No reviews yet.';

        reviewsSection.appendChild(noReviews);

        return;
    }

    const reviewsWithNames =
        await Promise.all(
            reviews.map(async (review) => {
                let userName =
                    review.user_name || null;

                if (!userName && review.user_id) {
                    userName =
                        await getUserDisplayName(
                            review.user_id
                        );
                }

                return {
                    review: review,
                    userName:
                        userName || 'Unknown user'
                };
            })
        );

    reviewsWithNames.forEach((item) => {
        const reviewCard =
            document.createElement('article');

        reviewCard.className = 'review-card';

        reviewCard.innerHTML = `
            <p>
                <strong>User:</strong>
                ${escapeHTML(item.userName)}
            </p>

            <p>
                <strong>Comment:</strong>
                ${escapeHTML(item.review.text)}
            </p>

            <p>
                <strong>Rating:</strong>
                ${escapeHTML(item.review.rating)}/5
            </p>
        `;

        reviewsSection.appendChild(reviewCard);
    });
}


async function getUserDisplayName(userId) {
    if (userNameCache.has(userId)) {
        return userNameCache.get(userId);
    }

    try {
        const response = await fetch(
            `${API_BASE_URL}/users/${encodeURIComponent(userId)}`
        );

        if (!response.ok) {
            return 'Unknown user';
        }

        const user = await readResponse(response);

        const fullName =
            `${user.first_name || ''} ` +
            `${user.last_name || ''}`;

        const cleanName =
            fullName.trim() || 'Unknown user';

        userNameCache.set(
            userId,
            cleanName
        );

        return cleanName;
    } catch (error) {
        return 'Unknown user';
    }
}


/* Add review page */

function setupReviewPage(token) {
    const reviewForm =
        document.getElementById('review-form');

    if (!reviewForm) {
        return;
    }

    if (!token) {
        window.location.href = 'index.html';
        return;
    }

    const placeId = getPlaceIdFromURL();

    if (!placeId) {
        setMessage(
            'review-message',
            'Invalid place ID.'
        );

        disableReviewForm(reviewForm);
        return;
    }

    prepareReviewPage(token, placeId);

    reviewForm.addEventListener(
        'submit',
        async (event) => {
            event.preventDefault();

            const reviewText =
                document
                    .getElementById('review')
                    .value
                    .trim();

            const rating =
                Number(
                    document.getElementById(
                        'rating'
                    ).value
                );

            if (!reviewText) {
                setMessage(
                    'review-message',
                    'Please enter your review.'
                );
                return;
            }

            if (
                !Number.isInteger(rating) ||
                rating < 1 ||
                rating > 5
            ) {
                setMessage(
                    'review-message',
                    'Please select a rating from 1 to 5.'
                );
                return;
            }

            await submitReview(
                token,
                placeId,
                reviewText,
                rating,
                reviewForm
            );
        }
    );
}


async function prepareReviewPage(token, placeId) {
    const placeName =
        document.getElementById(
            'review-place-name'
        );

    const backLink =
        document.querySelector(
            '.review-form-card .secondary-link'
        );

    if (backLink) {
        backLink.href =
            `place.html?id=${encodeURIComponent(placeId)}`;

        backLink.textContent =
            'Back to place';
    }

    try {
        const place =
            await fetchPlaceDetails(token, placeId);

        if (placeName) {
            placeName.textContent =
                `Reviewing: ${place.title}`;
        }
    } catch (error) {
        if (placeName) {
            placeName.textContent =
                'Unable to load place information.';
        }

        setMessage(
            'review-message',
            error.message
        );
    }
}


function disableReviewForm(reviewForm) {
    const fields =
        reviewForm.querySelectorAll(
            'textarea, select, button'
        );

    fields.forEach((field) => {
        field.disabled = true;
    });
}


async function submitReview(
    token,
    placeId,
    reviewText,
    rating,
    reviewForm
) {
    const submitButton =
        reviewForm.querySelector(
            'button[type="submit"]'
        );

    if (submitButton) {
        submitButton.disabled = true;
    }

    setMessage(
        'review-message',
        'Submitting your review...'
    );

    try {
        const response = await fetch(
            `${API_BASE_URL}/reviews/`,
            {
                method: 'POST',
                headers: {
                    'Content-Type':
                        'application/json',
                    'Authorization':
                        `Bearer ${token}`
                },
                body: JSON.stringify({
                    text: reviewText,
                    rating: rating,
                    place_id: placeId
                })
            }
        );

        const data = await readResponse(response);

        if (!response.ok) {
            setMessage(
                'review-message',
                data.error ||
                'Failed to submit review.'
            );

            return;
        }

        reviewForm.reset();

        setMessage(
            'review-message',
            'Review submitted successfully!'
        );
    } catch (error) {
        setMessage(
            'review-message',
            'Unable to connect to the HBnB API.'
        );
    } finally {
        if (submitButton) {
            submitButton.disabled = false;
        }
    }
}