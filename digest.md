---
layout: page
title: Daily Digest
permalink: /digest/
---

## Daily Summary Digest

Daily curated summaries of Louisville Metro public safety activity. Each digest provides an overview of the day's most significant incidents and patterns.

<div class="digest-list">
{% for post in site.posts %}
  {% if post.categories contains 'daily-digest' %}
    <div class="digest-item">
      <span class="post-meta">{{ post.date | date: "%B %-d, %Y at %I:%M %p EST" }}</span>
      <h3>{{ post.title }}</h3>

      <div class="post-content">
        {{ post.content }}
      </div>
    </div>
    <hr style="margin: 25px 0; border-top: 1px dashed #ccc;">
  {% endif %}
{% endfor %}
</div>
