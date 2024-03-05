from web import *
from models import *
from forms import *

# Admin page

@app.route('/admin', methods=['GET','POST'])
@admin_required
def admin_page():
    count_of_users = User.query.count()
    count_of_products = Product.query.count()
    return render_template('Admin/admin.html', count_of_products=count_of_products, count_of_users=count_of_users)


@app.route('/admin/users', methods=['GET','POST'])
@admin_required
def admin_users_page(page=1):
    form = SearchForm()
    total_pages = User.query.count() // 10

    search_query = ''           

    if request.method == 'POST':
        if form.validate_on_submit():
            search_query = form.search.data
    try:
        users = User.query.filter(
            (User.username.ilike(f'%{search_query}%')) |
            (User.name.ilike(f'%{search_query}%')) |
            (User.email_address.ilike(f'%{search_query}%'))
        )
        amount_of_users = users.count()
    except IndexError:
        users = User.query.filter(
            (User.username.ilike(f'%{search_query}%')) |
            (User.name.ilike(f'%{search_query}%')) |
            (User.email_address.ilike(f'%{search_query}%'))
        )
        amount_of_users = users.count()
    return render_template('Admin/users.html', users=users, page=page, total_pages=total_pages, search_query=search_query, amount_of_users=amount_of_users, form=form)
    
@app.route('/admin/user/<int:id>', methods=['GET','POST'])
@admin_required
def admin_user_info_page(id):
    user = User.query.get(id)
    return render_template('Admin/user-info.html', user=user)

@app.route('/admin/user/edit/<int:id>', methods=['GET','POST'])
@admin_required
def admin_user_edit_page(id):
    user = User.query.get(id)
    if request.method == 'POST':

        if user.role == 'owner' and current_user.role != 'owner':
            flash("You can't edit owner", category='danger')
            return redirect('/admin/users')

        # Username, name, email
        username = request.form.get('username')
        name = request.form.get('name')
        email_address = request.form.get('email')

        if username != user.username:
            if User.check_username(username):
                flash("This username is already taken", category='danger')
                return redirect(f'/admin/user/edit/{id}')
            user.username = username
        if name != user.name:
            user.name = name
        if email_address != user.email_address:
            if User.query.filter_by(email_address=email_address).count():
                flash("This email is already taken", category='danger')
                return redirect(f'/admin/user/edit/{id}')
            user.email_address = email_address
            
        # Confimation
        confirmation = request.form.get('confirmed')
        if confirmation == 'True':
            if user.is_confirmed == False:
                user.is_confirmed = True
                user.confirmed_on = str(datetime.now())[:19]
        if confirmation == 'False':
            if user.is_confirmed == True:
                user.is_confirmed = False
                user.confirmed_on = None

        # Role
        role = request.form.get('role')
        
        if current_user.role != 'owner' and role == 'owner':
            flash("You can't change owner role", category='danger')
            return redirect(f'/admin/user/edit/{id}')

        if role != user.role:
            user.role = role

        db.session.commit()
        flash("User edited successfully", category='success')
        return redirect('/admin/users')
    return render_template('Admin/edit-user.html', name=user.name, username=user.username, 
                           email_address=user.email_address, is_confirmed=user.is_confirmed, role=user.role, id=user.id)

@app.route('/admin/user/delete/<int:id>', methods=['GET','POST'])
@admin_required
def admin_user_delete_page(id):
    form = SubmitForm()
    user = User.query.get(id)
    if form.validate_on_submit():
        if user.role == 'owner' and current_user.role != 'owner':
            flash("You can't delete owner", category='danger')
            return redirect('/admin/users')
        
        db.session.delete(user)
        db.session.commit()
        flash("User deleted successfully", category='success')
        return redirect('/admin/users')
    return render_template('Admin/delete-user.html', form=form, user=user)


@app.route('/admin/products', methods=['GET','POST'])
@admin_required
def admin_products_page():
    pass