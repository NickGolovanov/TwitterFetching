let allClaims = []
let currentFiltered = []
let map, markerCluster
let refreshInterval = null

function transformApiItem(item) {
	if (!item || typeof item !== 'object') {
		console.error('Invalid item structure:', item)
		return null
	}

	const displayCity = item?.location?.city || 'Unknown'
	const latLngStr = item?.location?.longitude_latitude || '0,0'
	const [latPart, lngPart] = latLngStr.split(',')

	return {
		id: item?.id || 'UnknownID',
		description: item?.description || 'No description available',
		dateTime: item?.date || new Date().toISOString(),
		city: displayCity,
		latitude: parseFloat(latPart) || 0,
		longitude: parseFloat(lngPart) || 0,
		postId: item?.post_id || 'UnknownPostID',
		severity: item?.severity || 'unknown',
		socialMediaId: item?.social_media_id || 'UnknownSocialMediaID',
		weatherType: item?.weather_type || 'unknown',
		tweetLink: item?.tweet_link || '',
	}
}

async function getAllPosts() {
	try {
		const res = await fetch('http://127.0.0.1:5001/post/')
		const data = await res.json()

		const transformedData = data.map(transformApiItem).filter(Boolean)
		console.log('Transformed Data:', transformedData)

		localStorage.setItem('allPostInfo', JSON.stringify(transformedData))
	} catch (error) {
		console.error('Error fetching data from API:', error)
	}
}

async function getHashedPosts(hash) {
	try {
		const res = await fetch(`http://127.0.0.1:5001/post/rehash/${hash}`)
		const data = await res.json()

		console.log('Fetched Hashed Posts:', data)

		const transformedData = data.map(transformApiItem).filter(Boolean)
		console.log('Transformed Hashed Data:', transformedData)

		localStorage.setItem('hashedPostInfo', JSON.stringify(transformedData))
	} catch (error) {
		console.error('Error fetching hashed data from API:', error)
	}
}

function redirectToAllPosts() {
	window.location.href = 'monitoring.html'
}
function redirectToPost() {
	window.location.href = 'monitoringPost.html'
}

async function initializeData() {
	let storedData = localStorage.getItem('allPostInfo')

	if (!storedData) {
		await getAllPosts()
		storedData = localStorage.getItem('allPostInfo')
	}

	try {
		let parsedData = JSON.parse(storedData)

		if (Array.isArray(parsedData)) {
			allClaims = parsedData
			currentFiltered = [...allClaims]
		} else {
			console.warn('Data exists but is not an array:', parsedData)
		}
	} catch (error) {
		console.error('Error parsing JSON:', error)
	}
}

async function checkForNewPosts() {
	const previousCount = allClaims.length
	const previousIds = new Set(allClaims.map(claim => claim.id))

	await getAllPosts()
	const storedData = localStorage.getItem('allPostInfo')

	try {
		const parsedData = JSON.parse(storedData)

		if (Array.isArray(parsedData)) {
			const hasNewPosts =
				parsedData.length > previousCount ||
				parsedData.some(post => !previousIds.has(post.id))

			if (hasNewPosts) {
				console.log('New posts detected, updating display...')
				allClaims = parsedData

				applySearchFilter()
				populateFilterOptions(allClaims)
			}
		}
	} catch (error) {
		console.error('Error checking for new posts:', error)
	}
}

function formatDate(dateStr) {
	return new Date(dateStr).toLocaleString()
}

function setupMap() {
	const mapContainer = document.getElementById('map')
	if (!mapContainer) {
		console.error('Map container not found!')
		return false
	}

	const southWest = [50.5, 3.2]
	const northEast = [53.7, 7.3]

	map = L.map('map', {
		center: [52.1, 5.3],
		zoom: 7,
		maxBounds: [southWest, northEast],
		maxBoundsViscosity: 1.0,
	})

	L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
		attribution: '&copy; OpenStreetMap contributors',
	}).addTo(map)

	markerCluster = L.markerClusterGroup({
		spiderfyOnEveryZoom: true,
		showCoverageOnHover: false,
	})
	map.addLayer(markerCluster)

	map.on('click', () => {
		updatePanelTitle('All Claims')
		displayClaims(currentFiltered)
	})

	return true
}

function updatePanelTitle(text) {
	const titleElement = document.querySelector('.panel-title')
	if (titleElement) {
		titleElement.textContent = text
	}
}

function loadMarkers(claims) {
  markerCluster.clearLayers();

  claims.forEach(claim => {
    if (!claim.latitude || !claim.longitude) return;

    const marker = L.marker([claim.latitude, claim.longitude]);

    const fallbackContent = `
      <b>${claim.weatherType || 'Unknown'}</b><br>
      ${claim.city || 'Unknown'}<br>
      ${formatDate(claim.dateTime)}
    `;

    let embedHtml = fallbackContent;
    if (claim.tweetLink) {
      embedHtml = `
        <div class="tweet-container">
          <blockquote class="twitter-tweet">
            <p>${claim.description || 'No description available'}</p>
            <a href="${claim.tweetLink.replace('x.com', 'twitter.com')}"></a>
          </blockquote>
        </div>
      `;
    }

    marker.bindPopup(embedHtml);

    marker.on('click', () => {
      const sameLocation = claims.filter(
        c =>
          Math.abs(c.latitude - claim.latitude) < 0.0001 &&
          Math.abs(c.longitude - claim.longitude) < 0.0001
      );

      displayClaims(sameLocation);
      updatePanelTitle(`${sameLocation.length} Claim(s) at This Location`);

      if (claim.tweetLink) {
        setTimeout(() => {
          if (window.twttr && window.twttr.widgets) {
            window.twttr.widgets.load();
          }
        }, 100);
      }
    });

    markerCluster.addLayer(marker);
  });
}


