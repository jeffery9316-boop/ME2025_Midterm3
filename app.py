from flask import Flask, request, jsonify, render_template
import sqlite3

# ===============================
#   測試時會 mock 的 db
# ===============================
class DummyDB:
    def get_product_names_by_category(self, category):
        return []

    def get_product_price(self, product):
        return 0

    def add_order(self, data):
        return True

    def delete_order(self, order_id):
        return True

db = DummyDB()

# ===============================
#   SQLite
# ===============================
DB_PATH = "core/order_management.db"

def get_conn():
    return sqlite3.connect(DB_PATH)

# ===============================
#   Flask
# ===============================
app = Flask(__name__)

# ===============================
#   首頁
# ===============================
@app.route("/")
def index():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT order_id, order_date, customer_name,
               product_name, product_price, product_amount,
               product_total, product_status, product_note
        FROM orders
        ORDER BY order_id ASC
    """)
    rows = cursor.fetchall()
    conn.close()
    return render_template("index.html", orders=rows)

# ===============================
#   /product API
# ===============================
@app.route("/product", methods=["GET", "POST", "DELETE"])
def product():

    # =======================================================
    # GET：提供商品清單 / 商品價格
    # =======================================================
    if request.method == "GET":
        category = request.args.get("category")
        product = request.args.get("product")

        # ---- 查商品名稱 ----
        if category:
            names = db.get_product_names_by_category(category)
            if names == []:  # mock 回傳空，正式查 SQLite
                conn = get_conn()
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT product_name
                    FROM product
                    WHERE product_category=?
                """, (category,))
                names = [row[0] for row in cursor.fetchall()]
                conn.close()
            return jsonify({"product": names})

        # ---- 查商品價格 ----
        if product:
            price = db.get_product_price(product)
            if price == 0:  # mock 回傳 0 → 查 SQLite
                conn = get_conn()
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT product_price
                    FROM product
                    WHERE product_name=?
                """, (product,))
                row = cursor.fetchone()
                price = row[0] if row else 0
                conn.close()
            return jsonify({"price": price})

        return jsonify({"error": "missing parameters"}), 400

    # =======================================================
    # POST：新增訂單（前端 JSON + 測試 form 都支援）
    # =======================================================
    if request.method == "POST":

        # ---- 測試用：request.form ----
        if request.form:
            form = request.form
            data = {
                "product_date": form.get("product-date"),
                "customer_name": form.get("customer-name"),
                "product_name": form.get("product-name"),
                "product_amount": form.get("product-amount"),
                "product_total": form.get("product-total"),
                "product_status": form.get("product-status"),
                "product_note": form.get("product-note"),
            }
            db.add_order(data)

            # 測試要求：必須回傳純文字
            return "Order placed successfully", 200

        # ---- 前端 JSON ----
        data = request.json

        customer_name = data["customer_name"]
        product_name = data["product_name"]
        product_price = data["product_price"]
        product_amount = data["product_amount"]
        product_total = data["product_total"]
        product_status = data["order_status"]
        product_note = data["product_note"]

        db.add_order(data)

        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO orders
            (order_date, customer_name, product_name,
             product_price, product_amount, product_total,
             product_status, product_note)
            VALUES
            (DATE('now'), ?, ?, ?, ?, ?, ?, ?)
        """, (customer_name, product_name, product_price,
              product_amount, product_total, product_status, product_note))
        conn.commit()
        conn.close()

        return jsonify({"status": "ok"})

    # =======================================================
    # DELETE：刪除訂單（測試和前端兩種都支援）
    # =======================================================
    if request.method == "DELETE":

        # ---- 測試用：取 Query String ----
        order_id = request.args.get("order_id")

        # ---- 前端用：JSON ----
        if not order_id:
            body = request.json
            order_id = body.get("order_id")

        db.delete_order(order_id)

        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM orders WHERE order_id=?", (order_id,))
        conn.commit()
        conn.close()

        return jsonify({"message": "Order deleted successfully"}), 200


if __name__ == "__main__":
    app.run(debug=True)
