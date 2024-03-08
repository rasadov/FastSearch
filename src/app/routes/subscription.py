from web import *
from models import *
from datetime import datetime, timedelta


# Subcribtions

@app.route('/subcribe/monthly', methods=['GET', 'POST'])
def subcribe_monthly():
    if current_user.is_anonymous:
        flash('You need to login to subscribe', category='info')
        return redirect(url_for('login_page'))

    if current_user.is_subscribed():
        flash('You are already subscribed', category='info')
        return redirect(url_for('search', query='', page=1))

    user = User.query.get(current_user.id)
    user.subscribed_till = datetime.now() + timedelta(days=30)
    flash('Subcribed successfully for 1 month', category='success')
    db.session.commit()
    return redirect(url_for('search', query='', page=1))

@app.route('/subcribe/quarterly', methods=['GET', 'POST'])
def subcribe_quarterly():
    if current_user.is_anonymous:
        flash('You need to login to subscribe', category='info')
        return redirect(url_for('login_page'))

    if current_user.is_subscribed():
        flash('You are already subscribed', category='info')
        return redirect(url_for('search', query='', page=1))

    user = User.query.get(current_user.id)
    user.subscribed_till = datetime.now() + timedelta(days=90)
    flash('Subcribed successfully for 3 months', category='success')
    db.session.commit()
    return redirect(url_for('search', query='', page=1))

@app.route('/subcribe/yearly', methods=['GET', 'POST'])
def subcribe_yearly():
    if current_user.is_anonymous:
        flash('You need to login to subscribe', category='info')
        return redirect(url_for('login_page'))

    if current_user.is_subscribed():
        flash('You are already subscribed', category='info')
        return redirect(url_for('search', query='', page=1))

    user = User.query.get(current_user.id)
    user.subscribed_till = datetime.now() + timedelta(days=365)
    flash('Subcribed successfully for 1 year', category='success')
    db.session.commit()
    return redirect(url_for('search', query='', page=1))