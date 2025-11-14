---
layout: page
title: Daily Digest
permalink: /digest/
---

## Daily Scanner Activity Digest

Browse scanner updates organized by date. Each day's incidents and responses are grouped together for easier review.

<div class="date-picker-container">
  <label for="date-picker">Jump to date:</label>
  <input type="date" id="date-picker" class="date-picker-input">
  <button id="today-btn" class="today-button">Today</button>
  <button id="show-all-btn" class="show-all-button">Show All</button>
</div>

<div id="digest-container">
{% assign posts_by_date = site.posts | group_by_exp: "post", "post.date | date: '%Y-%m-%d'" %}

{% for date_group in posts_by_date %}
<div class="daily-digest">
  <h3>{{ date_group.name | date: "%B %-d, %Y" }}</h3>
  <p class="update-count">{{ date_group.items | size }} updates</p>

  <details>
    <summary>View {{ date_group.items | size }} updates from this day</summary>

    <div class="digest-content">
    {% for post in date_group.items %}
      <div class="digest-item">
        <span class="post-time">{{ post.date | date: "%I:%M %p" }}</span>
        <div class="digest-post-content">
          {{ post.content | strip_html | truncatewords: 50 }}
        </div>
      </div>
      {% unless forloop.last %}
      <hr style="margin: 10px 0; border-top: 1px dotted #ddd;">
      {% endunless %}
    {% endfor %}
    </div>
  </details>
</div>

<hr style="margin: 30px 0; border-top: 2px solid #ccc;">
{% endfor %}
</div>

<style>
.date-picker-container {
  background: #f5f5f5;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 30px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.date-picker-container label {
  font-weight: 600;
  color: #333;
  margin-right: 5px;
}

.date-picker-input {
  padding: 8px 12px;
  border: 2px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  background: white;
  flex: 1;
  min-width: 150px;
  max-width: 200px;
}

.today-button, .show-all-button {
  padding: 8px 16px;
  background: #0066cc;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: background 0.2s;
}

.show-all-button {
  background: #666;
}

.today-button:hover {
  background: #0052a3;
}

.show-all-button:hover {
  background: #444;
}

.today-button:active, .show-all-button:active {
  transform: scale(0.98);
}

.daily-digest {
  transition: opacity 0.3s ease;
}

.daily-digest.hidden {
  display: none;
}

.daily-digest.highlight {
  background: #fffacd;
  padding: 15px;
  border-radius: 8px;
  margin: -15px;
  margin-bottom: 15px;
}

/* Mobile optimization */
@media (max-width: 600px) {
  .date-picker-container {
    flex-direction: column;
    align-items: stretch;
  }

  .date-picker-input {
    max-width: 100%;
    width: 100%;
  }

  .today-button, .show-all-button {
    width: 100%;
    padding: 12px;
  }
}
</style>

<script>
document.addEventListener('DOMContentLoaded', function() {
  const datePicker = document.getElementById('date-picker');
  const todayBtn = document.getElementById('today-btn');
  const showAllBtn = document.getElementById('show-all-btn');
  const dailyDigests = document.querySelectorAll('.daily-digest');

  // Extract dates from the page
  const availableDates = new Map();
  dailyDigests.forEach(digest => {
    const h3 = digest.querySelector('h3');
    if (h3) {
      const dateText = h3.textContent.trim();
      const dateObj = new Date(dateText);
      const isoDate = formatDateToISO(dateObj);
      availableDates.set(isoDate, digest);
    }
  });

  // Set min and max dates for picker
  const dates = Array.from(availableDates.keys()).sort();
  if (dates.length > 0) {
    datePicker.min = dates[dates.length - 1];
    datePicker.max = dates[0];
  }

  // Format date to YYYY-MM-DD
  function formatDateToISO(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }

  // Show only selected date
  function showDate(selectedDate) {
    let found = false;
    dailyDigests.forEach(digest => {
      const h3 = digest.querySelector('h3');
      if (h3) {
        const dateText = h3.textContent.trim();
        const dateObj = new Date(dateText);
        const isoDate = formatDateToISO(dateObj);

        if (isoDate === selectedDate) {
          digest.classList.remove('hidden');
          digest.classList.add('highlight');
          found = true;
          // Scroll to the highlighted date
          setTimeout(() => {
            digest.scrollIntoView({ behavior: 'smooth', block: 'start' });
          }, 100);
        } else {
          digest.classList.add('hidden');
          digest.classList.remove('highlight');
        }
      }
    });

    if (!found) {
      alert('No posts found for the selected date.');
      showAll();
    }
  }

  // Show all dates
  function showAll() {
    dailyDigests.forEach(digest => {
      digest.classList.remove('hidden');
      digest.classList.remove('highlight');
    });
    datePicker.value = '';
  }

  // Event listeners
  datePicker.addEventListener('change', function() {
    if (this.value) {
      showDate(this.value);
    } else {
      showAll();
    }
  });

  todayBtn.addEventListener('click', function() {
    const today = formatDateToISO(new Date());
    datePicker.value = today;
    showDate(today);
  });

  showAllBtn.addEventListener('click', function() {
    showAll();
  });
});
</script>
