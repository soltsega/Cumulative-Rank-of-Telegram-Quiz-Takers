document.addEventListener('DOMContentLoaded', () => {
    const tableBody = document.getElementById('tableBody');
    const podiumContainer = document.getElementById('podium');
    const searchInput = document.getElementById('searchInput');
    let leaderboardData = [];

    async function fetchData() {
        if (!podiumContainer && !tableBody) return;

        const API_URL = 'http://localhost:8000/leaderboard';
        const FALLBACK_URL = 'data/cumulative_leaderboard.csv';

        try {
            console.log('Attempting to fetch from API...');
            const response = await fetch(API_URL);
            if (!response.ok) throw new Error('API not available');
            const data = await response.json();
            console.log('Data loaded from API');
            leaderboardData = data;
            if (podiumContainer) renderPodium(leaderboardData.slice(0, 3));
            if (tableBody) renderTable(leaderboardData);
        } catch (apiError) {
            console.warn('API fetch failed, falling back to CSV:', apiError);
            try {
                const response = await fetch(FALLBACK_URL);
                const data = await response.text();
                parseCSV(data);
                console.log('Data loaded from fallback CSV');
            } catch (csvError) {
                console.error('All data sources failed:', csvError);
                if (podiumContainer) {
                    podiumContainer.innerHTML = '<div class="error">Failed to load data from any source.</div>';
                }
            }
        }
    }

    function parseCSV(csvText) {
        const lines = csvText.trim().split('\n');
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
        // ... (rest of the visual order logic)
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

    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const term = e.target.value.toLowerCase();
            const filtered = leaderboardData.filter(user =>
                user.Username.toLowerCase().includes(term) ||
                user.Rank.includes(term)
            );
            renderTable(filtered);
        });
    }

    fetchData();
});
