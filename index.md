---
layout: home
title: Live Feed
---

<style>
  .post-card {
    display: flex;
    gap: 20px;
    margin-bottom: 20px;
  }

  .post-main-content {
    flex: 1;
  }

  .post-map-preview {
    flex-shrink: 0;
    width: 180px;
    height: 180px;
  }

  .map-thumbnail {
    width: 100%;
    height: 100%;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    display: block;
    transition: transform 0.2s, box-shadow 0.2s;
  }

  .map-thumbnail:hover {
    transform: scale(1.05);
    box-shadow: 0 4px 12px rgba(0,0,0,0.25);
  }

  .location-pending {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: #f5f5f5;
    border-radius: 8px;
    border: 2px dashed #ccc;
    font-size: 14px;
    color: #666;
    text-align: center;
    padding: 10px;
  }

  .location-pending .icon {
    font-size: 32px;
    margin-bottom: 8px;
  }

  /* Mobile responsive */
  @media screen and (max-width: 768px) {
    .post-card {
      flex-direction: column;
    }

    .post-map-preview {
      width: 100%;
      height: 200px;
      order: -1; /* Show map on top on mobile */
    }
  }
</style>

## Near Real-Time Scanner Updates

Live updates from public Louisville Metro safety feeds. Check back often for the latest incidents and responses.

<div class="posts-list">
{% assign counter = 0 %}
{% for post in site.posts %}
  {% unless post.categories contains 'daily-digest' %}
    {% if counter < 150 %}
      <div class="post-card" data-post-index="{{ counter }}">
        <div class="post-main-content">
          <span class="post-meta">{{ post.date | date: "%B %-d, %Y at %I:%M %p EST" }}</span>
          <h3>{{ post.title }}</h3>

          <div class="post-content" data-content="{{ post.content | strip_html | escape }}">
            {{ post.content }}
          </div>
        </div>

        <div class="post-map-preview" id="map-preview-{{ counter }}">
          <!-- Map preview will be injected here by JavaScript -->
        </div>
      </div>
      <hr style="margin: 25px 0; border-top: 1px dashed #ccc;">
      {% assign counter = counter | plus: 1 %}
    {% endif %}
  {% endunless %}
{% endfor %}
</div>

<script>
  // Inject geocoded addresses data from Jekyll
  const geocodedAddresses = {{ site.data.geocoded_addresses | jsonify }};

  // Extract addresses from event content (same logic as map.html)
  function extractAddresses(content) {
    const addresses = [];

    // Pattern 1: "block of Street Name" (e.g., "100 block of Sears Ave")
    const blockPattern = /(\d+)\s+block\s+of\s+([^–\n,.]+?)(?=\s*[,.]|\s*–|\s*\n|$)/gi;

    // Pattern 2: "Street and Street" intersections
    const intersectionPattern = /([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Parkway|Pky|Lane|Ln))\s+and\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Parkway|Pky|Lane|Ln))/gi;

    // Pattern 3: Full addresses (e.g., "4512 Tray Place")
    const fullAddressPattern = /\b(\d+)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Place|Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Parkway|Pky|Lane|Ln))\b/g;

    let match;

    // Extract block addresses
    while ((match = blockPattern.exec(content)) !== null) {
      addresses.push(`${match[1]} ${match[2].trim()}, Louisville, KY`);
    }

    // Extract intersections
    while ((match = intersectionPattern.exec(content)) !== null) {
      addresses.push(`${match[1].trim()} and ${match[2].trim()}, Louisville, KY`);
    }

    // Extract full addresses (if not already captured)
    while ((match = fullAddressPattern.exec(content)) !== null) {
      const addr = `${match[1]} ${match[2].trim()}, Louisville, KY`;
      if (!addresses.some(a => a.includes(match[2].trim()))) {
        addresses.push(addr);
      }
    }

    return [...new Set(addresses)]; // Remove duplicates
  }

  // Generate static map URL using OpenStreetMap tiles
  function generateStaticMapUrl(lat, lng, zoom = 15) {
    // Using OpenStreetMap Static Map API
    const width = 360;
    const height = 360;
    return `https://staticmap.openstreetmap.de/staticmap.php?center=${lat},${lng}&zoom=${zoom}&size=${width}x${height}&markers=${lat},${lng},red`;
  }

  // Process each post and add map previews
  document.addEventListener('DOMContentLoaded', function() {
    const postCards = document.querySelectorAll('.post-card');

    postCards.forEach((card, index) => {
      const contentEl = card.querySelector('.post-content');
      const mapPreviewEl = card.querySelector('.post-map-preview');

      if (!contentEl || !mapPreviewEl) return;

      // Get the content text
      const content = contentEl.getAttribute('data-content') || contentEl.textContent;

      // Extract addresses
      const addresses = extractAddresses(content);

      if (addresses.length === 0) {
        // No address found
        mapPreviewEl.innerHTML = `
          <div class="location-pending">
            <div class="icon">📍</div>
            <div>No location detected</div>
          </div>
        `;
        return;
      }

      // Try to find coordinates for the first address
      let coords = null;
      let matchedAddress = null;

      for (const address of addresses) {
        if (geocodedAddresses[address] && geocodedAddresses[address] !== null) {
          coords = geocodedAddresses[address];
          matchedAddress = address;
          break;
        }
      }

      if (coords && coords.lat && coords.lng) {
        // We have coordinates! Show map thumbnail
        const mapUrl = `/map/?center=${coords.lat},${coords.lng}&zoom=16`;
        const staticMapUrl = generateStaticMapUrl(coords.lat, coords.lng, 15);

        mapPreviewEl.innerHTML = `
          <a href="${mapUrl}" title="View on interactive map: ${matchedAddress}">
            <img src="${staticMapUrl}"
                 alt="Map preview of ${matchedAddress}"
                 class="map-thumbnail"
                 loading="lazy">
          </a>
        `;
      } else {
        // Address found but not geocoded yet
        const displayAddress = addresses[0].replace(', Louisville, KY', '');
        mapPreviewEl.innerHTML = `
          <div class="location-pending">
            <div class="icon">📍</div>
            <div>${displayAddress}</div>
            <div style="font-size: 11px; margin-top: 5px; opacity: 0.7;">Geocoding pending</div>
          </div>
        `;
      }
    });
  });
</script>
