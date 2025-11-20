---
layout: home
title: Live Feed
---

<style>
  .post-card {
    margin-bottom: 20px;
  }

  .location-links {
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid #eee;
    font-size: 14px;
  }

  .location-links strong {
    color: #666;
    margin-right: 8px;
  }

  .location-link {
    display: inline-block;
    margin-right: 12px;
    margin-bottom: 6px;
    color: #2A81CB;
    text-decoration: none;
    padding: 4px 8px;
    border-radius: 4px;
    background: #f0f7ff;
    transition: background 0.2s;
  }

  .location-link:hover {
    background: #d4ebff;
    text-decoration: underline;
  }

  .location-link::before {
    content: "📍 ";
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
        <span class="post-meta">{{ post.date | date: "%B %-d, %Y at %I:%M %p EST" }}</span>
        <h3>{{ post.title }}</h3>

        <div class="post-content" data-content="{{ post.content | strip_html | escape }}">
          {{ post.content }}
        </div>

        <div class="location-links" id="location-links-{{ counter }}"></div>
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

    // Pattern 1: "block of Street Name" (e.g., "2400 block of Broadway")
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

  // Process each post and add clickable location links
  document.addEventListener('DOMContentLoaded', function() {
    const postCards = document.querySelectorAll('.post-card');

    postCards.forEach((card, index) => {
      const contentEl = card.querySelector('.post-content');
      const locationLinksEl = card.querySelector('.location-links');

      if (!contentEl || !locationLinksEl) return;

      // Get the content text
      const content = contentEl.getAttribute('data-content') || contentEl.textContent;

      // Extract addresses
      const addresses = extractAddresses(content);

      if (addresses.length === 0) {
        locationLinksEl.style.display = 'none';
        return;
      }

      // Find all geocoded addresses for this post
      const geocodedLinks = [];

      for (const address of addresses) {
        if (geocodedAddresses[address] && geocodedAddresses[address] !== null) {
          const coords = geocodedAddresses[address];
          const displayAddress = address.replace(', Louisville, KY', '');
          const mapUrl = `/map/?center=${coords.lat},${coords.lng}&zoom=16`;

          geocodedLinks.push({
            address: displayAddress,
            url: mapUrl
          });
        }
      }

      if (geocodedLinks.length > 0) {
        const linksHtml = geocodedLinks.map(link =>
          `<a href="${link.url}" class="location-link" title="View ${link.address} on map">${link.address}</a>`
        ).join('');

        locationLinksEl.innerHTML = `<strong>Location${geocodedLinks.length > 1 ? 's' : ''}:</strong> ${linksHtml}`;
      } else {
        locationLinksEl.style.display = 'none';
      }
    });
  });
</script>
