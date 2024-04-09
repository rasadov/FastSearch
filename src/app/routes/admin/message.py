"""
This file contains routes for admin inbox
"""

from flask import request, render_template, redirect, url_for, flash

from app import app, db, admin_required

from app.models import Message, User

@app.get("/admin/messages")
@admin_required
def admin_messages_get():
    """
    This route handles the admin message page of the application.

    Returns:
        A rendered template of the admin message page with the list of messages.
    """
    items = Message.query.order_by(Message.read).paginate(page=1, per_page=9)
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
    user = User.query.get(message.sender_id)
    return render_template("Admin/Item/info.html", item=message, user=user)

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

@app.post("/admin/message/mark_as_read")
@admin_required
def admin_message_mark_as_read():
    """
    This route is used to mark a message as read in the admin panel.

    Args:
        message_id (int): The ID of the message to mark as read.

    Returns:
        A redirect to the admin message page after marking the message as read.
    """
    data = request.get_json()

    try:
        message_id = int(data.get("message_id"))
    except ValueError:
        flash("Invalid message ID", "error")
        return redirect(url_for("admin_messages_get"))
    if message_id is None:
        flash("Message ID is required", "error")
        return redirect(url_for("admin_messages_get"))
    message = Message.query.get(message_id)
    message.mark_as_read()
    db.session.commit()
    return redirect(url_for("admin_messages_get"))
