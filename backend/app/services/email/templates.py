"""
Email templates for HITL service notifications.

All templates are HTML-formatted and mobile-responsive.
"""

from datetime import datetime
from typing import Dict, Any


def new_request_email(request_data: Dict[str, Any], dashboard_url: str) -> str:
    """
    Email template for notifying reviewers of a new consultation request.

    Args:
        request_data: Dictionary with request details (title, description, context, id)
        dashboard_url: URL to the dashboard

    Returns:
        HTML email content
    """
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>New Consultation Request</title>
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background-color: #3B82F6; color: white; padding: 20px; border-radius: 8px 8px 0 0;">
            <h1 style="margin: 0; font-size: 24px;">New Consultation Request</h1>
        </div>

        <div style="background-color: #f8f9fa; padding: 20px; border: 1px solid #e9ecef; border-top: none; border-radius: 0 0 8px 8px;">
            <h2 style="color: #3B82F6; margin-top: 0;">{request_data.get('title', 'Untitled Request')}</h2>

            {f"<p style='color: #6c757d;'>{request_data.get('description', '')}</p>" if request_data.get('description') else ''}

            <div style="background-color: white; padding: 15px; border-radius: 4px; margin: 20px 0;">
                <h3 style="margin-top: 0; color: #495057; font-size: 16px;">Request Details</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 8px 0; color: #6c757d; font-weight: 600;">Request ID:</td>
                        <td style="padding: 8px 0; font-family: monospace;">{request_data.get('id', 'N/A')}</td>
                    </tr>
                    {f"<tr><td style='padding: 8px 0; color: #6c757d; font-weight: 600;'>Workflow ID:</td><td style='padding: 8px 0; font-family: monospace;'>{request_data.get('metadata', {}).get('workflow_id', 'N/A')}</td></tr>" if request_data.get('metadata', {}).get('workflow_id') else ''}
                    <tr>
                        <td style="padding: 8px 0; color: #6c757d; font-weight: 600;">Created:</td>
                        <td style="padding: 8px 0;">{datetime.utcnow().strftime('%Y-%m-% d %H:%M UTC')}</td>
                    </tr>
                </table>
            </div>

            <div style="text-align: center; margin: 30px 0;">
                <a href="{dashboard_url}/requests/{request_data.get('id')}"
                   style="display: inline-block; background-color: #3B82F6; color: white; padding: 12px 30px; text-decoration: none; border-radius: 4px; font-weight: 600;">
                    View Request →
                </a>
            </div>

            <p style="color: #6c757d; font-size: 14px; text-align: center; margin-top: 20px;">
                Or visit: <a href="{dashboard_url}" style="color: #3B82F6;">{dashboard_url}</a>
            </p>
        </div>

        <div style="margin-top: 20px; padding: 15px; background-color: #f8f9fa; border-radius: 4px; text-align: center; color: #6c757d; font-size: 12px;">
            <p style="margin: 0;">This is an automated notification from the HITL Service.</p>
        </div>
    </body>
    </html>
    """


def request_responded_email(
    request_data: Dict[str, Any], response_data: Dict[str, Any], dashboard_url: str
) -> str:
    """
    Email template confirming a response was submitted.

    Args:
        request_data: Dictionary with request details
        response_data: Dictionary with response details (decision, comment)
        dashboard_url: URL to the dashboard

    Returns:
        HTML email content
    """
    decision_color = {
        "approve": "#10B981",
        "reject": "#EF4444",
        "request_changes": "#F59E0B",
    }.get(response_data.get("decision", ""), "#6B7280")

    decision_label = response_data.get("decision", "unknown").replace("_", " ").title()

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Response Submitted</title>
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background-color: {decision_color}; color: white; padding: 20px; border-radius: 8px 8px 0 0;">
            <h1 style="margin: 0; font-size: 24px;">✓ Response Submitted</h1>
        </div>

        <div style="background-color: #f8f9fa; padding: 20px; border: 1px solid #e9ecef; border-top: none; border-radius: 0 0 8px 8px;">
            <p style="font-size: 16px; color: #495057;">Your response has been recorded and the agent has been notified.</p>

            <div style="background-color: white; padding: 15px; border-radius: 4px; margin: 20px 0;">
                <h3 style="margin-top: 0; color: #495057; font-size: 16px;">Request: {request_data.get('title', 'Untitled')}</h3>

                <div style="margin: 15px 0; padding: 12px; background-color: #f8f9fa; border-left: 4px solid {decision_color}; border-radius: 4px;">
                    <div style="font-weight: 600; color: {decision_color};">Decision: {decision_label}</div>
                    {f"<div style='margin-top: 8px; color: #495057;'>{response_data.get('comment', '')}</div>" if response_data.get('comment') else ''}
                </div>
            </div>

            <div style="text-align: center; margin: 30px 0;">
                <a href="{dashboard_url}/requests/{request_data.get('id')}"
                   style="display: inline-block; background-color: {decision_color}; color: white; padding: 12px 30px; text-decoration: none; border-radius: 4px; font-weight: 600;">
                    View Request →
                </a>
            </div>
        </div>

        <div style="margin-top: 20px; padding: 15px; background-color: #f8f9fa; border-radius: 4px; text-align: center; color: #6c757d; font-size: 12px;">
            <p style="margin: 0;">This is an automated confirmation from the HITL Service.</p>
        </div>
    </body>
    </html>
    """