function displayClaims(claimsArray) {
	const claimsList = document.getElementById('claimsList')
	if (!claimsList) {
		console.error('Post list container not found!')
		return
	}

	claimsList.innerHTML = ''

	claimsArray.forEach(claim => {
		const div = document.createElement('div')
		div.className = 'claim-item'
		div.innerHTML = `
      <strong>City:</strong> ${claim.city || 'Unknown'}<br>
      <strong>Weather:</strong> ${claim.weatherType || 'N/A'}<br>
      <strong>Social Media:</strong> ${claim.socialMediaId || 'N/A'}<br>
      <strong>Date/Time:</strong> ${formatDate(claim.dateTime)}<br>
      ${
				claim.tweetLink
					? `<small>Link: <a href="${claim.tweetLink}" target="_blank">${claim.tweetLink}</a></small>`
					: ''
			}
    `
		claimsList.appendChild(div)
	})
}

function populateFilterOptions(claims) {
	const elements = {
		location: document.getElementById('locationFilter'),
		weather: document.getElementById('weatherFilter'),
		social: document.getElementById('socialFilter'),
	}

	if (!elements.location || !elements.weather || !elements.social) {
		console.warn('Filter elements not found; skipping populateFilterOptions.')
		return
	}

	const uniqueValues = {
		locations: [...new Set(claims.map(c => c.city))].filter(Boolean),
		weather: [...new Set(claims.map(c => c.weatherType))].filter(Boolean),
		social: [...new Set(claims.map(c => c.socialMediaId))].filter(Boolean),
	}

	elements.location.innerHTML = "<option value=''>All</option>"
	elements.weather.innerHTML = "<option value=''>All</option>"
	elements.social.innerHTML = "<option value=''>All</option>"

	const populateDropdown = (element, values) => {
		values.forEach(value => {
			const opt = document.createElement('option')
			opt.value = value
			opt.textContent = value
			element.appendChild(opt)
		})
	}

	populateDropdown(elements.location, uniqueValues.locations)
	populateDropdown(elements.weather, uniqueValues.weather)
	populateDropdown(elements.social, uniqueValues.social)
}

function initSearchAndFilter() {
	const elements = {
		searchBtn: document.getElementById('searchBtn'),
		cancelBtn: document.getElementById('cancelBtn'),
		applyFilterBtn: document.getElementById('applyFilterBtn'),
		filterToggleBtn: document.getElementById('filterToggleBtn'),
		filterPanel: document.getElementById('filterPanel'),
	}

	if (!elements.searchBtn || !elements.cancelBtn || !elements.applyFilterBtn) {
		console.warn('Search/filter buttons not found, skipping filter init.')
		return
	}

	elements.filterToggleBtn.addEventListener('click', () => {
		elements.filterPanel.classList.toggle('hidden')
	})

	elements.searchBtn.addEventListener('click', applySearchFilter)
	elements.applyFilterBtn.addEventListener('click', applySearchFilter)

	elements.cancelBtn.addEventListener('click', () => {
		document.getElementById('searchInput').value = ''
		document.getElementById('locationFilter').value = ''
		document.getElementById('weatherFilter').value = ''
		document.getElementById('socialFilter').value = ''

		const dateEl = document.getElementById('dateFilter')
		if (dateEl) dateEl.value = ''

		updatePanelTitle('All Claims')
		currentFiltered = [...allClaims]
		displayClaims(allClaims)
		loadMarkers(allClaims)
	})
}

function applySearchFilter() {
	let filtered = [...allClaims]

	const filters = {
		searchTerm: (
			document.getElementById('searchInput').value || ''
		).toLowerCase(),
		location: document.getElementById('locationFilter').value,
		weather: document.getElementById('weatherFilter').value,
		social: document.getElementById('socialFilter').value,
		date: document.getElementById('dateFilter')?.value || '',
	}

	if (filters.searchTerm) {
		filtered = filtered.filter(claim => {
			const combined = [
				claim.city,
				claim.weatherType,
				claim.socialMediaId,
				claim.dateTime,
			]
				.join(' ')
				.toLowerCase()
			return combined.includes(filters.searchTerm)
		})
	}

	if (filters.location) {
		filtered = filtered.filter(c => c.city === filters.location)
	}

	if (filters.weather) {
		filtered = filtered.filter(c => c.weatherType === filters.weather)
	}

	if (filters.social) {
		filtered = filtered.filter(c => c.socialMediaId === filters.social)
	}

	if (filters.date) {
		filtered = filtered.filter(claim => {
			const claimDate = (claim.dateTime || '').split('T')[0]
			return claimDate === filters.date
		})
	}

	currentFiltered = filtered
	updatePanelTitle(`Search results: ${filtered.length} found`)
	displayClaims(filtered)
	loadMarkers(filtered)
}

function startAutoRefresh() {
	if (refreshInterval) {
		clearInterval(refreshInterval)
	}
	refreshInterval = setInterval(checkForNewPosts, 100000)
	console.log('Auto-refresh started: checking for new posts every 10 seconds')
}

window.addEventListener('DOMContentLoaded', async () => {
	await initializeData()

	if (setupMap()) {
		displayClaims(currentFiltered)
		loadMarkers(currentFiltered)
		populateFilterOptions(allClaims)
		initSearchAndFilter()
		startAutoRefresh()
	}
})
