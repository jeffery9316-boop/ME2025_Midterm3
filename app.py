from flask import Flask, request, jsonify, render_template
import sqlite3

# ===============================
#   測試時會 mock 的 db 物件
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


db = DummyDB()   # 測試時會被 mock


# ===============================
#   SQLite 設定
# ===============================
DB_PATH = "core/order_management.db"

def get_conn():
    return sqlite3.connect(DB_PATH)


# ===============================
#   Flask App
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

    orders = cursor.fetchall()
    conn.close()

    return render_template("index.html", orders=orders)


# ===============================
#   /product API
# ===============================
@app.route("/product", methods=["GET", "POST", "DELETE"])
def product():

    # -----------------------------------------
    # GET：取得商品列表或商品價格
    # -----------------------------------------
    if request.method == "GET":
        category = request.args.get("category")
        product = request.args.get("product")

        # ---- 查商品名稱 ----
        if category:
            names = db.get_product_names_by_category(category)

            # mock 回傳空 → 用 SQLite 查
            if names == []:
                conn = get_conn()
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT product_name
                    FROM product
                    WHERE product_category=?
                """, (category,))
                names = [r[0] for r in cursor.fetchall()]
                conn.close()

            return jsonify({"product": names})

        # ---- 查商品價格 ----
        if product:
            price = db.get_product_price(product)

            # mock price=0 → 用 SQLite 查
            if price == 0:
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

    # -----------------------------------------
    # POST：新增訂單（接 JSON）
    # -----------------------------------------
    if request.method == "POST":

        data = request.json

        customer_name  = data.get("customer_name")
        product_name   = data.get("product_name")
        product_price  = data.get("product_price")
        product_amount = data.get("product_amount")
        product_total  = data.get("product_total")
        order_status   = data.get("order_status")
        product_note   = data.get("product_note")

        # 給 mock 用
        db.add_order(data)

        # ----- 正式寫入 SQLite -----
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
              product_amount, product_total, order_status, product_note))

        conn.commit()
        conn.close()

        return jsonify({"status": "ok"})

    # -----------------------------------------
    # DELETE：刪除訂單
    # -----------------------------------------
    if request.method == "DELETE":
        data = request.json
        order_id = data.get("order_id")

        db.delete_order(order_id)

        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM orders WHERE order_id=?", (order_id,))
        conn.commit()
        conn.close()

        return jsonify({"message": "Order deleted successfully"}), 200


if __name__ == "__main__":
    app.run(debug=True)
