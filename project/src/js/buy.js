import { API_URL } from './config.js';

document.addEventListener('DOMContentLoaded', function() {
    const paymentAmount = document.getElementById('payment-amount');
    const receiveAmount = document.getElementById('receive-amount');
    const buyCoin = document.getElementById('buy-form');
    const message = document.getElementById('buy-message');
    
    // Exchange rate: 1 HSC = 2,170 VND
    const exchangeRate = 2170;
    
    // Update receive amount when payment amount changes
    paymentAmount.addEventListener('input', function() {
        const amount = parseFloat(this.value.replace(/,/g, '')) || 0;
        const btcAmount = amount / exchangeRate;
        receiveAmount.value = btcAmount.toFixed(8);
    });
    
    // Update payment amount when receive amount changes
    receiveAmount.addEventListener('input', function() {
        const amount = parseFloat(this.value) || 0;
        const vndAmount = amount * exchangeRate;
        paymentAmount.value = Math.round(vndAmount).toLocaleString('en-US');
    });
    
    // Format payment amount with commas
    paymentAmount.addEventListener('blur', function() {
        const amount = parseFloat(this.value.replace(/,/g, '')) || 0;
        this.value = amount.toLocaleString('en-US');
    });
    
    // Payment method button click handler
    buyCoin.addEventListener('submit', async (e) => {
        e.preventDefault();
        try {
            const token = localStorage.getItem('token');
            if (!token) {
                throw new Error('You must be logged in to buy coins');
            }

            const response = await fetch(`${API_URL}/buy_coin`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({amount: parseFloat(receiveAmount.value.replace(/,/g, '')) })
            });

            const data = await response.json();

            if (data.success) {
                message.textContent = 'Purchase successful! Your coin balance has been updated.';
                message.className = 'message success';
                buyCoin.reset();
                setTimeout(() => {
                    window.location.href = '/project/src/auth/dashboard.html';
                }, 1500);
            } else {
                throw new Error(data.message || 'Purchase failed');
            }
        } catch (error) {
            message.textContent = error.message;
            message.className = 'message error';
        }
        // Show success message and redirect
        alert(`Thank you for your purchase! ${receiveAmount.value} HSC have been added to your account.`)
        window.location.href = "dashboard.html"
    })

    // Tab switching functionality
    const tabs = document.querySelectorAll(".tab")
    tabs.forEach((tab) => {
        tab.addEventListener("click", function () {
        tabs.forEach((t) => t.classList.remove("active"))
        this.classList.add("active")
        });
    });
});