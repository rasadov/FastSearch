"""
This file contains routes for admin inbox
"""

from app import (db, admin_required,
                render_template, request,
                redirect, url_for, app, flash)

from app.models import Message

@app.get("/admin/messages")
@admin_required
def admin_messages_get():
    """
    This route handles the admin message page of the application.

    Returns:
        A rendered template of the admin message page with the list of messages.
    """
    items = Message.query.paginate(page=1, per_page=9)
    function = 'admin_messages_get'

    return render_template("Admin/search.html", items=items, variables={}, function=function)

@app.get("/admin/message/<int:message_id>")
@admin_required
def admin_message_info_get(message_id):
    """
    This route displays the information of a specific message in the admin panel.

    Args:
        message_id (int): The ID of the message to display.

    Returns:
        A rendered template of the message details page.
    """
    message = Message.query.get(message_id)
    return render_template("Admin/info.html", message=message)

@app.get("/admin/message/delete")
@admin_required
def admin_message_delete():
    """
    This route is used to delete a message from the admin panel.

    Args:
        message_id (int): The ID of the message to delete.

    Returns:
        A redirect to the admin message page after deleting the message.
    """
    message_id = request.args.get("id")
    if message_id is None:
        flash("Message ID is required", "error")
        return redirect(url_for("admin_messages_get"))
    message = Message.query.get(message_id)
    db.session.delete(message)
    db.session.commit()
    return redirect(url_for("admin_messages_get"))
