"""
This file contains routes for managing products.
- Product search in database
- Product editing, deleting and viewing pages
"""

from web import (app, admin_required, render_template,
                request, redirect, flash, db, datetime)
from models import Product, PriceHistory


@app.get("/admin/products/search")
@admin_required
def admin_products_search_get():
    """
    This route handles the search functionality for admin users to search for products.

    Parameters:
    - search (str, optional): The search query to filter products by title.
    - min_price (int, optional): The minimum price to filter products by.
    - max_price (int, optional): The maximum price to filter products by.
    - brand (str, optional): The brand name to filter products by.
    - min_rating (float, optional): The minimum rating to filter products by.
    - max_rating (float, optional): The maximum rating to filter products by.

    Returns:
    - render_template: A Flask function that renders a template with the following arguments:
        - items: The paginated products matching the search filters.
        - total_pages: The total number of pages for the paginated products.
        - variables: A dictionary containing the search filters and their corresponding values.
        - function: A string indicating the name of the current function ('admin_products_search_get').
        - page: The current page number for the paginated products.

    Example Usage:
    - When a user visits the '/admin/products/search' route, this function is called to handle the search functionality for admin users.
    - The function retrieves the search filters from the request arguments and applies them to the Product query.
    - The filtered products are then paginated and rendered in the 'Admin/search.html' template along with other necessary data.

    Note:
    - This function requires the user to be an admin, as indicated by the @admin_required decorator.
    """
    page = request.args.get("page", 1, type=int)

    filters = Product.get_filters()

    products = Product.query
    variables = {}
    for key, value in filters.items():
        if value[0]:
            products = value[1](value[0], products)
            variables[key] = value[0]

    products = products.paginate(page=page, per_page=9)
    total_pages = products.pages

    return render_template(
        "Admin/search.html",
        items=products,
        total_pages=total_pages,
        variables=variables,
        function="admin_products_search_get",
        page=page,
    )


@app.get("/admin/product/<int:id>")
@admin_required
def admin_product_info_get(id):
    """
    This route handles the admin product information page.

    Parameters:
    - id (int): The ID of the product.

    Returns:
    - render_template: The rendered template for the admin product information page.

    Raises:
    - None.

    Usage:
    - This route is used to display the information of a specific product in the admin panel.
    - It requires the user to be an admin.

    Example:
    - To access the information page of a product with ID 123, the URL would be '/admin/product/123'.
    """
    product = Product.query.get(id)
    return render_template("Admin/Item/info.html", item=product)


@app.get("/admin/product/edit/<int:id>")
@admin_required
def admin_product_edit_get(id):
    """
    Renders the admin product edit page.

    Args:
        id (int): The ID of the product to be edited.

    Returns:
        A rendered template of the admin product edit page with the product data.

    """
    product = Product.query.get(id)

    return render_template("Admin/Item/edit.html", item=product)


@app.post("/admin/product/edit/<int:id>")
@admin_required
def admin_product_edit_post(id):
    """
    Edit a product with the given ID.

    Args:
        id (int): The ID of the product to be edited.

    Returns:
        redirect: A redirect to the product details page after successful editing.

    Raises:
        None

    """
    # Title, price, item_class, producer, amount_of_ratings, rating, availability
    fields = [
        "title",
        "price",
        "item_class",
        "producer",
        "amount_of_ratings",
        "rating",
        "availability",
    ]
    product = Product.query.get(id)
    for field in fields:
        value = request.form.get(field)
        if field == "availability":
            # Not finished
            continue

        if getattr(product, field) != value:
            if field == "price":
                price_history = PriceHistory(product_id=id)
                price_history = PriceHistory(id, value, datetime.now().date())
                db.session.add(price_history)
            setattr(product, field, value)

    db.session.commit()
    flash("Product edited successfully", category="success")
    return redirect(f"/admin/product/{id}")


@app.get("/admin/product/delete/<int:id>")
@admin_required
def admin_product_delete_get(id):
    """
    Renders the delete page for a specific product in the admin panel.

    Args:
        id (int): The ID of the product to be deleted.

    Returns:
        - Renders the 'Admin/Item/delete.html' template with the product information and the function name.

    """
    product = Product.query.get(id)
    return render_template(
        "Admin/Item/delete.html", item=product, func="admin_product_delete_post"
    )


@app.post("/admin/product/delete/<int:id>")
@admin_required
def admin_product_delete_post(id):
    """
    Delete a product and its associated price history from the database.

    Args:
        id (int): The ID of the product to be deleted.

    Returns:
        redirect: A redirect response to the admin search page.

    """
    product = Product.query.get(id)
    price_history = PriceHistory.query.filter_by(product_id=id)
    for price in price_history:
        db.session.delete(price)
    db.session.delete(product)
    db.session.commit()
    flash("Product deleted successfully", category="success")
    return redirect("/admin/search")