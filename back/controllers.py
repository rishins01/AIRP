from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask import current_app as app
from sqlalchemy import text 
from back.backend import *  

@app.route("/")
def start():
    return redirect(url_for("login"))

@app.route("/home2",methods=["POST","GET"])
def home2():
    user_id = session.get('user_id')  
    products = db.session.execute(
        text("SELECT * FROM inventory where vendorId= :user_id"),{"user_id":user_id}
    ).fetchall()    
    return(render_template("home2.html",products=products))

@app.route("/home1",methods=["POST","GET"])
def home1():
    user_id = session.get('user_id')  
    userss = db.session.execute(
        text("SELECT * FROM user where type != 'Admin'")).fetchall()    
    return(render_template("home1.html",userss=userss))

@app.route("/home3", methods=["POST", "GET"])
def home():
    user_id = session.get("user_id")

    return render_template("home3.html", user_id=user_id,products=get_all_inventory(),sprod=get_search_rec(),vprod=get_view_rec())

@app.route("/cart")
def cart():
    user_id = session.get("user_id")  
    total_cost = get_cart_total(user_id) if user_id else 0
    cart_items = get_cart_items(user_id) if user_id else []  
    return render_template("cart.html", cart_items=cart_items,total_cost=total_cost)

def get_cart_items(user_id):
    results = db.session.execute(
        text("CALL get_cart_items(:user_id)"),
        {"user_id": user_id}
    ).fetchall()

    cart_items_list = []
    for row in results:
        cart_items_list.append(row._asdict())
    return cart_items_list

def get_cart_total(user_id):
    total_cost = db.session.execute(
        text("SELECT SUM(i.price * c.quantity) AS total_cost "
             "FROM inventory i JOIN cart c ON i.productID = c.productID "
             "WHERE c.id = :user_id"),
        {"user_id": user_id}
    ).scalar() 

    return total_cost or 0 

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password")
        user_type = request.form.get("utype")

        existing_user = db.session.execute(
            text("SELECT * FROM user WHERE username = :username"),
            {"username": username}
        ).fetchone()

        if not existing_user:
            db.session.execute(
                text("INSERT INTO user (username, password, type) VALUES (:username, :password, :user_type)"),
                {"username": username, "password": password, "user_type": user_type}
            )
            db.session.commit()
            flash("Signup successful! Please log in.", "success")
            return redirect(url_for("login"))
        else:
            flash("User already exists", "danger")

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password")

        user = db.session.execute(
            text("SELECT * FROM user WHERE username = :username"),
            {"username": username}
        ).fetchone()

        if user and user.password == password:
            session['user_id'] = user.id 
            if user.type=='Admin':
                return redirect(url_for("home1")) 
            elif user.type=='Retailer':
                return redirect(url_for("home2")) 
            elif user.type=='User':
                return redirect(url_for("home")) 
            else:
                return(render_template("error.html"))

        else:
            flash("Invalid username or password.", "danger")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))

@app.route("/register")
def reg():
    return render_template("register.html")

@app.route("/register_item", methods=["POST"])
def register_item():
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in to register an item.", "danger")
        return redirect(url_for("login"))

    item_name = request.form.get("nm").strip()
    description = request.form.get("desc").strip()
    price = request.form.get("price")
    quantity = request.form.get("quantity")
    image_url = request.form.get("img").strip()
    category = request.form.get("category") 

    db.session.execute(
        text("INSERT INTO inventory (vendorId, productname, description, price, quantity, image, category) "
             "VALUES (:vendor_id, :productname, :description, :price, :quantity, :image, :category)"),
        {"vendor_id": user_id, "productname": item_name, "description": description, 
         "price": price, "quantity": quantity, "image": image_url, "category": category}
    )
    db.session.commit()

    return redirect(url_for("home2"))

@app.route("/update_inventory/<int:product_id>/<action>", methods=["POST"])
def update_inventory(product_id, action):
    user_id = session.get("user_id")
    
    if not user_id:
        flash("You need to be logged in to update inventory.", "danger")
        return redirect(url_for("login"))

    if action == 'increase':
        db.session.execute(
            text("UPDATE inventory SET quantity = quantity + 1 WHERE productID = :product_id AND vendorId = :user_id"),
            {"user_id": user_id, "product_id": product_id}
        )
    
    elif action == 'decrease':
        db.session.execute(
            text("UPDATE inventory SET quantity = GREATEST(quantity - 1, 1) WHERE productID = :product_id AND vendorId = :user_id"),
            {"user_id": user_id, "product_id": product_id}
        )
    
    elif action == 'remove':
        db.session.execute(
            text("DELETE FROM cart WHERE productID = :product_id"),
            {"product_id": product_id}
        )
        db.session.execute(
            text("DELETE FROM orders WHERE productID = :product_id"),
            {"product_id": product_id}
        )
        db.session.execute(
            text("DELETE FROM inventory WHERE productID = :product_id AND vendorId = :user_id"),
            {"user_id": user_id, "product_id": product_id}
        )

    db.session.commit()
    return redirect(url_for("home2"))

