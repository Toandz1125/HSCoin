import { API_URL } from './config.js';

class AuthService {
    static async login(email, password) {
        try {
            const response = await fetch(`${API_URL}/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password }),
            });
            
            const data = await response.json();
            if (data.success) {
                localStorage.setItem('token', data.token);
                return { success: true };
            }
            return { success: false, message: data.message };
        } catch (error) {
            return { success: false, message: 'Đã xảy ra lỗi. Vui lòng thử lại.' };
        }
    }

    static async register(name, email, password) {
        try {
            const response = await fetch(`${API_URL}/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ name, email, password }),
            });
            
            const data = await response.json();
            return data;
        } catch (error) {
            return { success: false, message: 'Đã xảy ra lỗi. Vui lòng thử lại.' };
        }
    }

    static logout() {
        localStorage.removeItem('token');
        window.location.href = '/index.html';
    }
}

// Form handlers
document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');

    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const messageEl = document.getElementById('login-message');

            const result = await AuthService.login(email, password);
            if (result.success) {
                messageEl.textContent = 'Đăng nhập thành công! Đang chuyển hướng...';
                messageEl.className = 'message success';
                setTimeout(() => {
                    window.location.href = 'dashboard.html';
                }, 1500);
            } else {
                messageEl.textContent = result.message;
                messageEl.className = 'message error';
            }
        });
    }

    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const name = document.getElementById('name').value;
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const messageEl = document.getElementById('register-message');

            const result = await AuthService.register(name, email, password);
            if (result.success) {
                messageEl.textContent = 'Đăng ký thành công! Đang chuyển hướng đến trang đăng nhập...';
                messageEl.className = 'message success';
                setTimeout(() => {
                    window.location.href = 'login.html';
                }, 1500);
            } else {
                messageEl.textContent = result.message;
                messageEl.className = 'message error';
            }
        });
    }
});
