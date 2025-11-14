---
layout: page
title: Daily Digest
permalink: /digest/
---

## Daily Scanner Activity Digest

Browse scanner updates organized by date. Each day's incidents and responses are grouped together for easier review.

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
