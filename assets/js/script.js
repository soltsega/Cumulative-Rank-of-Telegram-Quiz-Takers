document.addEventListener('DOMContentLoaded', () => {
    const tableBody = document.getElementById('tableBody');
    const podiumContainer = document.getElementById('podium');
    const searchInput = document.getElementById('searchInput');
    let leaderboardData = [];

    async function fetchData() {
        if (!podiumContainer && !tableBody) return;

        // Fetch directly from CSV as requested
        const CSV_URL = 'data/cumulative_leaderboard.csv';

        try {
            console.log('Attempting to fetch from CSV...');
            const response = await fetch(CSV_URL);
            if (!response.ok) throw new Error('CSV file not found');
            const csvText = await response.text();
            parseCSV(csvText);
            console.log('Data loaded from CSV');
        } catch (error) {
            console.error('Data source failed:', error);
            if (podiumContainer) {
                podiumContainer.innerHTML = '<div class="error">Unable to load leaderboard data.</div>';
            }
        }
    }

    function parseCSV(csvText) {
        const lines = csvText.trim().split('\n');
        if (lines.length === 0) return;

        const headers = lines[0].split(',');

        leaderboardData = lines.slice(1).map(line => {
            const values = line.split(',');
            const entry = {};
            headers.forEach((header, i) => {
                entry[header.trim()] = values[i] ? values[i].trim() : '';
            });
            return entry;
        });

        if (podiumContainer) renderPodium(leaderboardData.slice(0, 3));
        if (tableBody) renderTable(leaderboardData);
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

    fetchData();
});
