from web import *

@login_manager.user_loader
def load_user(user_id):
    try:
        return db.session.get(User,int(user_id))
    except (ValueError, TypeError):
        return None 

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'images/favicon/favicon.ico', mimetype='image/vnd.microsoft.icon')

######## Product pages ########

from routes.product import *

######## User pages ########
    
from routes.account import *

######## Admin pages ########

from routes.admin import *

######## Other pages ########

from routes.other import *

######## Error pages ########

from routes.errors import * 
 
if __name__ == "__main__":
    app.run(debug=True)
