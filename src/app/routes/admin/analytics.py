"""
This file contains functions and routes related to analytics
for the admin section of the application.
~~~~~~~~~~~~~~~~~~~~~

The functions in this file utilize the Google Analytics API to generate reports on various metrics
such as user countries, page views, user devices, and active users.
The reports are then used to provide data for the admin analytics page.

To use the functions in this file, you need to download the credentials
from the Google Cloud Console and set the environment variable 
GOOGLE_APPLICATION_CREDENTIALS to the path of the credentials file.

Functions:
----------------
- run_report(dimensions, metrics, date_ranges): Runs a report using the Google Analytics API.
- report_on_user_countries(): Generates a report on user countries.
- report_on_page_views(): Generates a report on page views.
- report_on_user_devices(): Generates a report on user devices.
- report_on_active_users(): Generates a report on active users.
- admin_analytics_country_sessions(): Retrieves data for admin analytics on country sessions.
- admin_analytics_page_views(): Retrieves data for admin analytics on page views.
- admin_analytics_user_devices(): Retrieves data for admin analytics on user devices.
- admin_analytics_active_users(): Retrieves data for admin analytics on active users.
- admin_analytics_get(): Renders the admin analytics page.

Routes:
----------------
- GET '/admin/analytics/country_sessions': Retrieves data for admin analytics on country sessions.
- GET '/admin/analytics/page_views': Retrieves data for admin analytics on page views.
- GET '/admin/analytics/user_devices': Retrieves data for admin analytics on user devices.
- GET '/admin/analytics/active_users': Retrieves data for admin analytics on active users.
- GET '/admin/analysis': Renders the admin analytics page.
"""

import os

from flask import jsonify, flash, render_template
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)

from app import app, admin_required

def run_report(
        dimensions,
        metrics,
        date_ranges=DateRange(start_date="2020-03-31", end_date="today")):
    """
    Runs a report using the Google Analytics API.

    Args:
        dimensions (list): A list of dimensions to include in the report.
        metrics (list): A list of metrics to include in the report.
        date_ranges (DateRange, optional): The date range for the report.
        Defaults to [DateRange(start_date="2020-03-31", end_date="today")].

    Yields:
        tuple: A tuple containing the dimension value and metric value for each row in the report.

    Raises:
        Exception: If an error occurs while running the report.

    Note: 
        You need to download the credentials from the Google Cloud Console and
        set the environment variable GOOGLE_APPLICATION_CREDENTIALS
        to the path of the credentials file.
    """
    try:
        client = BetaAnalyticsDataClient()
        request = RunReportRequest(
            property=f"properties/{os.environ.get('GA4_PROPERTY_ID')}",
            dimensions=dimensions,
            metrics=metrics,
            date_ranges=[date_ranges],
        )
        response = client.run_report(request)

        for row in response.rows:
            yield (row.dimension_values[0].value, row.metric_values[0].value)

    except IndexError as e:
        flash(f"An error occurred: {e}")

def report_on_user_countries():
    """
    Generates a report on user countries.

    Returns:
        tuple: A tuple containing the country name and the number of sessions.
    """
    yield from run_report([Dimension(name="country")], [Metric(name="sessions")])

def report_on_page_views():
    """
    Generates a report on page views.

    Returns:
        tuple: A tuple containing the page path and the number of screen page views.
    """
    yield from run_report([Dimension(name="pageTitle")], [Metric(name="screenPageViews")])

def report_on_user_devices():
    """
    Generates a report on user devices.

    This function runs a report on user devices using the specified dimensions and metrics.

    Parameters:
        None

    Returns:
        None
    """
    yield from run_report([Dimension(name="deviceCategory")], [Metric(name="sessions")])

def report_on_active_users():
    """
    Generates a report on active users.

    This function runs a report on active users using the specified dimensions and metrics.

    Parameters:
        None

    Returns:
        None
    """
    yield from run_report([Dimension(name="date")], [Metric(name="activeUsers")])


@app.get("/admin/analytics/country_sessions")
@admin_required
def admin_analytics_country_sessions():
    """
    Retrieves data for admin analytics on country sessions.

    Returns:
        JSON response containing the data for country sessions.
    """
    country_sessions = list(report_on_user_countries())
    return jsonify(country_sessions)


@app.get("/admin/analytics/page_views")
@admin_required
def admin_analytics_page_views():
    """
    Retrieves data for admin analytics on page views.

    Returns:
        JSON response containing the data for page views.
    """
    page_views = list(report_on_page_views())[:15]
    return jsonify(page_views)


@app.get("/admin/analytics/user_devices")
@admin_required
def admin_analytics_user_devices():
    """
    Retrieves data for admin analytics on user devices.

    Returns:
        JSON response containing the data for user devices.
    """
    user_devices = list(report_on_user_devices())
    return jsonify(user_devices)


@app.get("/admin/analytics/active_users")
@admin_required
def admin_analytics_active_users():
    """
    Retrieves data for admin analytics on active users.

    Returns:
        JSON response containing the data for active users.
    """
    active_users = list(report_on_active_users())[:10]
    return jsonify(active_users)

@app.get("/admin/analysis")
@admin_required
def admin_analytics_get():
    """
    Renders the admin analytics page.

    Returns:
        A rendered template for the admin analytics page.
    """
    return render_template("Admin/analytics.html")
