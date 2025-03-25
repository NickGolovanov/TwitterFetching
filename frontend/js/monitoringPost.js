// Initialize data and state
let allPosts = []
let map, markerCluster

// Format date for display
function formatDate(dateStr) {
	return new Date(dateStr).toLocaleString()
}

// Initialize data from localStorage
async function initializeData() {
	let storedData = localStorage.getItem('hashedPostInfo')
	console.log('Retrieved hashedPostInfo from localStorage:', storedData)

	try {
		let parsedData = JSON.parse(storedData)

		if (Array.isArray(parsedData)) {
			allPosts = parsedData
			console.log('Final posts array:', allPosts)
			return true
		} else {
			console.warn('Unexpected format for hashedPostInfo:', parsedData)
			return false
		}
	} catch (error) {
		console.error('Error parsing JSON:', error)
		return false
	}
}

// Display error message
function showErrorMessage(message) {
	const errorDiv = document.createElement('div')
	errorDiv.id = 'error-message'
	errorDiv.textContent = message
	Object.assign(errorDiv.style, {
		position: 'fixed',
		top: '50%',
		left: '50%',
		transform: 'translate(-50%, -50%)',
		backgroundColor: 'red',
		color: 'white',
		padding: '20px',
		fontSize: '18px',
		borderRadius: '8px',
		textAlign: 'center',
		zIndex: '1000',
		boxShadow: '0px 4px 6px rgba(0, 0, 0, 0.1)',
	})
	document.body.appendChild(errorDiv)
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
	return true
}

// Load markers onto the map
function loadMarkers(posts) {
	if (!posts || posts.length === 0) {
		showErrorMessage('No posts available to display')
		if (document.getElementById('map')) {
			document.getElementById('map').style.display = 'none'
		}
		return
	}

	markerCluster.clearLayers()
	let validMarkerCount = 0

	posts.forEach(post => {
		if (!post.latitude || !post.longitude) return

		const marker = L.marker([post.latitude, post.longitude])
		marker.bindPopup(`
            <b>${post.weatherType || 'Unknown'}</b><br>
            ${post.city || 'Unknown'}<br>
            ${formatDate(post.dateTime)}
        `)

		markerCluster.addLayer(marker)
		validMarkerCount++
	})

	if (validMarkerCount === 0) {
		showErrorMessage('No valid coordinates found in posts')
		document.getElementById('map').style.display = 'none'
		return
	}

	// Set appropriate view based on number of markers
	setTimeout(() => {
		if (validMarkerCount === 1 && posts.length === 1) {
			const post = posts[0]
			map.setView([post.latitude, post.longitude], 13)
		} else {
			map.fitBounds(markerCluster.getBounds(), {
				maxZoom: 14,
				padding: [50, 50],
			})
		}
	}, 200)
}

// Main initialization
window.addEventListener('DOMContentLoaded', async () => {
	const dataInitialized = await initializeData()

	if (!dataInitialized || !allPosts || allPosts.length === 0) {
		showErrorMessage('Invalid or empty data')
		if (document.getElementById('map')) {
			document.getElementById('map').style.display = 'none'
		}
		return
	}

	if (setupMap()) {
		loadMarkers(allPosts)
	}
})
