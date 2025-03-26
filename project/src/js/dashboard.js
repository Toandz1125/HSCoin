import { API_URL } from './config.js';

document.addEventListener('DOMContentLoaded', async () => {
    const userDetailsDiv = document.getElementById('user-details');
    const donationTableBody = document.getElementById('donation-table').querySelector('tbody');
    const totalCoinsDiv = document.getElementById('total-coins');

    try {
        const token = localStorage.getItem('token');
        if (!token) {
            throw new Error('Bạn phải đăng nhập để xem bảng điều khiển của bạn');
        }

        // Fetch user information
        const userResponse = await fetch(`${API_URL}/user`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        const userData = await userResponse.json();
        if (!userData.success) {
            throw new Error(userData.message);
        }

        // Display user information
        userDetailsDiv.innerHTML = `
            <p><strong>Name:</strong> ${userData.user.name}</p>
            <p><strong>Email:</strong> ${userData.user.email}</p>
        `;
        // Fetch total coins
        const coinsResponse = await fetch(`${API_URL}/user_coins`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        const coinsData = await coinsResponse.json();
        if (coinsData.success) {
            totalCoinsDiv.innerHTML = `<p><strong>Total Coins:</strong> ${coinsData.coins}</p> &nbsp <img src="https://res.cloudinary.com/dslsdpxaf/image/upload/v1742269378/p4m25lkmwqquqwrxg2i0.png" alt="Coin Image" class="coin-image"/> `;
        }
        // Fetch donation history
        const donationResponse = await fetch(`${API_URL}/donations`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        const donationData = await donationResponse.json();
        if (!donationData.success) {
            throw new Error(donationData.message);
        }

        donationData.donations.sort((a, b) => new Date(b.date) - new Date(a.date));
        // Populate donation history table
        donationData.donations.forEach(donation => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${new Date(donation.date).toLocaleString()}</td>
                <td>${donation.amount.toFixed(2)}</td>
                <td>${donation.cause}</td>
                <td>${donation.card_number}</td>
                <td>${donation.transaction_id}</td>
            `;
            donationTableBody.appendChild(row);
        });

    } catch (error) {
        userDetailsDiv.innerHTML = `<p class="error">${error.message}</p>`;
        row.innerHTML = `<p class="error">${error.message}</p>`;
    }
});
