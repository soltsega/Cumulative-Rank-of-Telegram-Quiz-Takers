document.addEventListener('DOMContentLoaded', () => {
    const tableBody = document.getElementById('tableBody');
    const podiumContainer = document.getElementById('podium');
    const searchInput = document.getElementById('searchInput');
    let leaderboardData = [];

    async function fetchData() {
        try {
            // Using a relative path to the csv
            const response = await fetch('data/cumulative_leaderboard.csv');
            const data = await response.text();
            parseCSV(data);
        } catch (error) {
            console.error('Error fetching data:', error);
            podiumContainer.innerHTML = '<div class="error">Failed to load data. Make sure cumulative_leaderboard.csv exists.</div>';
        }
    }

    function parseCSV(csvText) {
        const lines = csvText.trim().split('\n');
        const headers = lines[0].split(',');

        leaderboardData = lines.slice(1).map(line => {
            const values = line.split(',');
            const entry = {};
            headers.forEach((header, i) => {
                entry[header.trim()] = values[i].trim();
            });
            return entry;
        });

        renderPodium(leaderboardData.slice(0, 3));
        renderTable(leaderboardData);
    }

    function renderPodium(topThree) {
        podiumContainer.innerHTML = '';

        // Reorder for visual podium: 2, 1, 3
        const visualOrder = [topThree[1], topThree[0], topThree[2]];
        const classes = ['second', 'first', 'third'];
        const icons = ['🥈', '🥇', '🥉'];

        visualOrder.forEach((user, index) => {
            if (!user) return;

            const card = document.createElement('div');
            card.className = `podium-card ${classes[index]}`;
            card.innerHTML = `
                <span class="rank-icon">${icons[index]}</span>
                <h3>${user.Username}</h3>
                <div class="score">${parseFloat(user.Final_Score).toFixed(1)}</div>
                <div class="label">Points</div>
                <div class="stats-mini" style="margin-top: 1rem; font-size: 0.8rem; color: #94a3b8;">
                    ${user.Quizzes_Participated} Quizzes | ${parseFloat(user.Avg_Points).toFixed(1)} Acc
                </div>
            `;
            podiumContainer.appendChild(card);
        });
    }

    function renderTable(data) {
        tableBody.innerHTML = '';
        data.forEach(user => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td class="rank-cell">#${user.Rank}</td>
                <td class="user-cell">${user.Username}</td>
                <td class="hide-mobile">${user.Quizzes_Participated}</td>
                <td class="hide-mobile">${parseFloat(user.Avg_Points).toFixed(2)}</td>
                <td class="hide-mobile">${parseFloat(user.Avg_Time).toFixed(1)}s</td>
                <td class="score-cell">${parseFloat(user.Final_Score).toFixed(2)}</td>
            `;
            tableBody.appendChild(row);
        });
    }

    searchInput.addEventListener('input', (e) => {
        const term = e.target.value.toLowerCase();
        const filtered = leaderboardData.filter(user =>
            user.Username.toLowerCase().includes(term) ||
            user.Rank.includes(term)
        );
        renderTable(filtered);
    });

    fetchData();
});