def request_timeout_email(request_data: Dict[str, Any], dashboard_url: str) -> str:
    """
    Email template for timeout notification.

    Args:
        request_data: Dictionary with request details
        dashboard_url: URL to the dashboard

    Returns:
        HTML email content
    """
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Request Timed Out</title>
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background-color: #EF4444; color: white; padding: 20px; border-radius: 8px 8px 0 0;">
            <h1 style="margin: 0; font-size: 24px;">⚠️ Request Timed Out</h1>
        </div>

        <div style="background-color: #f8f9fa; padding: 20px; border: 1px solid #e9ecef; border-top: none; border-radius: 0 0 8px 8px;">
            <p style="font-size: 16px; color: #495057;">The following consultation request has timed out without a response.</p>

            <div style="background-color: white; padding: 15px; border-radius: 4px; margin: 20px 0;">
                <h3 style="margin-top: 0; color: #495057; font-size: 16px;">{request_data.get('title', 'Untitled Request')}</h3>

                {f"<p style='color: #6c757d;'>{request_data.get('description', '')}</p>" if request_data.get('description') else ''}

                <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
                    <tr>
                        <td style="padding: 8px 0; color: #6c757d; font-weight: 600;">Request ID:</td>
                        <td style="padding: 8px 0; font-family: monospace;">{request_data.get('id', 'N/A')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; color: #6c757d; font-weight: 600;">Timeout:</td>
                        <td style="padding: 8px 0;">{datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}</td>
                    </tr>
                </table>
            </div>

            <div style="background-color: #FEF3C7; border-left: 4px solid #F59E0B; padding: 15px; border-radius: 4px; margin: 20px 0;">
                <p style="margin: 0; color: #92400E; font-size: 14px;">
                    <strong>Note:</strong> The agent has been notified of the timeout. The request state has been updated to "timeout".
                </p>
            </div>

            <div style="text-align: center; margin: 30px 0;">
                <a href="{dashboard_url}/requests/{request_data.get('id')}"
                   style="display: inline-block; background-color: #EF4444; color: white; padding: 12px 30px; text-decoration: none; border-radius: 4px; font-weight: 600;">
                    View Request →
                </a>
            </div>
        </div>

        <div style="margin-top: 20px; padding: 15px; background-color: #f8f9fa; border-radius: 4px; text-align: center; color: #6c757d; font-size: 12px;">
            <p style="margin: 0;">This is an automated notification from the HITL Service.</p>
        </div>
    </body>
    </html>
    """
