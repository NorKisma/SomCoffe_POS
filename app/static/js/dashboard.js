document.addEventListener('DOMContentLoaded', function() {
        const ctx = document.getElementById('mainDashboardChart').getContext('2d');
        const gradient = ctx.createLinearGradient(0, 0, 0, 400);
        gradient.addColorStop(0, 'rgba(99, 102, 241, 0.5)');
        gradient.addColorStop(1, 'rgba(99, 102, 241, 0)');

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['01 Mar', '05 Mar', '10 Mar', '15 Mar', '20 Mar', '25 Mar', '30 Mar'],
                datasets: [{
                    label: 'Revenue Growth',
                    data: [35000, 38000, 36000, 42000, 40000, 48000, 45000],
                    borderColor: '#6366f1',
                    borderWidth: 4,
                    pointBackgroundColor: '#ffffff',
                    pointBorderColor: '#6366f1',
                    pointBorderWidth: 2,
                    pointRadius: 6,
                    pointHoverRadius: 8,
                    fill: true,
                    backgroundColor: gradient,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: {
                        grid: { color: 'rgba(255, 255, 255, 0.05)', borderDash: [5, 5] },
                        ticks: { color: '#94a3b8', font: { family: 'Plus Jakarta Sans', weight: 'bold' } }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { color: '#94a3b8', font: { family: 'Plus Jakarta Sans', weight: 'bold' } }
                    }
                }
            }
        });
    });