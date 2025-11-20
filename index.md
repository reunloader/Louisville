---
layout: home
title: Live Feed
---

<style>
  .post-card {
    margin-bottom: 20px;
  }

  .inline-location-link {
    color: #2A81CB;
    text-decoration: underline;
    text-decoration-style: dotted;
    text-decoration-thickness: 1px;
    text-underline-offset: 2px;
    cursor: pointer;
    transition: all 0.2s;
  }

  .inline-location-link:hover {
    color: #1a5a8a;
    text-decoration-style: solid;
    text-decoration-thickness: 2px;
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

        <div class="post-content">
          {{ post.content }}
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

  // Extract addresses and their positions from content
  function findAddressesInContent(content) {
    const found = [];

    // Pattern 1: "block of Street Name" (e.g., "2400 block of Broadway")
    const blockPattern = /(\d+\s+block\s+of\s+[^–\n,.]+?)(?=\s*[,.]|\s*–|\s*\n|$)/gi;

    // Pattern 2: "Street and Street" intersections
    const intersectionPattern = /([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Parkway|Pky|Lane|Ln))\s+and\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Parkway|Pky|Lane|Ln))/gi;

    // Pattern 3: Full addresses (e.g., "4512 Tray Place")
    const fullAddressPattern = /\b(\d+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Place|Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Parkway|Pky|Lane|Ln))\b/g;

    let match;

    // Find block addresses
    while ((match = blockPattern.exec(content)) !== null) {
      const addressText = match[1].trim();
      const normalizedAddress = addressText + ', Louisville, KY';
      found.push({
        text: addressText,
        normalized: normalizedAddress,
        index: match.index,
        length: addressText.length
      });
    }

    // Reset regex
    blockPattern.lastIndex = 0;
    intersectionPattern.lastIndex = 0;
    fullAddressPattern.lastIndex = 0;

    // Find intersections
    while ((match = intersectionPattern.exec(content)) !== null) {
      const addressText = match[0].trim();
      const normalizedAddress = addressText + ', Louisville, KY';
      // Check if we haven't already found this position
      if (!found.some(f => Math.abs(f.index - match.index) < 5)) {
        found.push({
          text: addressText,
          normalized: normalizedAddress,
          index: match.index,
          length: addressText.length
        });
      }
    }

    intersectionPattern.lastIndex = 0;

    // Find full addresses
    while ((match = fullAddressPattern.exec(content)) !== null) {
      const addressText = match[1].trim();
      const normalizedAddress = addressText + ', Louisville, KY';
      // Check if we haven't already found this position
      if (!found.some(f => Math.abs(f.index - match.index) < 5)) {
        found.push({
          text: addressText,
          normalized: normalizedAddress,
          index: match.index,
          length: addressText.length
        });
      }
    }

    // Sort by index (position in text)
    found.sort((a, b) => a.index - b.index);

    return found;
  }

  // Make addresses clickable inline
  function makeAddressesClickable(element) {
    // Get all text nodes
    const walker = document.createTreeWalker(
      element,
      NodeFilter.SHOW_TEXT,
      null,
      false
    );

    const textNodes = [];
    let node;
    while (node = walker.nextNode()) {
      // Skip if parent is already a link or script
      if (node.parentElement && !['A', 'SCRIPT', 'STYLE'].includes(node.parentElement.tagName)) {
        textNodes.push(node);
      }
    }

    // Process each text node
    textNodes.forEach(textNode => {
      const content = textNode.textContent;
      const addresses = findAddressesInContent(content);

      if (addresses.length === 0) return;

      // Check which addresses are geocoded
      const geocodedAddresses_local = addresses.filter(addr => {
        const coords = geocodedAddresses[addr.normalized];
        return coords && coords !== null;
      });

      if (geocodedAddresses_local.length === 0) return;

      // Build replacement HTML
      let html = content;
      let offset = 0;

      // Replace addresses with links (in reverse order to maintain indices)
      geocodedAddresses_local.reverse().forEach(addr => {
        const coords = geocodedAddresses[addr.normalized];
        const mapUrl = `/map/?center=${coords.lat},${coords.lng}&zoom=16`;

        const before = html.substring(0, addr.index);
        const after = html.substring(addr.index + addr.text.length);

        const link = `<a href="${mapUrl}" class="inline-location-link" title="View on map: ${addr.text}">${addr.text}</a>`;

        html = before + link + after;
      });

      // Replace the text node with the new HTML
      const span = document.createElement('span');
      span.innerHTML = html;
      textNode.parentNode.replaceChild(span, textNode);
    });
  }

  // Process all posts
  document.addEventListener('DOMContentLoaded', function() {
    const postContents = document.querySelectorAll('.post-content');

    postContents.forEach(contentEl => {
      makeAddressesClickable(contentEl);
    });
  });
</script>
