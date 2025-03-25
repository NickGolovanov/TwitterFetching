const API_URL = 'http://127.0.0.1:5001/alert/'

function createAlertBox() {
	if (document.getElementById('weatherAlertBox')) return

	let alertBox = document.createElement('div')
	alertBox.id = 'weatherAlertBox'

	let alertContent = document.createElement('div')
	alertContent.id = 'alertContent'
	alertContent.innerHTML = '🔄 Checking for alerts...'

	let closeBtn = document.createElement('button')
	closeBtn.id = 'closeAlert'
	closeBtn.innerText = 'CLOSE'

	closeBtn.onclick = () => {
		alertBox.style.display = 'none'
	}

	// Append elements to the alert box
	alertBox.appendChild(alertContent)
	alertBox.appendChild(closeBtn)
	document.body.appendChild(alertBox)
}

// Function to Fetch Alerts and Update the Box
function fetchAlerts() {
	fetch(API_URL + '?timestamp=' + new Date().getTime(), { cache: 'no-store' })
		.then(response => {
			if (!response.ok) {
				throw new Error(`HTTP Error! Status: ${response.status}`)
			}
			return response.json()
		})
		.then(data => {
			console.log('✅ Fetched Alerts:', data)

			if (data.length > 0) {
				// ✅ Sort alerts by newest first
				data.sort((a, b) => new Date(b.date_time) - new Date(a.date_time))

				let latestAlert = data[0] // Always pick the most recent alert
				console.log('📢 Latest Alert (Selected by JS):', latestAlert)

				let alertContent = document.getElementById('alertContent')

				if (!alertContent) {
					console.log('⚠️ Alert box not found. Skipping update.')
					return
				}

				let newAlertMessage = `
                    🚨 <strong>${latestAlert.weather_type} Alert!</strong><br>
                    📍 Location: ${latestAlert.location}<br>
                    📅 Time: ${latestAlert.date_time}
                `

				// ✅ Always update the content even if it's the same
				if (alertContent.innerHTML !== newAlertMessage) {
					alertContent.innerHTML = newAlertMessage
					document.getElementById('weatherAlertBox').style.display = 'block'
					console.log('✅ Alert updated.')
				} else {
					console.log('⚠️ No new alerts detected. Skipping update.')
				}
			} else {
				console.log('⚠️ No alerts found.')
			}
		})
		.catch(error => console.error('❌ Error fetching alerts:', error))
}

setTimeout(() => {
	createAlertBox()
	fetchAlerts()
}, 3000)

setInterval(fetchAlerts, 30000) // Update every 30 seconds
