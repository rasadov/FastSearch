"""
This file contains routes for managing users.
- User search in database
- User editing, deleting and viewing pages
"""
from web import (app, admin_required, render_template, request,
                redirect, flash, db, current_user, datetime)
from models import User, Cart

@app.get("/admin/users")
@admin_required
def admin_user_search_get():
    """
    Renders the admin user search page.

    This route handles the GET request to '/admin/users' and is accessible only to admin users.
    It retrieves the page number and search query from the request arguments.
    It then performs a search query on the User model using the provided search query,
    filtering by username, name, and email address.
    The search results are paginated with a default of 9 items per page.
    The total number of search results and total number of pages are calculated.
    Finally, the search results, total pages, search query, page number, data type, and function name
    are passed to the 'Admin/search.html' template for rendering.

    Returns:
        A rendered template for the admin user search page.
    """

    page = request.args.get("page", 1, type=int)
    search = request.args.get("search", "")
    users = User.query.filter(
        User.username.ilike(f"%{search}%")
        | User.email_address.ilike(f"%{search}%")
        | User.name.ilike(f"%{search}%")
    )
    variables = {"search": search}

    users = users.paginate(page=page, per_page=9)

    total_pages = users.pages

    return render_template(
        "Admin/search.html",
        items=users,
        total_pages=total_pages,
        variables=variables,
        page=page,
        function="admin_user_search_get",
    )


@app.get("/admin/user/<int:id>")
@admin_required
def admin_user_info_get(id):
    """
    This route handles the admin user info page.

    Parameters:
    - id (int): The ID of the user.

    Returns:
    - render_template: The rendered template for the admin user info page.

    Raises:
    - None

    Usage:
    - This route is used to display the information of a specific user in the admin panel.
    - It requires the user to be logged in as an admin.
    - The user ID is passed as a parameter in the URL.
    """
    user = User.query.get(id)
    cart = Cart.query.filter_by(user_id=id).all()
    cart = [item.product for item in cart]
    return render_template("Admin/Item/info.html", item=user, cart=cart)


@app.get("/admin/user/edit/<int:id>")
@admin_required
def admin_user_edit_get(id):
    """
    returns the admin user edit page.

    Args:
        id (int): The ID of the user to be edited.

    Returns:
        Renders the 'Admin/Item/edit.html' template with the user as context variables.
    """
    user = User.query.get(id)

    return render_template("Admin/Item/edit.html", item=user, func="admin_user_edit_post")


@app.post("/admin/user/edit/<int:id>")
@admin_required
def admin_user_edit_post(id):
    """
    Edits a user with the given ID.

    Args:
        id (int): The ID of the user to be edited.


    Returns:
        - Updates the user's fields based on the form data.
        - Validates the form data using the specified validators.
        - If validation fails, flashes an error message and redirects to the edit page.
        - If validation succeeds, commits the changes to the database, flashes a success message, and redirects to the users page.
    """
    user = User.query.get(id)

    if user.role == "owner" and current_user.role != "owner":
        flash("You can't edit owner", category="danger")
        return redirect("/admin/users")

    fields = {
        "username": {
            "validator": User.username_exists,
            "error_message": "This username is already taken",
        },
        "name": {},
        "email_address": {
            "validator": lambda email: User.query.filter_by(
                email_address=email
            ).count(),
            "error_message": "This email is already taken",
        },
        "confirmed": {},
        "role": {},
    }

    for field, options in fields.items():
        value = request.form.get(field)
        if field == "confirmed":
            if value != f"{user.is_confirmed()}":
                user.confirmed_on = datetime.now().date() if value == "True" else None
            continue
        if getattr(user, field) != value:
            if value == "None":
                value = None

            if "validator" in options and options["validator"](value):
                flash(options["error_message"], category="danger")
                return redirect(f"/admin/user/edit/{id}")
            setattr(user, field, value)

    db.session.commit()
    flash("User edited successfully", category="success")
    return redirect("/admin/users")


@app.get("/admin/user/delete/<int:id>")
@admin_required
def admin_user_delete_get(id):
    """
    This route is used to delete a user with the specified ID from the admin panel.

    Args:
    - id (int): The ID of the user to be deleted.

    Returns:
        - Renders the 'Admin/Item/delete.html' template with the user object and the function name.
    """
    user = User.query.get(id)

    return render_template(
        "Admin/Item/delete.html", item=user, func="admin_user_delete_post"
    )


@app.post("/admin/user/delete/<int:id>")
@admin_required
def admin_user_delete_post(id):
    """
    Deletes a user with the specified ID from the admin panel.

    Args:
        - id (int): The ID of the user to be deleted.

    Returns:
        - Deletes the user from the database.
        - Flashes a success message.
        - Redirects to the '/admin/users' route.

    Note:
        - If the user to be deleted has the role 'owner' and the current user does not have the role 'owner',
        a danger flash message is flashed and the user is redirected to the '/admin/users' route.

    """
    if user.role == "owner" and current_user.role != "owner":
        flash("You can't edit owner", category="danger")
        return redirect("/admin/users")

    user = User.query.get(id)
    db.session.delete(user)
    db.session.commit()
    flash("User deleted successfully", category="success")
    return redirect("/admin/users")

