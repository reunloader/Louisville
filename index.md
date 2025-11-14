---
layout: home
title: Live Feed
---

## Near Real-Time Scanner Updates

Live updates from public Louisville Metro safety feeds. Check back often for the latest incidents and responses.

<div class="posts-list">
{% assign counter = 0 %}
{% for post in site.posts %}
  {% unless post.categories contains 'daily-digest' %}
    {% if counter < 150 %}
      <div class="post-card">
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
