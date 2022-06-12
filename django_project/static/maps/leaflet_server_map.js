// TODO - Open blogthedataserver popup on map load
// TOOD - Draw lines between cities
// TODO - Make lines great circle routes
// Change Map projection?
// initialize Leaflet
var map = L.map('map', {
    center: [39, -98],
    zoom: 4,
    zoomControl: false,
    dragging: false,
    minZoom: 4,
    maxZoom: 4,
});


// show the scale bar on the lower left corner
L.control.scale({ imperial: true, metric: true }).addTo(map);

// add the OpenStreetMap tiles
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 20,
    attribution: '&copy; <a href="https://openstreetmap.org/copyright">OpenStreetMap contributors</a>'
}).addTo(map);

var LaLatLng = { lat: 34.1, lon: -118.2 }
var DallasLatLng = { lat: 32.8, lon: -96.8 }
var NYCLatLng = { lat: 40.7, lon: -73.9 }

//LA
var LAMarkerOptions = {
    title: "The City of Angels",
    alt: "The city of Los Angels, California. USA",
}
L.marker(LaLatLng, LAMarkerOptions).addTo(map);

// Dallas
var IPAddressIcon = L.icon({
    iconUrl: "static/icons/ip-address.png",
    iconSize: [40, 40]
});

var DallasMarkerOptions = {
    title: "Blogthedata.com Server",
    alt: "The city of Dallas, Texas. USA",
    icon: IPAddressIcon
}
L.marker(DallasLatLng, DallasMarkerOptions).bindPopup('Blogthedata.com server <br> Dallas, TX').addTo(map);

// NYC
var NYCMarkerOptions = {
    title: "The Big Apple",
    alt: "The city of New York, New York. USA",
}
L.marker(NYCLatLng, NYCMarkerOptions).addTo(map);

// LA to Dallas Polyline
var LaToDallasPlyLyn = L.Polyline.Arc([LaLatLng.lat, LaLatLng.lon], [DallasLatLng.lat, DallasLatLng.lon], { interactive: false })
var LaToDallasDistance = (Math.floor(map.distance(LaLatLng, DallasLatLng) / 1000)).toString()

console.log
LaToDallasPlyLyn.setText(LaToDallasDistance.concat(' km'), {
    center: true,
    offset: -5,
    attributes: { 'font-size': '24', 'font-weight': 'bold', fill: '#007DEF' }
})
LaToDallasPlyLyn.addTo(map)


// Dallas to NYC Polyline
var DallasToNYC = L.Polyline.Arc([DallasLatLng.lat, DallasLatLng.lon], [NYCLatLng.lat, NYCLatLng.lon], { color: 'orange', interactive: false })
var DallasToNYCDistance = (Math.floor(map.distance(DallasLatLng, NYCLatLng) / 1000)).toString()

DallasToNYC.setText(DallasToNYCDistance.concat(' km'), {
    center: true,
    offset: -5,
    attributes: { 'font-size': '24', 'font-weight': 'bold', fill: 'orange' }
})

DallasToNYC.addTo(map)