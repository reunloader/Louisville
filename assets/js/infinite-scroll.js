/**
 * Infinite Scroll for Derby City Watch Live Feed
 * Loads posts dynamically as user scrolls
 */

(function() {
  'use strict';

  // Configuration
  const POSTS_PER_PAGE = 20;
  const SCROLL_THRESHOLD = 300; // pixels from bottom to trigger load

  // State
  let allPosts = [];
  let currentIndex = 0;
  let isLoading = false;
  let allPostsLoaded = false;

  // DOM elements
  const postsContainer = document.getElementById('posts-list');
  const loadingIndicator = document.getElementById('loading-indicator');

  /**
   * Initialize infinite scroll
   */
  function init() {
    if (!postsContainer) {
      console.error('Posts container not found');
      return;
    }

    // Load the posts JSON feed
    loadPostsFeed();

    // Set up scroll listener
    window.addEventListener('scroll', handleScroll);
  }

  /**
   * Load the posts JSON feed
   */
  function loadPostsFeed() {
    showLoading();

    fetch('/feed.json')
      .then(response => {
        if (!response.ok) {
          throw new Error('Failed to load posts feed');
        }
        return response.json();
      })
      .then(data => {
        allPosts = data.posts;
        console.log(`Loaded ${allPosts.length} posts`);

        // Load initial batch of posts
        loadMorePosts();
      })
      .catch(error => {
        console.error('Error loading posts:', error);
        hideLoading();
        showError('Failed to load posts. Please refresh the page.');
      });
  }

  /**
   * Load the next batch of posts
   */
  function loadMorePosts() {
    if (isLoading || allPostsLoaded) return;

    isLoading = true;
    showLoading();

    // Calculate the range of posts to load
    const endIndex = Math.min(currentIndex + POSTS_PER_PAGE, allPosts.length);
    const postsToLoad = allPosts.slice(currentIndex, endIndex);

    // Render posts
    postsToLoad.forEach(post => {
      renderPost(post);
    });

    currentIndex = endIndex;

    // Check if all posts are loaded
    if (currentIndex >= allPosts.length) {
      allPostsLoaded = true;
      showEndMessage();
    }

    isLoading = false;
    hideLoading();
  }

  /**
   * Render a single post
   */
  function renderPost(post) {
    const postCard = document.createElement('div');
    postCard.className = 'post-card';

    postCard.innerHTML = `
      <span class="post-meta">${escapeHtml(post.date)}</span>
      <h3>${escapeHtml(post.title)}</h3>
      <div class="post-content">
        ${post.content}
      </div>
      <hr style="margin: 25px 0; border-top: 1px dashed #ccc;">
    `;

    postsContainer.appendChild(postCard);
  }

  /**
   * Handle scroll events
   */
  function handleScroll() {
    if (isLoading || allPostsLoaded) return;

    // Calculate distance from bottom
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    const windowHeight = window.innerHeight;
    const documentHeight = document.documentElement.scrollHeight;
    const distanceFromBottom = documentHeight - (scrollTop + windowHeight);

    // Load more posts if near bottom
    if (distanceFromBottom < SCROLL_THRESHOLD) {
      loadMorePosts();
    }
  }

  /**
   * Show loading indicator
   */
  function showLoading() {
    if (loadingIndicator) {
      loadingIndicator.style.display = 'block';
    }
  }

  /**
   * Hide loading indicator
   */
  function hideLoading() {
    if (loadingIndicator) {
      loadingIndicator.style.display = 'none';
    }
  }

  /**
   * Show error message
   */
  function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.style.cssText = 'padding: 20px; margin: 20px 0; background-color: #fee; border: 1px solid #fcc; border-radius: 4px; color: #c33;';
    errorDiv.textContent = message;
    postsContainer.appendChild(errorDiv);
  }

  /**
   * Show end of posts message
   */
  function showEndMessage() {
    const endDiv = document.createElement('div');
    endDiv.className = 'end-message';
    endDiv.style.cssText = 'padding: 20px; margin: 20px 0; text-align: center; color: #666; font-style: italic;';
    endDiv.textContent = `You've reached the end! All ${allPosts.length} posts loaded.`;
    postsContainer.appendChild(endDiv);
  }

  /**
   * Escape HTML to prevent XSS
   */
  function escapeHtml(text) {
    const map = {
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#039;'
    };
    return String(text).replace(/[&<>"']/g, m => map[m]);
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
