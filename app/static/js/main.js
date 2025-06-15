// Theme Switcher
const themeSwitcher = document.getElementById('theme-switcher');
const html = document.documentElement;

// Infinite Scroll
let isLoading = false;
let page = 1;

// Search with debounce
let searchTimeout;

const loadMoreBtn = document.getElementById('load-more-btn');
const newsGrid = document.querySelector('.news-grid');

// // Check for saved theme preference
// const currentTheme = localStorage.getItem('theme') || 'light';
// html.setAttribute('data-theme', currentTheme);

// themeSwitcher.addEventListener('click', () => {
//   const newTheme = html.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
//   html.setAttribute('data-theme', newTheme);
//   localStorage.setItem('theme', newTheme);
  
//   // Update icon
//   const icon = themeSwitcher.querySelector('i');
//   icon.classList.toggle('fa-moon');
//   icon.classList.toggle('fa-sun');
// });

// // Initialize icon based on current theme
// if (currentTheme === 'dark') {
//   const icon = themeSwitcher.querySelector('i');
//   icon.classList.remove('fa-moon');
//   icon.classList.add('fa-sun');
// }

// Search Functionality
const globalSearch = document.getElementById('global-search');
globalSearch.addEventListener('keyup', (e) => {
  if (e.key === 'Enter') {
    performSearch(globalSearch.value);
  }
});

function performSearch(query) {
  if (query.trim() === '') return;
  
  // Show loading state
  const searchBtn = document.querySelector('.search-btn');
  searchBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
  
  // In a real app, you would make an API call here
  setTimeout(() => {
    window.location.href = `/?custom_query=${encodeURIComponent(query)}`;
    searchBtn.innerHTML = '<i class="fas fa-search"></i>';
  }, 500);
}

// Bookmark Functionality
document.addEventListener('click', (e) => {
  if (e.target.classList.contains('bookmark-btn')) {
    const btn = e.target;
    btn.classList.toggle('active');
    
    // Get article data from parent card
    const card = btn.closest('.news-card');
    const articleId = card.dataset.id;
    
    // Toggle bookmark in localStorage
    toggleBookmark(articleId);
  }
});

function toggleBookmark(articleId) {
  let bookmarks = JSON.parse(localStorage.getItem('bookmarks')) || [];
  
  if (bookmarks.includes(articleId)) {
    bookmarks = bookmarks.filter(id => id !== articleId);
  } else {
    bookmarks.push(articleId);
  }
  
  localStorage.setItem('bookmarks', JSON.stringify(bookmarks));
}

// Initialize bookmarked articles
function initBookmarks() {
  const bookmarks = JSON.parse(localStorage.getItem('bookmarks')) || [];
  bookmarks.forEach(id => {
    const btn = document.querySelector(`.news-card[data-id="${id}"] .bookmark-btn`);
    if (btn) btn.classList.add('active');
  });
}

// Run when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  initBookmarks();
  
  // Lazy load images
  if ('IntersectionObserver' in window) {
    const lazyImages = document.querySelectorAll('img.lazy');
    
    const imageObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target;
          img.src = img.dataset.src;
          img.classList.remove('lazy');
          imageObserver.unobserve(img);
        }
      });
    });
    
    lazyImages.forEach(img => imageObserver.observe(img));
  }
});


async function loadMoreArticles() {
  if (isLoading) return;
  
  isLoading = true;
  loadMoreBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
  
  try {
    const response = await fetch(`/api/articles?page=${page}`);
    const newArticles = await response.json();
    
    if (newArticles.length > 0) {
      // In a real app, you would create DOM elements for new articles
      page++;
      loadMoreBtn.style.display = 'block';
    } else {
      loadMoreBtn.style.display = 'none';
    }
  } catch (error) {
    console.error('Error loading more articles:', error);
  } finally {
    isLoading = false;
    loadMoreBtn.innerHTML = '<i class="fas fa-plus"></i> Load More Stories';
  }
}

// Button click
loadMoreBtn?.addEventListener('click', loadMoreArticles);

// Scroll detection
window.addEventListener('scroll', () => {
  if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 500) {
    loadMoreArticles();
  }
});


