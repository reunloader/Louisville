---
layout: page
title: Daily Digest
permalink: /digest/
---

## Scanner Activity Digest

All scanner updates in chronological order. Browse through recent incidents and responses from Louisville Metro public safety feeds.

<div class="digest-list">
{% for post in site.posts %}
  <div class="digest-item">
    <span class="post-meta">{{ post.date | date: "%B %-d, %Y at %I:%M %p EST" }}</span>
    <h3>{{ post.title }}</h3>

    <div class="post-content">
      {{ post.content }}
    </div>
  </div>
  <hr style="margin: 25px 0; border-top: 1px dashed #ccc;">
{% endfor %}
</div>
