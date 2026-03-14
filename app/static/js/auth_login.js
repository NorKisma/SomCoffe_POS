function togglePassword() {
    const pwd = document.getElementById('passwordField');
    const icon = document.querySelector('.show-pass-toggle:not(.pin-toggle)');
    if (pwd.type === 'password') {
        pwd.type = 'text';
        icon.classList.replace('fa-eye', 'fa-eye-slash');
    } else {
        pwd.type = 'password';
        icon.classList.replace('fa-eye-slash', 'fa-eye');
    }
}

function togglePin() {
    const pinField = document.getElementById('pinField');
    const icon = document.querySelector('.pin-toggle');
    if (pinField.type === 'password') {
        pinField.type = 'text';
        icon.classList.replace('fa-eye', 'fa-eye-slash');
    } else {
        pinField.type = 'password';
        icon.classList.replace('fa-eye-slash', 'fa-eye');
    }
}

function switchMethod(method) {
    const loginType = document.getElementById('login_type');
    const pwdSection = document.getElementById('password-section');
    const pinSection = document.getElementById('pin-section');
    const btnPwd = document.getElementById('btn-password');
    const btnPin = document.getElementById('btn-pin');

    if (method === 'pin') {
        loginType.value = 'pin';
        pwdSection.style.display = 'none';
        pinSection.style.display = 'block';
        btnPin.classList.add('active');
        btnPwd.classList.remove('active');
        
        // Remove required attribute from password fields when PIN is active
        document.querySelectorAll('#password-section input').forEach(input => input.removeAttribute('required'));
        document.getElementById('pinField').setAttribute('required', 'required');
    } else {
        loginType.value = 'password';
        pwdSection.style.display = 'block';
        pinSection.style.display = 'none';
        btnPwd.classList.add('active');
        btnPin.classList.remove('active');
        
        // Restore required attribute
        document.querySelectorAll('#password-section input').forEach(input => {
            if (input.name === 'username' || input.name === 'password') {
                input.setAttribute('required', 'required');
            }
        });
        document.getElementById('pinField').removeAttribute('required');
    }
}

function appendPin(num) {
    const pinField = document.getElementById('pinField');
    if (pinField.value.length < 6) {
        pinField.value += num;
    }
}

function clearPin() {
    const pinField = document.getElementById('pinField');
    pinField.value = pinField.value.slice(0, -1);
}
// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    switchMethod('pin');
    
    // OFFLINE LOGIN HANDLER
    const loginForm = document.getElementById('loginForm');
    loginForm.addEventListener('submit', function(e) {
        if (!navigator.onLine) {
            e.preventDefault();
            const loginType = document.getElementById('login_type').value;
            const pin = document.getElementById('pinField').value;
            
            if (loginType === 'pin' && pin) {
                const offlineUser = JSON.parse(localStorage.getItem('offline_user_session'));
                if (offlineUser && offlineUser.pin === pin) {
                    // Success: Fake a session and redirect to cached POS
                    localStorage.setItem('is_offline_authed', 'true');
                    window.location.href = '/pos/';
                } else {
                    alert('Offline Error: PIN-ka waa khalad ama marna horay uma soo gelin computer-kan adigoo online ah.');
                }
            } else {
                alert('Internet ma jiro. Password-ka kuma shaqeynayo offline. Fadlan isticmaal PIN-kaaga hadaad horay u soo gashay.');
            }
        }
    });

    // Capture success from server to store for offline use
    // Note: In a real app, we'd use a server response. 
    // Here we'll watch for the form submission and if it succeeds (cookie set), 
    // the next page load (Dashboard) will handle the storage.
});
