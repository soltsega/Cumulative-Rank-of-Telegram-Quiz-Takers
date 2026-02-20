document.addEventListener('DOMContentLoaded', () => {
    const tableBody = document.getElementById('tableBody');
    const podiumContainer = document.getElementById('podium');
    const searchInput = document.getElementById('searchInput');
    let leaderboardData = [];
    let originalData = [];
    let isRefreshing = false;
    let startY = 0;
    let currentY = 0;
    let pullDistance = 0;

    // Mobile detection
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);

    // Show loading state
    function showLoading(element, message = 'Loading...') {
        if (element) {
            element.innerHTML = `<div class="loading">${message}</div>`;
        }
    }

    // Show error state
    function showError(element, message = 'Error loading data') {
        if (element) {
            element.innerHTML = `<div class="error">${message}</div>`;
        }
    }

    // Show success message
    function showSuccess(message) {
        const successDiv = document.createElement('div');
        successDiv.className = 'success';
        successDiv.textContent = message;
        document.body.appendChild(successDiv);

        setTimeout(() => {
            successDiv.remove();
        }, 3000);
    }

    // Haptic feedback (if supported)
    function hapticFeedback() {
        if ('vibrate' in navigator) {
            navigator.vibrate(50);
        }
    }

    // Pull-to-refresh functionality
    function initPullToRefresh() {
        if (!isMobile) return;

        const pullToRefresh = document.createElement('div');
        pullToRefresh.className = 'pull-to-refresh';
        pullToRefresh.innerHTML = '🔄 Pull to refresh';
        document.body.appendChild(pullToRefresh);

        let touchStartY = 0;

        document.addEventListener('touchstart', (e) => {
            if (window.scrollY === 0) {
                touchStartY = e.touches[0].clientY;
                isRefreshing = false;
            }
        }, { passive: true });

        document.addEventListener('touchmove', (e) => {
            if (window.scrollY === 0 && touchStartY > 0) {
                currentY = e.touches[0].clientY;
                pullDistance = currentY - touchStartY;

                if (pullDistance > 0 && pullDistance < 150) {
                    e.preventDefault();
                    pullToRefresh.style.transform = `translateY(${Math.min(pullDistance - 60, 0)}px)`;

                    if (pullDistance > 100) {
                        pullToRefresh.innerHTML = '🔄 Release to refresh';
                        pullToRefresh.classList.add('show');
                    } else {
                        pullToRefresh.innerHTML = '🔄 Pull to refresh';
                        pullToRefresh.classList.remove('show');
                    }
                }
            }
        }, { passive: false });

        document.addEventListener('touchend', () => {
            if (pullDistance > 100 && !isRefreshing) {
                isRefreshing = true;
                pullToRefresh.innerHTML = '🔄 Refreshing...';
                hapticFeedback();
                fetchData();
            }

            setTimeout(() => {
                pullToRefresh.style.transform = 'translateY(-60px)';
                pullToRefresh.classList.remove('show');
                pullDistance = 0;
                isRefreshing = false;
            }, 300);
        }, { passive: true });
    }

    // Mobile menu functionality
    function initMobileMenu() {
        if (!isMobile) return;

        const nav = document.querySelector('nav');
        const mobileMenuBtn = document.createElement('button');
        mobileMenuBtn.className = 'mobile-menu-btn';
        mobileMenuBtn.innerHTML = '<span></span><span></span><span></span>';
        nav.appendChild(mobileMenuBtn);

        mobileMenuBtn.addEventListener('click', () => {
            mobileMenuBtn.classList.toggle('active');
            hapticFeedback();
        });

        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            if (!nav.contains(e.target)) {
                mobileMenuBtn.classList.remove('active');
            }
        });
    }

    // Add touch interactions to cards
    function addTouchInteractions() {
        const cards = document.querySelectorAll('.feature-card, .podium-card, .gospel-card');

        cards.forEach(card => {
            card.addEventListener('touchstart', () => {
                card.style.transform = 'scale(0.98)';
                hapticFeedback();
            }, { passive: true });

            card.addEventListener('touchend', () => {
                setTimeout(() => {
                    card.style.transform = '';
                }, 150);
            }, { passive: true });
        });
    }

    // Smooth scroll for mobile
    function initSmoothScroll() {
        if (!isMobile) return;

        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }

    // Enhanced search with mobile keyboard handling
    function initEnhancedSearch() {
        if (!searchInput) return;

        // Add mobile keyboard optimizations
        searchInput.setAttribute('autocomplete', 'off');
        searchInput.setAttribute('autocorrect', 'off');
        searchInput.setAttribute('autocapitalize', 'off');
        searchInput.setAttribute('spellcheck', 'false');

        // Add clear button
        const clearBtn = document.createElement('button');
        clearBtn.innerHTML = '✕';
        clearBtn.style.cssText = `
            position: absolute;
            right: 3rem;
            top: 50%;
            transform: translateY(-50%);
            background: none;
            border: none;
            color: var(--text-dim);
            font-size: 1.2rem;
            cursor: pointer;
            padding: 0.5rem;
            display: none;
        `;

        const searchBox = searchInput.parentElement;
        searchBox.style.position = 'relative';
        searchBox.appendChild(clearBtn);

        // Show/hide clear button
        searchInput.addEventListener('input', () => {
            clearBtn.style.display = searchInput.value ? 'block' : 'none';
        });

        // Clear functionality
        clearBtn.addEventListener('click', () => {
            searchInput.value = '';
            clearBtn.style.display = 'none';
            searchInput.focus();
            performSearch();
            hapticFeedback();
        });
    }

    // Debounce function for search
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    async function fetchData() {
        if (!podiumContainer && !tableBody) return;

        // Show loading states
        showLoading(podiumContainer, 'Loading top champions...');
        showLoading(tableBody, 'Loading leaderboard data...');

        // Try CSV first, then fallback to API
        const CSV_URL = 'data/cumulative_leaderboard.csv';
        const API_URL = 'http://localhost:8000/leaderboard';

        try {
            console.log('Attempting to fetch from CSV...');
            const response = await fetch(CSV_URL);
            if (!response.ok) throw new Error('CSV file not found');
            const csvText = await response.text();
            parseCSV(csvText);
            console.log('Data loaded from CSV');
        } catch (csvError) {
            console.warn('CSV failed, trying API:', csvError);
            try {
                const response = await fetch(API_URL);
                if (!response.ok) throw new Error('API request failed');
                const data = await response.json();
                if (data.status === 'success' && data.data) {
                    leaderboardData = data.data;
                    originalData = [...leaderboardData];
                    if (podiumContainer) renderPodium(leaderboardData.slice(0, 3));
                    if (tableBody) renderTable(leaderboardData);
                    console.log('Data loaded from API');
                } else {
                    throw new Error('Invalid API response');
                }
            } catch (apiError) {
                console.error('Both data sources failed:', { csvError, apiError });
                showError(podiumContainer, 'Unable to load leaderboard data. Please ensure the data file exists or the API server is running.');
                if (tableBody) {
                    tableBody.innerHTML = '<tr><td colspan="7" class="error">Unable to load data. Check console for details.</td></tr>';
                }
            }
        }
    }

    function parseCSV(csvText) {
        try {
            const lines = csvText.trim().split('\n');
            if (lines.length === 0) {
                throw new Error('Empty CSV file');
            }

            const headers = lines[0].split(',').map(h => h.trim());

            leaderboardData = lines.slice(1)
                .filter(line => line.trim())
                .map(line => {
                    const values = line.split(',');
                    const entry = {};
                    headers.forEach((header, i) => {
                        entry[header] = values[i] ? values[i].trim() : '';
                    });
                    return entry;
                })
                .filter(entry => entry.Username && entry.Rank); // Filter out empty entries

            originalData = [...leaderboardData];

            if (podiumContainer) renderPodium(leaderboardData.slice(0, 3));
            if (tableBody) renderTable(leaderboardData);

            console.log(`Parsed ${leaderboardData.length} entries from CSV`);
        } catch (error) {
            console.error('Error parsing CSV:', error);
            showError(podiumContainer, 'Error parsing data file');
        }
    }

    function renderPodium(topThree) {
        if (!podiumContainer) return;
        podiumContainer.innerHTML = '';

        // Podium visual order: 2nd, 1st, 3rd
        const visualOrder = [topThree[1], topThree[0], topThree[2]];
        const classes = ['second', 'first', 'third'];
        const icons = ['🥈', '🥇', '🥉'];

        visualOrder.forEach((user, index) => {
            if (!user) return;
            const card = document.createElement('div');
            card.className = `podium-card ${classes[index]}`;
            card.innerHTML = `
                <span class="rank-icon">${icons[index]}</span>
                <div class="user-name-wrapper">
                    <h3>${user.Username}</h3>
                </div>
                <div class="score">${parseFloat(user.Final_Score).toFixed(1)}</div>
                <div class="label">Points</div>
                <div class="stats-mini">
                    ${user.Quizzes_Participated} Quizzes | ${parseFloat(user.Avg_Points).toFixed(1)} Acc
                </div>
                <div class="blessing-overlay">
                    <div class="blessing-content">
                        <span class="sparkle">✨</span>
                        <p class="blessing-text">
                            እንኳን ደስ አለህ/አለሽ! <br>
                            እግዚአብሔር ያክብርልን፤ በቤቱ ያጽናልን። በዕውቀት ላይ ዕውቀት፣ በጸጋ ላይ ጸጋ ይጨምርልህ/ሽ።
                        </p>
                        <span class="sparkle">✨</span>
                    </div>
                </div>
            `;
            podiumContainer.appendChild(card);
        });
    }

    function renderTable(data) {
        if (!tableBody) return;
        tableBody.innerHTML = '';
        data.forEach(user => {
            const row = document.createElement('tr');
            row.className = 'rank-row';
            row.innerHTML = `
                <td class="rank-cell">#${user.Rank}</td>
                <td class="user-cell">
                    ${user.Username}
                </td>
                <td class="hide-mobile">${user.Quizzes_Participated}</td>
                <td class="hide-mobile">${parseFloat(user.Avg_Points || 0).toFixed(2)}</td>
                <td class="hide-mobile">${parseFloat(user.Avg_Time || 0).toFixed(1)}s</td>
                <td class="score-cell">${parseFloat(user.Final_Score || 0).toFixed(2)}</td>
                <td class="remark-cell">
                    <span class="click-hint">Click to see...</span>
                    <span class="remark-text">${user.Remark || ''}</span>
                </td>
            `;

            const remarkCell = row.querySelector('.remark-cell');
            remarkCell.addEventListener('click', (e) => {
                const isAlreadyRevealed = remarkCell.classList.contains('revealed');
                document.querySelectorAll('.remark-cell.revealed').forEach(cell => {
                    cell.classList.remove('revealed');
                });
                if (!isAlreadyRevealed) {
                    remarkCell.classList.add('revealed');
                }
            });

            tableBody.appendChild(row);
        });
    }

    // Tab Switching Logic for Resources Page
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    if (tabButtons.length > 0) {
        tabButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const tabId = btn.getAttribute('data-tab');

                // Update buttons
                tabButtons.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');

                // Update content
                tabContents.forEach(content => {
                    content.classList.remove('active');
                    if (content.id === tabId) {
                        content.classList.add('active');
                    }
                });
            });
        });
    }

    // Search functionality with debouncing
    function performSearch() {
        const searchTerm = searchInput.value.toLowerCase().trim();

        if (!searchTerm) {
            leaderboardData = [...originalData];
        } else {
            leaderboardData = originalData.filter(user =>
                user.Username && user.Username.toLowerCase().includes(searchTerm)
            );
        }

        if (podiumContainer) renderPodium(leaderboardData.slice(0, 3));
        if (tableBody) renderTable(leaderboardData);
    }

    // Add search event listener with debouncing
    if (searchInput) {
        const debouncedSearch = debounce(performSearch, 300);
        searchInput.addEventListener('input', debouncedSearch);

        // Add clear button functionality
        searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                searchInput.value = '';
                performSearch();
            }
        });
    }

    // Theme toggle functionality
    function initThemeToggle() {
        const themeToggle = document.createElement('button');
        themeToggle.className = 'theme-toggle';
        themeToggle.setAttribute('aria-label', 'Toggle theme');
        themeToggle.setAttribute('title', 'Switch between light and dark mode');

        // Use SVG icons for a more professional look
        themeToggle.innerHTML = `
            <svg class="icon sun-icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>
            <svg class="icon moon-icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>
        `;

        document.body.appendChild(themeToggle);

        // Load saved theme or detect system preference
        const savedTheme = localStorage.getItem('theme');
        const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        // Default to dark mode for "professional" feel if no preference
        const initialTheme = savedTheme || (systemPrefersDark ? 'dark' : 'dark');

        setTheme(initialTheme);

        // Theme toggle event
        themeToggle.addEventListener('click', () => {
            const currentTheme = document.body.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            setTheme(newTheme);
            hapticFeedback();
        });

        // Listen for system theme changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            if (!localStorage.getItem('theme')) {
                setTheme(e.matches ? 'dark' : 'light');
            }
        });
    }

    function setTheme(theme) {
        document.body.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);

        // Update meta theme-color
        const metaTheme = document.querySelector('meta[name="theme-color"]');
        if (metaTheme) {
            metaTheme.content = theme === 'dark' ? '#022c22' : '#c19b4a';
        }

        // Show animation
        const themeToggle = document.querySelector('.theme-toggle');
        if (themeToggle) {
            themeToggle.style.transform = 'scale(1.2) rotate(360deg)';
            setTimeout(() => {
                themeToggle.style.transform = '';
            }, 300);
        }
    }

    // Initialize mobile features
    initPullToRefresh();
    initMobileMenu();
    addTouchInteractions();
    initSmoothScroll();
    initEnhancedSearch();
    initThemeToggle();

    // Add page visibility API for better performance
    document.addEventListener('visibilitychange', () => {
        if (!document.hidden && isMobile) {
            // Refresh data when page becomes visible
            fetchData();
        }
    });

    // Add online/offline detection
    function updateOnlineStatus() {
        if (navigator.onLine) {
            showSuccess('Connection restored');
            fetchData();
        } else {
            showError(podiumContainer, 'You are offline. Some features may not work.');
        }
    }

    window.addEventListener('online', updateOnlineStatus);
    window.addEventListener('offline', updateOnlineStatus);

    // Initialize with data fetch
    fetchData();
});
