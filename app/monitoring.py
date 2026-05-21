"""
Monitoring module for Prometheus metrics and error tracking
Tracks application errors, requests, and database operations
"""

import os
import requests
from prometheus_client import Counter, Histogram, Gauge
from flask import request, current_app
from datetime import datetime
import traceback

# ===== PROMETHEUS METRICS =====

# Counter for total errors
total_errors = Counter(
    'microblog_errors_total',
    'Total number of errors in the application',
    ['error_type', 'endpoint']
)

# Counter for HTTP requests
http_requests = Counter(
    'microblog_http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

# Histogram for request duration
request_duration = Histogram(
    'microblog_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)

# Counter for database operations
db_operations = Counter(
    'microblog_db_operations_total',
    'Total database operations',
    ['operation', 'status']
)

# Gauge for active users
active_users = Gauge(
    'microblog_active_users',
    'Number of currently active users'
)

# Counter for authentication events
auth_events = Counter(
    'microblog_auth_events_total',
    'Authentication events',
    ['event_type', 'status']
)

# ===== WEBHOOK.SITE INTEGRATION =====

WEBHOOK_URL = os.environ.get('WEBHOOK_URL', 'https://webhook.site/unique-id')

def send_alert_to_webhook(error_type: str, error_message: str, endpoint: str, traceback_str: str):
    """
    Send error alert to webhook.site for monitoring and alerting
    
    Args:
        error_type: Type of error (ValueError, KeyError, etc.)
        error_message: Error message
        endpoint: The route/endpoint where error occurred
        traceback_str: Full traceback string
    """
    payload = {
        'timestamp': datetime.utcnow().isoformat(),
        'alert_type': 'application_error',
        'error_type': error_type,
        'error_message': error_message,
        'endpoint': endpoint,
        'traceback': traceback_str,
        'severity': 'high'
    }
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            json=payload,
            timeout=5
        )
        current_app.logger.info(f"Alert sent to webhook: {response.status_code}")
    except Exception as e:
        current_app.logger.error(f"Failed to send webhook alert: {str(e)}")


def record_error(error_type: str, error_message: str, endpoint: str = 'unknown'):
    """
    Record error metrics and send alert
    
    Args:
        error_type: Type of error
        error_message: Error message
        endpoint: Route where error occurred
    """
    # Record in Prometheus
    total_errors.labels(error_type=error_type, endpoint=endpoint).inc()
    
    # Get traceback
    tb_str = traceback.format_exc()
    
    # Send to webhook
    send_alert_to_webhook(error_type, error_message, endpoint, tb_str)
    
    # Log error
    current_app.logger.error(f"{error_type} on {endpoint}: {error_message}\n{tb_str}")


# ===== FLASK INTEGRATION =====

def init_monitoring(app):
    """
    Initialize monitoring for Flask app
    
    Args:
        app: Flask application instance
    """
    
    @app.before_request
    def before_request_metrics():
        """Record request start time"""
        request.start_time = datetime.utcnow()
    
    @app.after_request
    def after_request_metrics(response):
        """Record request metrics after response"""
        if hasattr(request, 'start_time'):
            duration = (datetime.utcnow() - request.start_time).total_seconds()
            request_duration.labels(
                method=request.method,
                endpoint=request.endpoint or 'unknown'
            ).observe(duration)
        
        # Record HTTP request
        http_requests.labels(
            method=request.method,
            endpoint=request.endpoint or 'unknown',
            status_code=response.status_code
        ).inc()
        
        return response
    
    @app.errorhandler(Exception)
    def handle_error(error):
        """
        Global error handler - catches all unhandled exceptions
        """
        error_type = type(error).__name__
        error_message = str(error)
        endpoint = request.endpoint or 'unknown'
        
        record_error(error_type, error_message, endpoint)
        
        # Re-raise the error so Flask handles it normally
        raise


def record_db_operation(operation: str, status: str = 'success'):
    """
    Record database operation metrics
    
    Args:
        operation: Type of operation (insert, update, delete, query)
        status: Operation status (success, error)
    """
    db_operations.labels(operation=operation, status=status).inc()


def update_active_users(count: int):
    """
    Update active users gauge
    
    Args:
        count: Number of active users
    """
    active_users.set(count)


def record_auth_event(event_type: str, status: str = 'success'):
    """
    Record authentication event
    
    Args:
        event_type: Type of auth event (login, logout, register)
        status: Event status (success, failure)
    """
    auth_events.labels(event_type=event_type, status=status).inc()