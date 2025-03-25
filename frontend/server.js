const claim = [
    {
        id: 101,
        location: "Emmen, Flintstraat",
        lat: 52.778,
        lng: 6.897,
        weatherType: "Hail",
        windDirection: "ZZV",
        socialMedia: "X",
        dateTime: "2025-10-26T16:04"
    }];

const claims = [
    {
        id: 101,
        location: "Emmen, Flintstraat",
        lat: 52.778,
        lng: 6.897,
        weatherType: "Hail",
        windDirection: "ZZV",
        socialMedia: "X",
        dateTime: "2025-10-26T16:04"
    },
    {
        id: 102,
        location: "Emmen, Flintstraat",
        lat: 52.778,
        lng: 6.897,
        weatherType: "Hail",
        windDirection: "ZZV",
        socialMedia: "X",
        dateTime: "2025-10-26T16:04"
    },
    {
        id: 103,
        location: "Amsterdam",
        lat: 52.3702,
        lng: 4.8952,
        weatherType: "Storm",
        windDirection: "NNE",
        socialMedia: "X",
        dateTime: "2025-10-26T16:10"
    },
    {
        id: 104,
        location: "Enschede, Flintstraat",
        lat: 52.2215,
        lng: 6.8937,
        weatherType: "Rain",
        windDirection: "W",
        socialMedia: "X",
        dateTime: "2025-10-26T16:15"
    },
    {
        id: 105,
        location: "Enschede, Flintstraat",
        lat: 52.2215,
        lng: 6.8937,
        weatherType: "Rain",
        windDirection: "W",
        socialMedia: "X",
        dateTime: "2025-10-26T16:16"
    },
    {
        id: 106,
        location: "Enschede, Flintstraat",
        lat: 52.2215,
        lng: 6.8937,
        weatherType: "Rain",
        windDirection: "W",
        socialMedia: "X",
        dateTime: "2025-10-26T16:17"
    },
    {
        id: 107,
        location: "Rotterdam",
        lat: 51.9244,
        lng: 4.4777,
        weatherType: "Drizzle",
        windDirection: "ESE",
        socialMedia: "X",
        dateTime: "2025-10-26T16:20"
    },
    {
        id: 108,
        location: "Nijmegen",
        lat: 51.8126,
        lng: 5.8372,
        weatherType: "Hail",
        windDirection: "NW",
        socialMedia: "X",
        dateTime: "2025-10-26T16:50"
    }
];

const express = require('express');
const cors = require('cors');
const app = express();

app.use(express.json());
app.use(cors());


app.post('/receive-all-post-data', (req, res) => {
    const receivedData = req.body.receivedHash; // Extracted hashed data
    console.log("Received data from frontend:", receivedData);

    res.json({
        confirmation: "Data received successfully",
        extractedData: JSON.stringify({data: claims}),
        message: "Auto sent from frontend!"
    });
});

app.post('/receive-post-data', (req, res) => {
    const receivedData = req.body.receivedHash; // Extracted hashed data
    console.log("Received data from frontend:", receivedData);

    res.json({
        confirmation: "Data received successfully",
        extractedData: JSON.stringify({data: claim}),
        message: "Auto sent from frontend!"
    });
});

const PORT = 4000;
app.listen(PORT, () => console.log(`Server running on http://localhost:${PORT}`));
