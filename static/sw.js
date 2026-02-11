// AIMS PWA Service Worker with Push Notifications
const CACHE_NAME = 'aims-pwa-v1.1.0';
const urlsToCache = [
  '/',
  '/dashboard/',
  '/dashboard/staff/',
  '/dashboard/student/', 
  '/dashboard/service-statistics/',
  '/static/manifest.json',
  
  // CSS
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css',
  'https://cdn.jsdelivr.net/npm/admin-lte@3.2/dist/css/adminlte.min.css',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css',
  'https://cdn.jsdelivr.net/npm/apexcharts@latest/dist/apexcharts.css',
  'https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap',
  
  // JavaScript
  'https://code.jquery.com/jquery-3.7.1.min.js',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js',
  'https://cdn.jsdelivr.net/npm/admin-lte@3.2/dist/js/adminlte.min.js',
  'https://cdn.jsdelivr.net/npm/apexcharts@latest'
];

// Install event - cache resources
self.addEventListener('install', event => {
  console.log('🔧 AIMS PWA: Service Worker installing...');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('📦 AIMS PWA: Caching app shell');
        return cache.addAll(urlsToCache);
      })
      .then(() => self.skipWaiting())
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
  console.log('✅ AIMS PWA: Service Worker activating...');
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('🗑️ AIMS PWA: Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', event => {
  // Skip non-GET requests
  if (event.request.method !== 'GET') return;
  
  // Skip Chrome extension requests
  if (event.request.url.startsWith('chrome-extension://')) return;
  
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // Return cached version or fetch from network
        if (response) {
          console.log('💾 AIMS PWA: Serving from cache:', event.request.url);
          return response;
        }
        
        return fetch(event.request).then(response => {
          // Don't cache non-successful responses
          if (!response || response.status !== 200 || response.type !== 'basic') {
            return response;
          }
          
          // Clone the response for caching
          const responseToCache = response.clone();
          
          // Cache successful responses
          caches.open(CACHE_NAME)
            .then(cache => {
              console.log('📥 AIMS PWA: Caching new resource:', event.request.url);
              cache.put(event.request, responseToCache);
            });
          
          return response;
        }).catch(() => {
          // Offline fallback
          if (event.request.destination === 'document') {
            return caches.match('/dashboard/').then(response => 
              response || new Response('🔌 AIMS PWA: คุณกำลังใช้งานแบบออฟไลน์', {
                status: 200,
                statusText: 'Offline',
                headers: {'Content-Type': 'text/html; charset=utf-8'}
              })
            );
          }
        });
      })
  );
});

// Push event - handle incoming push notifications
self.addEventListener('push', event => {
  console.log('🔔 AIMS PWA: Push notification received');
  
  let notificationData = {
    title: 'AIMS แจ้งเตือน',
    body: 'คุณมีข้อมูลใหม่',
    icon: '/static/icons/icon-192x192.png',
    badge: '/static/icons/icon-96x96.png',
    tag: 'aims-notification',
    requireInteraction: true,
    data: {
      url: '/dashboard/',
      timestamp: new Date().toISOString()
    }
  };
  
  // Parse notification data from push payload
  if (event.data) {
    try {
      const pushData = event.data.json();
      console.log('📨 Push data received:', pushData);
      
      notificationData = {
        ...notificationData,
        title: pushData.title || notificationData.title,
        body: pushData.body || pushData.message || notificationData.body,
        icon: pushData.icon || notificationData.icon,
        badge: pushData.badge || notificationData.badge,
        tag: pushData.tag || notificationData.tag,
        requireInteraction: pushData.requireInteraction !== false,
        data: {
          url: pushData.url || pushData.data?.url || '/dashboard/',
          timestamp: pushData.timestamp || new Date().toISOString(),
          ...pushData.data
        }
      };
      
      // Add action buttons if provided
      if (pushData.actions && Array.isArray(pushData.actions)) {
        notificationData.actions = pushData.actions;
      }
      
    } catch (error) {
      console.error('❌ Error parsing push data:', error);
      // Use default notification data
    }
  }
  
  // Show notification
  event.waitUntil(
    self.registration.showNotification(notificationData.title, {
      body: notificationData.body,
      icon: notificationData.icon,
      badge: notificationData.badge,
      tag: notificationData.tag,
      requireInteraction: notificationData.requireInteraction,
      data: notificationData.data,
      actions: notificationData.actions || [
        {
          action: 'open',
          title: '📊 เปิด AIMS Dashboard',
          icon: '/static/icons/icon-96x96.png'
        },
        {
          action: 'close',
          title: '❌ ปิด',
          icon: '/static/icons/icon-96x96.png'
        }
      ]
    })
  );
});