globalSearch.addEventListener('input', () => {
  clearTimeout(searchTimeout);
  
  const query = globalSearch.value.trim();
  if (query.length < 3) return;
  
  searchTimeout = setTimeout(() => {
    fetchSearchSuggestions(query);
  }, 300);
});

async function fetchSearchSuggestions(query) {
  try {
    const response = await fetch(`/api/search/suggest?q=${encodeURIComponent(query)}`);
    const suggestions = await response.json();
    
    showSearchSuggestions(suggestions);
  } catch (error) {
    console.error('Error fetching suggestions:', error);
  }
}

function showSearchSuggestions(suggestions) {
  // Implement dropdown UI with suggestions
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
      toast.classList.add('show');
    }, 10);
    
    setTimeout(() => {
      toast.classList.remove('show');
      setTimeout(() => {
        toast.remove();
      }, 300);
    }, 3000);
  }
  

  // Example usage:
  // showToast('Article bookmarked!', 'success')

  document.addEventListener('DOMContentLoaded', function() {
    // Navigation active state management
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // Remove active class from all links
            navLinks.forEach(l => l.classList.remove('active'));
            
            // Add active class to clicked link
            this.classList.add('active');
            
            // Get the target section
            const target = this.getAttribute('data-target');
            
            // In a real app, you would load content for the target section
            console.log('Navigating to:', target);
            
            // For demo purposes, prevent default anchor behavior
            e.preventDefault();
        });
    });
    
    // Update saved articles count
    function updateSavedCount() {
        const savedArticles = JSON.parse(localStorage.getItem('savedArticles')) || [];
        document.querySelector('.saved-count').textContent = savedArticles.length;
    }
    
    // Update trending badge (example)
    function updateTrendingBadge() {
        // In a real app, you would fetch this from your backend
        document.querySelector('.trending-badge').textContent = '3';
    }
    
    // Initialize counts
    updateSavedCount();
    updateTrendingBadge();
    
    // Listen for storage changes (if other tabs modify saved articles)
    window.addEventListener('storage', updateSavedCount);
});


document.addEventListener('DOMContentLoaded', function() {
    // Get elements
    const html = document.documentElement;
    const themeSwitcher = document.getElementById('theme-switcher');
    
    // Check for saved theme preference or system preference
    const savedTheme = localStorage.getItem('theme');
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const currentTheme = savedTheme || (systemPrefersDark ? 'dark' : 'light');
    
    // Apply theme
    function setTheme(theme) {
        html.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        
        // Update icon
        const icon = themeSwitcher.querySelector('i');
        if (icon) {
            icon.className = theme === 'light' ? 'fas fa-sun' : 'fas fa-moon';
        }
        
        // Dispatch custom event
        document.dispatchEvent(new CustomEvent('themeChanged', { detail: theme }));
    }
    
    // Initialize theme
    setTheme(currentTheme);
    
    // Toggle theme on click
    themeSwitcher.addEventListener('click', () => {
        const newTheme = html.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
        setTheme(newTheme);
    });
    
    // Watch for system preference changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
        if (!localStorage.getItem('theme')) { // Only if user hasn't set a preference
            setTheme(e.matches ? 'dark' : 'light');
        }
    });
    
    // Optional: Add animation class during transition
    html.classList.add('theme-transition');
    setTimeout(() => {
        html.classList.remove('theme-transition');
    }, 500);
});




document.addEventListener('DOMContentLoaded', function() {
    // View Toggle Functionality - Corrected Version
    const viewBtns = document.querySelectorAll('.view-btn');
    const gridView = document.getElementById('grid-view');
    const listView = document.getElementById('list-view');
    
    viewBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            // Update active state
            viewBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            // Toggle views - Corrected logic
            if (this.dataset.view === 'grid') {
                gridView.classList.remove('d-none');
                listView.classList.add('d-none');
            } else {
                gridView.classList.add('d-none');
                listView.classList.remove('d-none');
            }
            
            // Save preference
            localStorage.setItem('preferredView', this.dataset.view);
        });
    });
    
    // Load preferred view from localStorage
    const preferredView = localStorage.getItem('preferredView') || 'grid';
    if (preferredView === 'list') {
        document.querySelector('.view-btn[data-view="list"]').click();
    }
});