function getHashedData() {
	const urlParams = new URLSearchParams(window.location.search)
	return urlParams.get('data') || null
}

async function sendLink() {
	try {
		const hashedInfo = getHashedData()

		console.log('Extracted hashed info:', hashedInfo)

		if (hashedInfo) {
			await getHashedPosts(hashedInfo)

			console.log(
				'Stored hashedPostInfo:',
				localStorage.getItem('hashedPostInfo')
			)

			redirectToPost()
		} else {
			await getAllPosts()

			console.log('Stored allPostInfo:', localStorage.getItem('allPostInfo'))

			redirectToAllPosts()
		}
	} catch (error) {
		console.error('Error:', error)
	}
}

window.addEventListener('DOMContentLoaded', async () => {
	await sendLink()
})
