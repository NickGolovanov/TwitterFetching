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
		console.error('Error fetching data from API:', error)
	}
}
