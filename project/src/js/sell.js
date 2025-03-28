import { API_URL } from './config.js';

document.addEventListener('DOMContentLoaded', function() {
    const paymentAmount = document.getElementById('payment-amount');
    const receiveAmount = document.getElementById('receive-amount');
    const sellCoin = document.getElementById('sell-form');
    const message = document.getElementById('sell-message');
    
    // Exchange rate: 1 HSC = 2,170 VND
    const exchangeRate = 2170;
    
    // Update receive amount when payment amount changes
    paymentAmount.addEventListener('input', function() {
        const amount = parseFloat(this.value.replace(/,/g, '')) || 0;
        const btcAmount = amount * exchangeRate;
        receiveAmount.value = Math.round(btcAmount).toLocaleString('en-US');;
    });
    
    // Update payment amount when receive amount changes
    receiveAmount.addEventListener('input', function() {
        const amount = parseFloat(this.value.replace(/,/g, '')) || 0;
        const vndAmount = amount / exchangeRate;
        paymentAmount.value = vndAmount.toFixed(8);
    });
    
    // Format receive amount with commas
    receiveAmount.addEventListener('blur', function() {
        const amount = parseFloat(this.value.replace(/,/g, '')) || 0;
        this.value = amount.toLocaleString('en-US');
    });
    
    // Sell coin button click handler
    sellCoin.addEventListener('submit', async (e) => {
        e.preventDefault();
        try {
            const token = localStorage.getItem('token');
            if (!token) {
                throw new Error('Bạn phải đăng nhập để mua tiền xu');
            }
            const coin = parseFloat(paymentAmount.value.replace(/,/g, ''))
            const sellcoin = -coin

            const response = await fetch(`${API_URL}/sell_coin`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({amount: sellcoin})
            });

            const data = await response.json();

            if (data.success) {
                message.textContent = 'Đã bán thành công! Số dư tiền xu của bạn đã được cập nhật.';
                message.className = 'message success';
                sellCoin.reset();
                setTimeout(() => {
                    window.location.href = 'dashboard.html';
                }, 1500);
            } else {
                message.textContent = data.message || 'Giao dịch thất bại';
                message.className = 'message error';
                setTimeout(() => {
                    window.location.href = 'dashboard.html';
                }, 1500);
                return;
            }
        } catch (error) {
            message.textContent = error.message;
            message.className = 'message error';
        }
        // Show success message and redirect
        alert(`Cảm ơn sự ủng hộ của bạn! ${paymentAmount.value} HSC vừa được bán. You nhận được ${receiveAmount.value} vnđ.`)
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