// Notification click event - handle notification interactions
self.addEventListener('notificationclick', event => {
  console.log('🔔 AIMS PWA: Notification clicked');
  
  const notification = event.notification;
  const action = event.action;
  
  // Close the notification
  notification.close();
  
  // Handle notification click actions
  if (action === 'close') {
    console.log('❌ Notification closed by user');
    return;
  }
  
  // Default action or 'open' action
  const urlToOpen = notification.data?.url || '/dashboard/';
  
  console.log('🔗 Opening URL:', urlToOpen);
  
  // Open or focus AIMS PWA window
  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true })
      .then(clientList => {
        // Try to find existing AIMS window
        for (const client of clientList) {
          if (client.url.includes(urlToOpen) && 'focus' in client) {
            console.log('🎯 Focusing existing AIMS window');
            return client.focus();
          }
        }
        
        // Open new window if no existing window found
        if (clients.openWindow) {
          console.log('🔗 Opening new AIMS window');
          return clients.openWindow(urlToOpen);
        }
      })
      .catch(error => {
        console.error('❌ Error handling notification click:', error);
      })
  );
});

// Notification close event
self.addEventListener('notificationclose', event => {
  console.log('🔔 AIMS PWA: Notification closed');
  
  // Track notification close analytics if needed
  const notification = event.notification;
  console.log('📊 Closed notification:', notification.tag);
});

// Background sync for data updates
self.addEventListener('sync', event => {
  console.log('🔄 AIMS PWA: Background sync triggered:', event.tag);
  
  if (event.tag === 'aims-data-sync') {
    event.waitUntil(syncAIMSData());
  }
});

// Push notification handler
self.addEventListener('push', event => {
  console.log('🔔 AIMS PWA: Push notification received');
  
  const options = {
    body: event.data ? event.data.text() : 'มีข้อมูลใหม่ในระบบ AIMS',
    icon: '/static/icons/icon-192x192.png',
    badge: '/static/icons/icon-72x72.png',
    vibrate: [100, 50, 100],
    tag: 'aims-notification',
    requireInteraction: true,
    actions: [
      {
        action: 'view',
        title: 'ดูข้อมูล',
        icon: '/static/icons/view-action.png'
      },
      {
        action: 'close',
        title: 'ปิด',
        icon: '/static/icons/close-action.png'
      }
    ]
  };
  
  event.waitUntil(
    self.registration.showNotification('📊 AIMS Dashboard', options)
  );
});

// Notification click handler
self.addEventListener('notificationclick', event => {
  console.log('🖱️ AIMS PWA: Notification clicked:', event.action);
  
  event.notification.close();
  
  if (event.action === 'view') {
    event.waitUntil(
      clients.openWindow('/dashboard/')
    );
  }
});

// Sync AIMS data function
async function syncAIMSData() {
  try {
    console.log('📊 AIMS PWA: Syncing data...');
    
    // Update dashboard data
    const dashboardResponse = await fetch('/dashboard/');
    if (dashboardResponse.ok) {
      const cache = await caches.open(CACHE_NAME);
      await cache.put('/dashboard/', dashboardResponse.clone());
      console.log('✅ AIMS PWA: Dashboard data synced');
    }
    
    // Show sync complete notification
    self.registration.showNotification('📊 AIMS Dashboard', {
      body: 'ข้อมูลได้รับการอัปเดตแล้ว',
      icon: '/static/icons/icon-192x192.png',
      tag: 'aims-sync-complete'
    });
    
  } catch (error) {
    console.error('❌ AIMS PWA: Sync failed:', error);
  }
}

// Message handler for communication with main thread
self.addEventListener('message', event => {
  console.log('💬 AIMS PWA: Message received:', event.data);
  
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  
  if (event.data && event.data.type === 'GET_VERSION') {
    event.ports[0].postMessage({version: CACHE_NAME});
  }
});

console.log('🚀 AIMS PWA: Service Worker loaded successfully!');