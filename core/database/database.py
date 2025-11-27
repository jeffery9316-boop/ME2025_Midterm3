import datetime
import os
import random
import sqlite3


class Database():
    def __init__(self, db_filename="order_management.db"):
        # 資料庫檔案路徑
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(base_dir, db_filename)

        # 初始化資料庫（建立資料表）
        self.initialize_database()

    # =============================
    # 建立資料表（重要）
    # =============================
    def initialize_database(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        # 商品資料（種類、名稱、價格）
        cur.execute("""
            CREATE TABLE IF NOT EXISTS commodity (
                category TEXT,
                product TEXT PRIMARY KEY,
                price INTEGER
            )
        """)

        # 訂單資料
        cur.execute("""
            CREATE TABLE IF NOT EXISTS order_list (
                order_id TEXT PRIMARY KEY,
                product_date TEXT,
                customer_name TEXT,
                product_name TEXT,
                product_amount INTEGER,
                product_total INTEGER,
                product_status TEXT,
                product_note TEXT
            )
        """)

        conn.commit()
        conn.close()

    # =============================
    # 產生訂單編號
    # =============================
    @staticmethod
    def generate_order_id() -> str:
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y%m%d%H%M%S")
        random_num = random.randint(1000, 9999)
        return f"OD{timestamp}{random_num}"

    # =============================
    # 依種類取得商品名稱
    # =============================
    def get_product_names_by_category(self, category):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute(
            "SELECT product FROM commodity WHERE category = ?",
            (category,)
        )
        rows = cur.fetchall()
        conn.close()

        return [row[0] for row in rows]  # 回傳名稱 list

    # =============================
    # 取得商品價格
    # =============================
    def get_product_price(self, product):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute(
            "SELECT price FROM commodity WHERE product = ?",
            (product,)
        )
        row = cur.fetchone()
        conn.close()

        if row is None:
            return None
        return row[0]

    # =============================
    # 新增訂單
    # =============================
    def add_order(self, order_data):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        order_id = self.generate_order_id()

        cur.execute(
            """
            INSERT INTO order_list (
                order_id, product_date, customer_name, product_name,
                product_amount, product_total, product_status, product_note
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                order_id,
                order_data["product_date"],
                order_data["customer_name"],
                order_data["product_name"],
                order_data["product_amount"],
                order_data["product_total"],
                order_data["product_status"],
                order_data.get("product_note", "")
            )
        )

        conn.commit()
        conn.close()

        return order_id

    # =============================
    # 查詢所有訂單（JOIN 價格）
    # =============================
        # 4. 取得所有訂單 + 每筆的 price
    def get_all_orders(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute(
            """
            SELECT 
                o.order_id,       -- 0
                o.product_date,   -- 1
                o.customer_name,  -- 2
                o.product_name,   -- 3
                c.price,          -- 4
                o.product_amount, -- 5
                o.product_total,  -- 6
                o.product_status, -- 7
                o.product_note    -- 8
            FROM order_list AS o
            LEFT JOIN commodity AS c
                ON o.product_name = c.product
            ORDER BY o.product_date DESC, o.order_id DESC
            """
        )

        rows = cur.fetchall()   # list of tuple
        conn.close()

        return rows


    # =============================
    # 刪除訂單
    # =============================
    def delete_order(self, order_id):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute(
            "DELETE FROM order_list WHERE order_id = ?",
            (order_id,)
        )

        conn.commit()
        conn.close()
