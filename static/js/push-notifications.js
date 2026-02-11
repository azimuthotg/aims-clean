/**
 * AIMS PWA Push Notifications
 * Web Push API Implementation
 */

class AIMSPushNotifications {
    constructor() {
        this.swRegistration = null;
        this.isSubscribed = false;
        this.applicationServerKey = null;
        
        // Initialize when DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.init());
        } else {
            this.init();
        }
    }

    async init() {
        console.log('🔔 AIMS Push Notifications: Initializing...');
        
        // Check if service worker and push messaging are supported
        if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
            console.warn('❌ Push messaging is not supported');
            this.showNotificationError('เบราว์เซอร์ไม่รองรับการแจ้งเตือน');
            return;
        }

        try {
            // Wait for service worker registration to be ready
            console.log('⏳ Waiting for Service Worker registration...');
            this.swRegistration = await navigator.serviceWorker.ready;
            console.log('✅ Service Worker ready for push notifications');
            
            // Initialize UI
            this.initializeUI();
            
            // Check current subscription status
            await this.updateSubscriptionStatus();
            
        } catch (error) {
            console.error('❌ Error initializing push notifications:', error);
            // Retry after a delay if service worker isn't ready
            setTimeout(() => {
                console.log('🔄 Retrying push notifications initialization...');
                this.init();
            }, 2000);
        }
    }

    initializeUI() {
        // Create notification control UI
        this.createNotificationUI();
        
        // Add notification button to navbar if it doesn't exist
        this.addNotificationButton();
    }

    createNotificationUI() {
        // Check if notification UI already exists
        if (document.getElementById('notification-controls')) return;
        
        const notificationHTML = `
            <div id="notification-controls" class="d-none">
                <div class="alert alert-info alert-dismissible fade show" role="alert">
                    <i class="fas fa-bell me-2"></i>
                    <strong>การแจ้งเตือน AIMS</strong>
                    <p class="mb-2 mt-1">รับการแจ้งเตือนเมื่อมีข้อมูลใหม่หรือการอัพเดทระบบ</p>
                    <div class="btn-group" role="group">
                        <button id="enable-notifications" class="btn btn-success btn-sm">
                            <i class="fas fa-bell"></i> เปิดการแจ้งเตือน
                        </button>
                        <button id="disable-notifications" class="btn btn-outline-secondary btn-sm d-none">
                            <i class="fas fa-bell-slash"></i> ปิดการแจ้งเตือน
                        </button>
                        <button id="test-notification" class="btn btn-outline-primary btn-sm d-none">
                            <i class="fas fa-paper-plane"></i> ทดสอบ
                        </button>
                    </div>
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            </div>
        `;
        
        // Insert notification UI after navbar
        const navbar = document.querySelector('.navbar');
        if (navbar) {
            navbar.insertAdjacentHTML('afterend', notificationHTML);
        }
        
        // Add event listeners
        this.attachUIEventListeners();
    }

    addNotificationButton() {
        // Bell icon already exists in HTML, just add click handler
        const bellButton = document.getElementById('notification-toggle-test');
        if (bellButton) {
            bellButton.addEventListener('click', (e) => {
                e.preventDefault();
                console.log('🔔 Bell icon clicked!');
                this.toggleNotificationControls();
            });
            console.log('✅ Bell icon event handler attached');
        } else {
            console.error('❌ Bell icon not found');
        }
    }

    attachUIEventListeners() {
        // Enable notifications button
        const enableBtn = document.getElementById('enable-notifications');
        if (enableBtn) {
            enableBtn.addEventListener('click', () => this.subscribeUser());
        }
        
        // Disable notifications button
        const disableBtn = document.getElementById('disable-notifications');
        if (disableBtn) {
            disableBtn.addEventListener('click', () => this.unsubscribeUser());
        }
        
        // Test notification button
        const testBtn = document.getElementById('test-notification');
        if (testBtn) {
            testBtn.addEventListener('click', () => this.sendTestNotification());
        }
    }

    toggleNotificationControls() {
        const controls = document.getElementById('notification-controls');
        if (controls) {
            controls.classList.toggle('d-none');
        }
    }

    async updateSubscriptionStatus() {
        try {
            // Check if swRegistration is available
            if (!this.swRegistration) {
                console.warn('⚠️ Service Worker registration not ready yet');
                return;
            }
            
            const subscription = await this.swRegistration.pushManager.getSubscription();
            this.isSubscribed = subscription !== null;
            
            console.log(`📊 Push subscription status: ${this.isSubscribed ? 'Subscribed' : 'Not subscribed'}`);
            
            this.updateUI();
            
            if (subscription) {
                console.log('📝 Current subscription:', subscription.endpoint);
            }
            
        } catch (error) {
            console.error('❌ Error checking subscription status:', error);
        }
    }

    updateUI() {
        const enableBtn = document.getElementById('enable-notifications');
        const disableBtn = document.getElementById('disable-notifications');
        const testBtn = document.getElementById('test-notification');
        const icon = document.getElementById('notification-icon');
        
        if (this.isSubscribed) {
            // User is subscribed
            enableBtn?.classList.add('d-none');
            disableBtn?.classList.remove('d-none');
            testBtn?.classList.remove('d-none');
            
            if (icon) {
                icon.className = 'fas fa-bell text-success';
                icon.title = 'การแจ้งเตือนเปิดอยู่';
            }
        } else {
            // User is not subscribed
            enableBtn?.classList.remove('d-none');
            disableBtn?.classList.add('d-none');
            testBtn?.classList.add('d-none');
            
            if (icon) {
                icon.className = 'fas fa-bell-slash text-muted';
                icon.title = 'การแจ้งเตือนปิดอยู่';
            }
        }
    }

    async subscribeUser() {
        try {
            console.log('🔔 Requesting notification permission...');
            
            // Check if swRegistration is available
            if (!this.swRegistration) {
                console.error('❌ Service Worker registration not available');
                this.showNotificationError('ระบบยังไม่พร้อม กรุณาลองใหม่อีกครั้ง');
                return;
            }
            
            // Request notification permission
            const permission = await Notification.requestPermission();
            
            if (permission === 'granted') {
                console.log('✅ Notification permission granted');
                
                // Subscribe to push notifications
                const subscription = await this.swRegistration.pushManager.subscribe({
                    userVisibleOnly: true,
                    applicationServerKey: this.urlB64ToUint8Array(this.getApplicationServerKey())
                });
                
                console.log('✅ User subscribed to push notifications');
                console.log('📝 Subscription:', subscription);
                
                // Send subscription to server
                await this.sendSubscriptionToServer(subscription);
                
                this.isSubscribed = true;
                this.updateUI();
                
                this.showNotificationSuccess('เปิดการแจ้งเตือนเรียบร้อยแล้ว');
                
            } else {
                console.warn('❌ Notification permission denied');
                this.showNotificationError('กรุณาอนุญาตการแจ้งเตือนในเบราว์เซอร์');
            }
            
        } catch (error) {
            console.error('❌ Error subscribing user:', error);
            this.showNotificationError('เกิดข้อผิดพลาดในการเปิดการแจ้งเตือน');
        }
    }

    async unsubscribeUser() {
        try {
            const subscription = await this.swRegistration.pushManager.getSubscription();
            
            if (subscription) {
                await subscription.unsubscribe();
                await this.removeSubscriptionFromServer(subscription);
                
                console.log('✅ User unsubscribed from push notifications');
                this.showNotificationSuccess('ปิดการแจ้งเตือนเรียบร้อยแล้ว');
            }
            
            this.isSubscribed = false;
            this.updateUI();
            
        } catch (error) {
            console.error('❌ Error unsubscribing user:', error);
            this.showNotificationError('เกิดข้อผิดพลาดในการปิดการแจ้งเตือน');
        }
    }

    async sendSubscriptionToServer(subscription) {
        try {
            const response = await fetch('/dashboard/push/subscribe/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                },
                body: JSON.stringify({
                    subscription: subscription.toJSON(),
                    user_agent: navigator.userAgent,
                    timestamp: new Date().toISOString()
                })
            });
            
            if (response.ok) {
                console.log('✅ Subscription sent to server');
            } else {
                console.error('❌ Failed to send subscription to server');
            }
            
        } catch (error) {
            console.error('❌ Error sending subscription to server:', error);
        }
    }

    async removeSubscriptionFromServer(subscription) {
        try {
            const response = await fetch('/dashboard/push/unsubscribe/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                },
                body: JSON.stringify({
                    endpoint: subscription.endpoint
                })
            });
            
            if (response.ok) {
                console.log('✅ Subscription removed from server');
            }
            
        } catch (error) {
            console.error('❌ Error removing subscription from server:', error);
        }
    }

    async sendTestNotification() {
        try {
            const response = await fetch('/dashboard/push/test/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                },
                body: JSON.stringify({
                    title: 'AIMS ทดสอบการแจ้งเตือน',
                    message: 'นี่คือการทดสอบการแจ้งเตือนจากระบบ AIMS',
                    timestamp: new Date().toISOString()
                })
            });
            
            if (response.ok) {
                console.log('✅ Test notification sent');
                this.showNotificationSuccess('ส่งการแจ้งเตือนทดสอบแล้ว');
            } else {
                this.showNotificationError('ไม่สามารถส่งการแจ้งเตือนทดสอบได้');
            }
            
        } catch (error) {
            console.error('❌ Error sending test notification:', error);
            this.showNotificationError('เกิดข้อผิดพลาดในการส่งการแจ้งเตือน');
        }
    }

    // Utility functions
    getApplicationServerKey() {
        // This will be replaced with actual VAPID public key
        return 'BEl62iUYgUivxIkv69yViEuiBIa40HI80NuVx6wDNKWkPE0aMKNxXUJT_uNkcMnR7oUjLp9iBvWoVHoGM8FYjE8';
    }

    urlB64ToUint8Array(base64String) {
        const padding = '='.repeat((4 - base64String.length % 4) % 4);
        const base64 = (base64String + padding)
            .replace(/\-/g, '+')
            .replace(/_/g, '/');
        
        const rawData = window.atob(base64);
        const outputArray = new Uint8Array(rawData.length);
        
        for (let i = 0; i < rawData.length; ++i) {
            outputArray[i] = rawData.charCodeAt(i);
        }
        return outputArray;
    }

    getCSRFToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
            }
        }
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }

    showNotificationSuccess(message) {
        this.showToast(message, 'success');
    }

    showNotificationError(message) {
        this.showToast(message, 'error');
    }

    showToast(message, type = 'info') {
        // Create toast notification
        const toastHTML = `
            <div class="toast align-items-center text-white bg-${type === 'success' ? 'success' : 'danger'} border-0 show" role="alert">
                <div class="d-flex">
                    <div class="toast-body">
                        <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-triangle'} me-2"></i>
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;
        
        // Add to toast container or create one
        let toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toast-container';
            toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            toastContainer.style.zIndex = '1055';
            document.body.appendChild(toastContainer);
        }
        
        toastContainer.insertAdjacentHTML('beforeend', toastHTML);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            const toasts = toastContainer.querySelectorAll('.toast');
            if (toasts.length > 0) {
                toasts[0].remove();
            }
        }, 5000);
    }
}

// Initialize AIMS Push Notifications
window.aimsPushNotifications = new AIMSPushNotifications();