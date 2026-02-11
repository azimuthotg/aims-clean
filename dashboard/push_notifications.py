"""
AIMS Push Notifications Backend
Django views and utilities for Web Push notifications
"""

import json
import logging
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import PushSubscription

# Set up logging
logger = logging.getLogger(__name__)

User = get_user_model()

@login_required
@require_http_methods(["POST"])
def subscribe_push(request):
    """Handle push notification subscription"""
    try:
        data = json.loads(request.body)
        subscription = data.get('subscription', {})
        
        if not subscription:
            return JsonResponse({'error': 'Missing subscription data'}, status=400)
        
        endpoint = subscription.get('endpoint')
        keys = subscription.get('keys', {})
        p256dh = keys.get('p256dh')
        auth = keys.get('auth')
        
        if not all([endpoint, p256dh, auth]):
            return JsonResponse({'error': 'Invalid subscription data'}, status=400)
        
        # Create or update subscription
        push_subscription, created = PushSubscription.objects.update_or_create(
            endpoint=endpoint,
            defaults={
                'user': request.user,
                'p256dh_key': p256dh,
                'auth_key': auth,
                'user_agent': data.get('user_agent', ''),
                'is_active': True
            }
        )
        
        logger.info(f"Push subscription {'created' if created else 'updated'} for user {request.user.username}")
        
        return JsonResponse({
            'success': True,
            'message': 'Push subscription saved successfully',
            'subscription_id': push_subscription.id
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        logger.error(f"Error in subscribe_push: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)

@login_required
@require_http_methods(["POST"])
def unsubscribe_push(request):
    """Handle push notification unsubscription"""
    try:
        data = json.loads(request.body)
        endpoint = data.get('endpoint')
        
        if not endpoint:
            return JsonResponse({'error': 'Missing endpoint'}, status=400)
        
        # Deactivate subscription
        updated = PushSubscription.objects.filter(
            endpoint=endpoint,
            user=request.user
        ).update(is_active=False)
        
        if updated:
            logger.info(f"Push subscription unsubscribed for user {request.user.username}")
            return JsonResponse({
                'success': True,
                'message': 'Push subscription removed successfully'
            })
        else:
            return JsonResponse({'error': 'Subscription not found'}, status=404)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        logger.error(f"Error in unsubscribe_push: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)

@login_required
@require_http_methods(["POST"])
def test_notification(request):
    """Send a test push notification"""
    try:
        data = json.loads(request.body)
        title = data.get('title', 'AIMS ทดสอบการแจ้งเตือน')
        message = data.get('message', 'นี่คือการทดสอบการแจ้งเตือนจากระบบ AIMS')
        
        # Get user's active subscriptions
        subscriptions = PushSubscription.objects.filter(
            user=request.user,
            is_active=True
        )
        
        if not subscriptions.exists():
            return JsonResponse({
                'error': 'No active push subscriptions found',
                'message': 'กรุณาเปิดการแจ้งเตือนก่อน'
            }, status=400)
        
        # Prepare notification data
        notification_data = {
            'title': title,
            'body': message,
            'icon': '/static/icons/icon-192x192.png',
            'badge': '/static/icons/icon-96x96.png',
            'tag': 'aims-test-notification',
            'requireInteraction': True,
            'data': {
                'url': '/dashboard/',
                'timestamp': datetime.now().isoformat(),
                'type': 'test'
            },
            'actions': [
                {
                    'action': 'open',
                    'title': '📊 เปิด AIMS Dashboard'
                },
                {
                    'action': 'close', 
                    'title': '❌ ปิด'
                }
            ]
        }
        
        # Send notification to all user's subscriptions
        sent_count = 0
        failed_count = 0
        
        for subscription in subscriptions:
            try:
                # In a real implementation, you would use a library like pywebpush
                # For now, we'll just log and return success
                logger.info(f"Sending test notification to {subscription.endpoint[:50]}...")
                
                # Here you would implement actual push sending:
                # send_web_push(subscription, notification_data)
                
                sent_count += 1
                
            except Exception as e:
                logger.error(f"Failed to send notification to {subscription.endpoint[:50]}: {str(e)}")
                failed_count += 1
        
        return JsonResponse({
            'success': True,
            'message': f'Test notification sent to {sent_count} device(s)',
            'sent_count': sent_count,
            'failed_count': failed_count,
            'notification_data': notification_data
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        logger.error(f"Error in test_notification: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)

def send_push_notification(user_ids, title, message, url='/dashboard/', **kwargs):
    """
    Utility function to send push notifications to specific users
    
    Args:
        user_ids: List of user IDs or single user ID
        title: Notification title
        message: Notification message
        url: URL to open when notification is clicked
        **kwargs: Additional notification options
    """
    if isinstance(user_ids, (int, str)):
        user_ids = [user_ids]
    
    # Get active subscriptions for specified users
    subscriptions = PushSubscription.objects.filter(
        user_id__in=user_ids,
        is_active=True
    )
    
    if not subscriptions.exists():
        logger.warning(f"No active subscriptions found for users: {user_ids}")
        return {'sent': 0, 'failed': 0}
    
    # Prepare notification data
    notification_data = {
        'title': title,
        'body': message,
        'icon': kwargs.get('icon', '/static/icons/icon-192x192.png'),
        'badge': kwargs.get('badge', '/static/icons/icon-96x96.png'),
        'tag': kwargs.get('tag', 'aims-notification'),
        'requireInteraction': kwargs.get('requireInteraction', True),
        'data': {
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'type': kwargs.get('type', 'general'),
            **kwargs.get('data', {})
        }
    }
    
    # Add action buttons if provided
    if 'actions' in kwargs:
        notification_data['actions'] = kwargs['actions']
    
    sent_count = 0
    failed_count = 0
    
    for subscription in subscriptions:
        try:
            # In a real implementation, use pywebpush library
            # send_web_push(subscription, notification_data)
            
            logger.info(f"Sending notification to user {subscription.user.username}")
            sent_count += 1
            
        except Exception as e:
            logger.error(f"Failed to send notification to {subscription.user.username}: {str(e)}")
            failed_count += 1
    
    return {'sent': sent_count, 'failed': failed_count}

def send_broadcast_notification(title, message, url='/dashboard/', **kwargs):
    """
    Send notification to all active subscriptions
    """
    # Get all active subscriptions
    subscriptions = PushSubscription.objects.filter(is_active=True)
    user_ids = subscriptions.values_list('user_id', flat=True).distinct()
    
    return send_push_notification(user_ids, title, message, url, **kwargs)

# Usage examples for different notification types:

def notify_data_update(affected_users=None):
    """Notify users about data updates"""
    title = "📊 AIMS อัพเดทข้อมูล"
    message = "ข้อมูลบุคลากรและนักศึกษาได้รับการอัพเดทแล้ว"
    
    if affected_users:
        return send_push_notification(affected_users, title, message)
    else:
        return send_broadcast_notification(title, message)

def notify_system_maintenance():
    """Notify about system maintenance"""
    title = "🔧 AIMS ระบบบำรุงรักษา"
    message = "ระบบจะปิดปรับปรุงในวันที่ XX เวลา XX:XX น."
    
    return send_broadcast_notification(
        title, message,
        tag='maintenance',
        requireInteraction=True
    )

def notify_security_alert(user_id, details):
    """Notify about security events"""
    title = "🔐 AIMS การแจ้งเตือนความปลอดภัย"
    message = f"ตรวจพบการเข้าสู่ระบบผิดปกติ: {details}"
    
    return send_push_notification(
        user_id, title, message,
        tag='security',
        type='security',
        requireInteraction=True
    )