@app.route("/add_to_cart/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    user_id = session.get('user_id')  
    if user_id:
        try:
            existing_cart_item = db.session.execute(
                text("SELECT * FROM cart WHERE id = :user_id AND productID = :product_id"),
                {"user_id": user_id, "product_id": product_id}
            ).fetchone()

            if existing_cart_item:
                db.session.execute(
                    text("UPDATE cart SET quantity = quantity + 1 WHERE id = :user_id AND productID = :product_id"),
                    {"user_id": user_id, "product_id": product_id}
                )
            else:
                db.session.execute(
                    text("INSERT INTO cart (id, productID, quantity) VALUES (:user_id, :product_id, 1)"),
                    {"user_id": user_id, "product_id": product_id}
                )
            db.session.commit()
        except Exception as e:
            db.session.rollback()  # Rollback the session if an error occurs
            flash("quantity in cart exceeds available stock", "danger")  # Flash the error message to the user
            return redirect(url_for("cart"))  # Redirect back to cart
    else:
        flash("You need to be logged in to add items to the cart.", "danger")
    return redirect(url_for("home"))

@app.route("/update_cart/<int:product_id>/<action>", methods=["POST"])
def update_cart(product_id, action):
    user_id = session.get("user_id")  

    try:
        if action == 'increase':
            db.session.execute(
                text("UPDATE cart SET quantity = quantity + 1 WHERE id = :user_id AND productID = :product_id"),
                {"user_id": user_id, "product_id": product_id}
            )
        elif action == 'decrease':
            db.session.execute(
                text("UPDATE cart SET quantity = GREATEST(quantity - 1, 1) WHERE id = :user_id AND productID = :product_id"),
                {"user_id": user_id, "product_id": product_id}
            )
        elif action == 'remove':
            db.session.execute(
                text("DELETE FROM cart WHERE id = :user_id AND productID = :product_id"),
                {"user_id": user_id, "product_id": product_id}
            )

        db.session.commit() 
    except Exception as e:
        db.session.rollback() 
        flash("quantity in cart exceeds available stock", "danger") 
        return redirect(url_for("cart")) 

    return redirect(url_for("cart")) 

def get_all_inventory():
    results = db.session.execute(
        text("SELECT * FROM inventory")
    ).fetchall()
    return results

@app.route("/review")
def rev():
    user_id = session.get("user_id")  
    cart_items = get_cart_items(user_id) if user_id else []  
    total_cost = get_cart_total(user_id) if user_id else 0
    return(render_template("review.html", cart_items=cart_items,total_cost=total_cost))

@app.route("/pay",methods=["POST","GET"])
def pay():
    return(render_template("pay.html"))

@app.route("/success", methods=["POST", "GET"])
def success():
    if request.method == "POST":
        user_id = session.get("user_id")
        
        if user_id:
            cart_items = get_cart_items(user_id)
            
            time=datetime.datetime.utcnow()
            for item in cart_items:
                db.session.execute(
                    text("INSERT INTO orders (id, productID, quantity, status,times) VALUES (:user_id, :product_id, :quantity, :status,:timest)"),
                    {"user_id": user_id, "product_id": item["productID"], "quantity": item["quantity"], "status": "Order Placed","timest":time}
                )
            
            db.session.execute(
                text("DELETE FROM cart WHERE id = :user_id"),
                {"user_id": user_id}
            )
            
            db.session.commit()
        
        return render_template("success.html")
    
    return(render_template("error.html"))

@app.route("/searchres")
def searchres():
    return(render_template("searchres.html"))

@app.route("/search_inventory", methods=["POST"])
def search_inventory():
    user_id = session.get('user_id')
    search_term = request.form.get("search_term").strip()

    products = db.session.execute(
        text("SELECT * FROM inventory WHERE "
             "productname LIKE :search_term OR "
             "description LIKE :search_term OR "
             "category LIKE :search_term"),
        {"search_term": f"%{search_term}%"}
    ).fetchall()

    existing_entry = db.session.execute(
        text("SELECT 1 FROM recently_searched WHERE id = :user_id AND query = :query"),
        {"user_id": user_id, "query": search_term}
    ).fetchone()

    if existing_entry:
        db.session.execute(
            text("CALL upsert_recently_searched(:user_id, :query, :ts)"),
            {"user_id": user_id, "query": search_term, "ts": datetime.datetime.utcnow()}
        )
    else:
        db.session.execute(
            text("INSERT INTO recently_searched (id, query, timestamp) VALUES (:user_id, :query, :ts)"),
            {"user_id": user_id, "query": search_term, "ts": datetime.datetime.utcnow()}
        )

    db.session.commit()

    return render_template("searchres.html", products=products,user_id=user_id)

def get_search_rec():
    user_id = session.get('user_id')
    query=f'select query from recently_searched where id = {user_id} order by timestamp desc limit 5;'

    queries=db.session.execute(text(query))

    products=[]

    for q in queries:

        products += db.session.execute(
        text("SELECT * FROM inventory WHERE "
             "productname LIKE :search_term OR "
             "description LIKE :search_term OR "
             "category LIKE :search_term"),
        {"search_term": f"%{q[0]}%"}
    ).fetchall()
        
        if len(products)>=5:
            break

    print(len(products))

    return products if len(products)<=5 else products[:5]

def get_view_rec():
    user_id = session.get('user_id')
    query=f'select * from recently_viewed r join inventory i on r.productid=i.productid where id = {user_id} order by timestamp desc limit 5;	;'

    products=db.session.execute(text(query)).fetchall()

    return products if len(products)<=5 else products[:5]

@app.route("/orders")
def orders():
    user_id = session.get('user_id')  
    orderss = db.session.execute(
        text("select id,productname,o.quantity,status,image,times  from orders o join inventory i on o.productId=i.productId where id= :user_id  order by times asc , id asc ;"),{"user_id":user_id}).fetchall()  

    x=dict()

    for i in orderss:
        if i[-1] in x:
            x[i[-1]].append([i[1],i[2],i[3],i[4]])
        else:
            x[i[-1]]=[[i[1],i[2],i[3],i[4]]]
        pass

    print(x)
    return(render_template("orders.html",orders=x))


@app.route("/orders1/<int:user_id>", methods=["GET", "POST"])
def orders1(user_id):
    try:
        print(f"Fetching orders for user_id: {user_id}")
        
        orderss = db.session.execute(
            text("SELECT id, productname, o.quantity, status, image, times "
                 "FROM orders o JOIN inventory i ON o.productId = i.productId "
                 "WHERE id = :user_id "
                 "ORDER BY times ASC, id ASC;")
            .bindparams(user_id=user_id) 
        ).fetchall()

        x = {}
        for i in orderss:
            if i[-1] in x:
                x[i[-1]].append([i[1], i[2], i[3], i[4]])
            else:
                x[i[-1]] = [[i[1], i[2], i[3], i[4]]]

        print("Orders data:", x)
        
        return render_template("orders copy.html", orders=x)
    
    except Exception as e:
        print(f"Error fetching orders for user {user_id}: {e}")
        flash("An error occurred while fetching the orders.", "error")
        return redirect(url_for('admin_page'))  


@app.route('/update_recently_viewed', methods=['POST'])
def update_recently_viewed():
        user_id = request.form['user_id']
        product_id = request.form['product_id']

        query = """
            SELECT * FROM RecentlyViewed
            WHERE user_id = :user_id AND productID = :product_id
        """
        existing_entry = db.session.execute(query, {'user_id': user_id, 'product_id': product_id}).fetchone()

        if not existing_entry:
            insert_query = """
                INSERT INTO RecentlyViewed 
                (user_id, productID, timestamp)
                VALUES (:user_id, :product_id, :ts)
            """
            db.session.execute(insert_query, {'user_id': user_id, 'product_id': product_id, "ts": datetime.datetime.utcnow()})
            db.session.commit()
        else:
            update_query = """
                UPDATE RecentlyViewed
                SET timestamp = :ts
                WHERE user_id = :user_id AND productID = :product_id
            """
            db.session.execute(update_query, {'user_id': user_id, 'product_id': product_id, "ts": datetime.datetime.utcnow()})
            db.session.commit()

        return redirect(url_for('home'))


@app.route('/search', methods=['GET'])
def search_by_category():
    category = request.args.get('category', None)
    if not category:
        return "Please specify a category to search.", 400

    try:
        query = """
            SELECT productname, description, price, category
            FROM inventory
            WHERE category = :category
            AND productID IN (
                SELECT product_id
                FROM orders
                WHERE user_id IN (
                    SELECT user_id
                    FROM users
                    WHERE purchase_history IS NOT NULL
                )
            )
        """
        results = db.engine.execute(query, {'category': category})

        products = []
        for row in results:
            products.append({
                'productname': row['productname'],
                'description': row['description'],
                'price': row['price'],
                'category': row['category']
            })
        return render_template('search_results.html', products=products, category=category)

    except Exception as e:
        print(f"Error executing query: {e}")
        return "An error occurred while processing your request.", 500


