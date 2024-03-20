from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)
from web import app, admin_required, render_template, flash, os

def run_report(dimensions, metrics, date_ranges=[DateRange(start_date="2020-03-31", end_date="today")]):
    """
    Runs a report using the Google Analytics API.

    Args:
        dimensions (list): A list of dimensions to include in the report.
        metrics (list): A list of metrics to include in the report.
        date_ranges (DateRange, optional): The date range for the report. Defaults to [DateRange(start_date="2020-03-31", end_date="today")].

    Yields:
        tuple: A tuple containing the dimension value and metric value for each row in the report.

    Raises:
        Exception: If an error occurs while running the report.

    Note: 
        You need to download the credentials from the Google Cloud Console and
        set the environment variable GOOGLE_APPLICATION_CREDENTIALS to the path of the credentials file.
    """
    try:
        client = BetaAnalyticsDataClient()
        request = RunReportRequest(
            property=f"properties/{os.environ.get('GA4_PROPERTY_ID')}",
            dimensions=dimensions,
            metrics=metrics,
            date_ranges=date_ranges,
        )
        response = client.run_report(request)

        for row in response.rows:
            yield (row.dimension_values[0].value, row.metric_values[0].value)

    except Exception as e:
        flash(f"An error occurred: {e}")
    
def report_on_user_countries():
    """
    Generates a report on user countries.

    Returns:
        tuple: A tuple containing the country name and the number of sessions.
    """
    for i in run_report([Dimension(name="country")], [Metric(name="sessions")]):
        yield i
    
def report_on_page_views():
    """
    Generates a report on page views.

    Returns:
        tuple: A tuple containing the page path and the number of screen page views.
    """
    for i in run_report([Dimension(name="pagePath")], [Metric(name="screenPageViews")]):
        yield i
    
def report_on_user_devices():
    """
    Generates a report on user devices.

    This function runs a report on user devices using the specified dimensions and metrics.

    Parameters:
        None

    Returns:
        None
    """
    for i in run_report([Dimension(name="deviceCategory")], [Metric(name="sessions")]):
        yield i

def report_on_active_users():
    """
    Generates a report on active users.

    This function runs a report on active users using the specified dimensions and metrics.

    Parameters:
        None

    Returns:
        None
    """
    for i in run_report([Dimension(name="date")], [Metric(name="activeUsers")]):
        yield i

@app.get("/admin/analysis")
@admin_required
def admin_analytics_get():
    """
    Renders the admin analytics page.

    Returns:
        A rendered template for the admin analytics page.
    """

    country_sessions = report_on_user_countries()
    page_views = report_on_page_views()
    user_devices = report_on_user_devices()
    active_users = report_on_active_users()

    country_sessions = list(country_sessions) if country_sessions else []
    page_views = list(page_views) if page_views else []
    user_devices = list(user_devices) if user_devices else []
    active_users = list(active_users) if active_users else []

    report = {
        "country_sessions": country_sessions,
        "page_views": page_views,
        "user_devices": user_devices,
        "active_users": active_users,
    }

    return render_template("Admin/analytics.html", report=report)