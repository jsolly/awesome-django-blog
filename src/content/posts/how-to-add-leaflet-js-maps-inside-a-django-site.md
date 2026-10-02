---
slug: how-to-add-leaflet-js-maps-inside-a-django-site
title: "Creating Interactive Maps With Leaflet.js: A Step-by-Step Guide"
category: Geodev
description: "Creating interactive maps with Leaflet.js: A guide to adding plugins, customizing appearance, and more"
draft: false
image: https://d1d7p8ufhgz4ld.cloudfront.net/media/post_metaimgs/leaflet_map_fW6awdh.png
legacyImage: post_metaimgs/leaflet_map_fW6awdh.png
imageAlt: Map of the US showing points in LA, Dallas and NYC.
imageAttribution: ""
imageWidth: 926
imageHeight: 377
published: "2022-06-13T00:16:43Z"
updated: "2022-06-13T00:16:43Z"
author: John Solly
feedAuthor: John_Solly
legacyAuthorId: 2
excerpt: "<p>Creating interactive maps with Leaflet.js: A guide to adding plugins, customizing appearance, and more</p>"
legacyId: 65
related:
  - how-to-implement-subresource-integrity-django
  - smartly-load-CSS-JS-page-load-time
  - migrating-to-ckeditor-5
---

Leaflet.js is an open-source JavaScript library for interactive maps. After copying a couple lines of code into your application, you have full access to the library. I’ve added two plugins, <a target="_blank" rel="noopener noreferrer" href="https://github.com/mad-gooze/Leaflet.Arc">Leaflet.Arc</a> for drawing <a target="_blank" rel="noopener noreferrer" href="https://en.wikipedia.org/wiki/Great-circle_navigation">great circle</a> polylines and <a target="_blank" rel="noopener noreferrer" href="https://github.com/makinacorpus/Leaflet.TextPath">Leaflet.TextPath</a> for displaying text labels above the polylines.

<pre><code class="language-html">// site_analytics.html
{% block head %}
&lt;!-- Leaflet --&gt;
&lt;link rel="stylesheet" href="https://unpkg.com/leaflet@1.8.0/dist/leaflet.css"
  integrity="sha512-hoalWLoI8r4UszCkZ5kL8vayOGVae1oxXe/2A4AO6J9+580uKHDO3JdHb7NzwwzK5xr/Fs0W40kiNHxM9vyTtQ=="
  crossorigin="" /&gt;
&lt;script src="https://unpkg.com/leaflet@1.8.0/dist/leaflet.js"
  integrity="sha512-BB3hKbKWOc9Ez/TAwyWxNXeoV9c1v6FIeYiBieIWkpLjauysF18NzgR1MBNBXf8/KABdlkX68nAhlwcDFLGPCQ=="
  crossorigin=""&gt;&lt;/script&gt;
&lt;!-- Leaflet Plugins --&gt;
{% sri_static 'leaflet_plugins/leaflet.textpath.js' %}
{% sri_static 'leaflet_plugins/leaflet-arc.min.js' %}
{% endblock head %}</code></pre>

I place leaflet.js code in a separate file and inject it into the template underneath a \<div\> tag.

<pre><code class="language-html">// site_analytics.html
&lt;div id="map"&gt;&lt;/div&gt;
{% sri_static 'maps/leaflet_server_map.js' %}</code></pre>

In main.css, I set the map width to 100% of the container and the height to 40% of the viewport.

<pre><code class="language-css">// main.css
#map{ 
  height: 40vh;
  width : 100%;
}</code></pre>

First, I add a map

<pre><code class="language-javascript">// leaflet_map.js
var map = L.map('map', {
    center: [39, -98],
    zoom: 4,
});</code></pre>

Then, a scalebar

<pre><code class="language-javascript">L.control.scale({ imperial: true, metric: true }).addTo(map); </code></pre>

A basemap

<pre><code class="language-javascript">L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 20,
    attribution: '&amp;copy; &lt;a href="https://openstreetmap.org/copyright"&gt;OpenStreetMap contributors&lt;/a&gt;'
}).addTo(map);</code></pre>

Now we have a map centered at the <a target="_blank" rel="noopener noreferrer" href="https://en.wikipedia.org/wiki/Geographic_center_of_the_United_States">geographic center of the US</a>. Next, I add three markers for the cities of Los Angeles, Dallas, and NYC.

<pre><code class="language-javascript">var LaLatLng = { lat: 34.1, lon: -118.2 }
var DallasLatLng = { lat: 32.8, lon: -96.8 }
var NYCLatLng = { lat: 40.7, lon: -73.9 }</code></pre>

For each marker, I include a title and alt text. I wanted to use a custom marker icon for the Dallas marker, so I found one on <a target="_blank" rel="noopener noreferrer" href="https://www.flaticon.com/free-icons/ip-address">Flaticon</a>. After adding the icon png to /static, I reference it from within the JavaScript file.

<pre><code class="language-javascript">var IPAddressIcon = L.icon({
    iconUrl: "static/icons/ip-address.png",
    iconSize: [40, 40]
});
var DallasMarkerOptions = {
    title: "Blogthedata.com Server",
    alt: "The city of Dallas, Texas. USA",
    icon: IPAddressIcon
}</code></pre>

After adding the markers, I add polylines connecting the markers. The Polyline.Arc syntax is leveraging the Leaflet.Arc plugin to draw a great circle route. A plane would take this path when traveling between these locations.

<pre><code class="language-javascript">var DallasToNYC = L.Polyline.Arc([DallasLatLng.lat, DallasLatLng.lon], [NYCLatLng.lat, NYCLatLng.lon], { color: 'orange' })</code></pre>

Next, I want to show the distance between the two cities. I could have hard-coded this, but it was easy enough to do it in the client since I am only performing a couple calculations.

<pre><code class="language-javascript">var DallasToNYCDistance = (Math.floor(map.distance(DallasLatLng, NYCLatLng) / 1000)).toString()</code></pre>

With the distance as a string, I add it to the polyline and then add the polyline to the map.

<pre><code class="language-javascript">DallasToNYC.setText(DallasToNYCDistance.concat(' km'), {
    center: true,
    offset: -5,
    attributes: { 'font-size': '24', 'font-weight': 'bold', fill: 'orange' }
})
DallasToNYC.addTo(map)</code></pre>

And we've got a map!
