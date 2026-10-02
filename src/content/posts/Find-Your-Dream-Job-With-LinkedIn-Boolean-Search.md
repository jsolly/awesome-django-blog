---
slug: Find-Your-Dream-Job-With-LinkedIn-Boolean-Search
title: "Finding GIS Jobs With LinkedIn Boolean Search: A Guide"
category: productivity
description: Using the power of LinkedIn Boolean search, you can find GIS jobs tailored to your specific needs. Learn how to use ORs and NOTs to find the perfect job!
draft: false
image: https://d1d7p8ufhgz4ld.cloudfront.net/media/post_metaimgs/LinkedInBooleanSearch.webp
legacyImage: post_metaimgs/LinkedInBooleanSearch.webp
imageAlt: John Solly Headshot
imageAttribution: ""
imageWidth: 521
imageHeight: 594
published: "2022-08-14T19:55:56.533Z"
updated: "2026-09-07T14:25:05.498Z"
author: John Solly
feedAuthor: John_Solly
legacyAuthorId: 2
excerpt: <p>Using the power of LinkedIn Boolean search, you can find GIS jobs tailored to your specific needs. Learn how to use ORs and NOTs to find the perfect job!</p>
legacyId: 98
related:
  - optimizing-ahrefs-orphan-pages-duplicate-content
  - use-brave-search-goggles-to-improve-web-searches
  - my-favorite-youtube-channels-podcasts-newsletters
---

LinkedIn <a target="_blank" rel="noopener noreferrer" href="https://www.linkedin.com/help/linkedin/answer/a524335/using-boolean-search-on-linkedin?lang=en">Boolean Search</a> is my favorite way to find positions. Let's say you want to find 'GIS Developer' positions. If we search for that, there are over 1K results. That's a lot of jobs go through. Perhaps we can make a more targeted search.

<figure class="image"><img src="https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/image_WoJiHcX.png" alt="LinkedIn search for 'GIS Developer' with 1K results"></figure>

## Find Relevant Keywords

The first step is to find the right words to search for. Since I am interested in GIS positions, I found a list of 'GIS buzzwords' in this <a target="_blank" rel="noopener noreferrer" href="https://github.com/HeikkiVesanto/GIS-Buzzwords">Github repo</a>. I then copy/pasted the terms into MS word and did a find/replace on <code>^p</code> (carriage return) with <code>' OR '</code> to get a list of terms separated by ORs. You can learn more about the technique in <a target="_blank" rel="noopener noreferrer" href="https://youtu.be/5-O4R-rvvNk?t=1677">this video</a>.

<a target="_blank" rel="noopener noreferrer" href="https://docs.google.com/document/d/1W00IW9nrX5KK6u9SiTyhvGJPrJkvSl9RDmZLaVMuz9c/edit?usp=sharing">See the full list</a>

Armed with a list of keywords, we can perform more customized searches.

## Show me as many GIS jobs as possible

<code>GIS OR geospatial OR geographic OR spatial OR leaflet OR geoserver OR openlayers OR postgis OR GDAL OR ArcPy OR GeoJSON OR shapefile OR GeoDjango OR esri OR ArcGIS OR mapbox</code> 

(You get the idea...keep appending terms to get more and more results)

<figure class="image"><img src="https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/image_Kfklgyh.png" alt="LinkedIn search result with 129K results"></figure>

Wow, that's a lot of jobs to go through. 128K!

## Show Me Open Source GIS Positions

With our list of ORs, we can start to get creative with our search. What if we want to find open source GIS positions? Ones that include OS software in the title or job description but don't mention enterprise players like Mapbox or Esri.

<code>(leaflet OR geoserver OR openlayers) AND (-(esri OR mapbox))</code>

<figure class="image image-style-align-center"><img src="https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/image_aAfvsLu.png" alt="LinkedIn search for Open Source positions with 485 results"></figure>

## Show Me GIS Jobs That Don't Mention GIS

Many GIS jobs might not even have GIS in them! These are great positions to find because they probably won't be seen by other applications that perform regular searches. Here, I'm searching for jobs that mention popular GIS technologies but don't mention common terms like GIS or Geographic. 

<code>(leaflet OR geoserver OR openlayers) AND (-(gis OR geographic OR geospatial))</code>

<figure class="image image-style-align-center"><img src="https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/image_olZnj0G.png" alt="LinkedIn search for GIS jobs that don't mention GIS. 317 results."></figure>

## Show me Open Source GIS Positions in Austin, TX

Let's go back to the open source example where we had 485 results. This time let's add one of LinkedIn's standard filters on top. A geographic filter of 'Austin, TX.'

<figure class="image"><img src="https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/image_QCrFTvZ.png" alt="LinkedIn search with spatial filter of Austin Texas. 1 result."></figure>

One result! I checked the job description, and it looks like they use Leaflet for visualization. Here's an excerpt from the posting.

<blockquote><p>React and vanilla javascript is our “go-to” with jquery mixed in where it makes sense. Leaflet, D3 and highcharts to make things contextual for our users, we are always exploring new frameworks and libraries to improve our frontend experience.</p></blockquote>

Maybe this is the perfect position for you!

## The Query I Use to Find GIS Jobs 

I want to find companies that use spatial libraries and tools, but I don't wish to see manager or sales positions.

<blockquote><p>(PostGIS OR GeoDjango OR &nbsp;OpenLayers OR Geoserver OR Geonode OR leaflet OR openlayers OR cesium OR folium OR geopandas OR pysal OR gdal OR rasterio OR fiona OR STAC OR geemap OR shapely OR arcpy) AND (-(Manager OR Specialist OR Analyst OR “Product Engineer” OR “Solution Engineer” OR "Sales Engineer" OR “Quality Assurance”))</p></blockquote>

## Conclusion

LinkedIn boolean search is a great way to find positions you might not come across with a standard search. The sky is the limit regarding the different searches you can come up with. Find your needle in the haystack using these powerful search operators!
