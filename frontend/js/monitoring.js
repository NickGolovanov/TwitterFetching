// Initialize data and state
let allClaims = []
let currentFiltered = []
let map, markerCluster
let refreshInterval = null

// Load data from localStorage or fetch it
async function initializeData() {
	let storedData = localStorage.getItem('allPostInfo')

	if (!storedData) {
		await getAllPosts()
		storedData = localStorage.getItem('allPostInfo')
	}

	console.log('Raw localStorage data:', storedData)

	try {
		let parsedData = JSON.parse(storedData)

		if (Array.isArray(parsedData)) {
			allClaims = parsedData
			currentFiltered = [...allClaims]
			console.log('Extracted posts array:', allClaims)
		} else {
			console.warn('Data exists but is not an array:', parsedData)
		}
	} catch (error) {
		console.error('Error parsing JSON:', error)
	}
}

// Check for new posts and update if needed
async function checkForNewPosts() {
	const previousCount = allClaims.length
	const previousIds = new Set(allClaims.map(claim => claim.id))

	await getAllPosts()
	const storedData = localStorage.getItem('allPostInfo')

	try {
		const parsedData = JSON.parse(storedData)

		if (Array.isArray(parsedData)) {
			// Check if there are new posts
			const hasNewPosts =
				parsedData.length > previousCount ||
				parsedData.some(post => !previousIds.has(post.id))

			if (hasNewPosts) {
				console.log('New posts detected, updating display...')
				allClaims = parsedData

				// Maintain current filter settings
				applySearchFilter()

				// Update filter options with new data
				populateFilterOptions(allClaims)
			}
		}
	} catch (error) {
		console.error('Error checking for new posts:', error)
	}
}

// Format date for display
function formatDate(dateStr) {
	return new Date(dateStr).toLocaleString()
}

// Initialize and configure the map
function setupMap() {
	const mapContainer = document.getElementById('map')
	if (!mapContainer) {
		console.error('Map container not found!')
		return false
	}

	// Define Netherlands boundaries
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

// Update the panel title
function updatePanelTitle(text) {
	const titleElement = document.querySelector('.panel-title')
	if (titleElement) {
		titleElement.textContent = text
	}
}

// Load markers onto the map
function loadMarkers(claims) {
	markerCluster.clearLayers()

	claims.forEach(claim => {
		if (!claim.latitude || !claim.longitude) return

		const marker = L.marker([claim.latitude, claim.longitude])
		marker.bindPopup(`
            <b>${claim.weatherType || 'Unknown'}</b><br>
            ${claim.city || 'Unknown'}<br>
            ${formatDate(claim.dateTime)}
        `)

		marker.on('click', () => {
			const sameLocation = claims.filter(
				c =>
					Math.abs(c.latitude - claim.latitude) < 0.0001 &&
					Math.abs(c.longitude - claim.longitude) < 0.0001
			)

			displayClaims(sameLocation)
			updatePanelTitle(`${sameLocation.length} Claim(s) at This Location`)
		})

		markerCluster.addLayer(marker)
	})
}

// Display claims in the sidebar
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
            <strong>Date/Time:</strong> ${formatDate(claim.dateTime)}
        `
		claimsList.appendChild(div)
	})
}

// Populate filter dropdowns with unique values
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

	// Reset dropdowns
	elements.location.innerHTML = "<option value=''>All</option>"
	elements.weather.innerHTML = "<option value=''>All</option>"
	elements.social.innerHTML = "<option value=''>All</option>"

	// Populate dropdowns
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

// Initialize search and filter functionality
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

	// Toggle filter panel
	elements.filterToggleBtn.addEventListener('click', () => {
		elements.filterPanel.classList.toggle('hidden')
	})

	// Apply search/filter
	elements.searchBtn.addEventListener('click', applySearchFilter)
	elements.applyFilterBtn.addEventListener('click', applySearchFilter)

	// Reset filters
	elements.cancelBtn.addEventListener('click', () => {
		// Reset all filter inputs
		document.getElementById('searchInput').value = ''
		document.getElementById('locationFilter').value = ''
		document.getElementById('weatherFilter').value = ''
		document.getElementById('socialFilter').value = ''

		const dateEl = document.getElementById('dateFilter')
		if (dateEl) dateEl.value = ''

		// Reset display
		updatePanelTitle('All Claims')
		currentFiltered = [...allClaims]
		displayClaims(allClaims)
		loadMarkers(allClaims)
	})
}

// Apply search and filter criteria
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

	// Apply text search
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

	// Apply dropdown filters
	if (filters.location)
		filtered = filtered.filter(c => c.city === filters.location)
	if (filters.weather)
		filtered = filtered.filter(c => c.weatherType === filters.weather)
	if (filters.social)
		filtered = filtered.filter(c => c.socialMediaId === filters.social)

	// Apply date filter
	if (filters.date) {
		filtered = filtered.filter(claim => {
			const claimDate = (claim.dateTime || '').split('T')[0]
			return claimDate === filters.date
		})
	}

	// Update display
	currentFiltered = filtered
	updatePanelTitle(`Search results: ${filtered.length} found`)
	displayClaims(filtered)
	loadMarkers(filtered)
}

// Start the auto-refresh timer
function startAutoRefresh() {
	if (refreshInterval) {
		clearInterval(refreshInterval)
	}

	refreshInterval = setInterval(checkForNewPosts, 10000)
	console.log('Auto-refresh started: checking for new posts every 10 seconds')
}

// Main initialization
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
