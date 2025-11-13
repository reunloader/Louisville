---
layout: page
title: Daily Digest
permalink: /digest/
---

## Derby City Watch: Daily Digest Archive

Browse daily digest summaries organized by date. Each digest provides a comprehensive overview of the day's significant incidents and community insights.

{% assign digest_posts = site.posts | where: "status", "daily-digest" %}
{% assign posts_by_date = digest_posts | group_by_exp: "post", "post.digest_date" | sort: "name" | reverse %}

{% for date_group in posts_by_date %}
<div class="daily-digest">
  <h3>{{ date_group.name | date: "%B %-d, %Y" }}</h3>

  <div class="digest-content">
    {% for post in date_group.items %}
      <div class="digest-item">
        <div class="digest-post-content">
          {{ post.content }}
        </div>
      </div>
    {% endfor %}
  </div>
</div>

<hr style="margin: 30px 0; border-top: 2px solid #ccc;">
{% endfor %}
