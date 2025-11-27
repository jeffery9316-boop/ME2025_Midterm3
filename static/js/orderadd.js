// =========================
//  彈出視窗開關
// =========================

function open_input_table() {
    const modal = document.getElementById("addModal");
    if (modal) {
        modal.style.display = "block";
    }

    const form = document.getElementById("orderForm");
    if (form) {
        form.reset();
        const totalInput = document.getElementById("totalInput");
        if (totalInput) totalInput.value = "";
    }
}

function close_input_table() {
    const modal = document.getElementById("addModal");
    if (modal) {
        modal.style.display = "none";
    }
}


// =========================
//  商品種類 / 單價 / 小計
// =========================

function selectCategory() {
    const categorySelect = document.getElementById("categorySelect");
    const productSelect  = document.getElementById("productSelect");
    const priceInput     = document.getElementById("priceInput");
    const totalInput     = document.getElementById("totalInput");

    if (!categorySelect || !productSelect) return;

    const category = categorySelect.value;

    // 先清空商品選單與金額
    productSelect.innerHTML = '<option value="" disabled selected>請選擇商品</option>';
    if (priceInput) priceInput.value = "";
    if (totalInput) totalInput.value = "";

    if (!category) return;

    fetch(`/product?category=${encodeURIComponent(category)}`)
        .then(response => response.json())
        .then(data => {
            const products = data.product || [];
            products.forEach(name => {
                const opt = document.createElement("option");
                opt.value = name;
                opt.textContent = name;
                productSelect.appendChild(opt);
            });
        })
        .catch(err => {
            console.error("載入商品清單失敗：", err);
        });
}

function selectProduct() {
    const productSelect = document.getElementById("productSelect");
    const priceInput    = document.getElementById("priceInput");

    if (!productSelect || !priceInput) return;

    const product = productSelect.value;
    if (!product) {
        priceInput.value = "";
        return;
    }

    fetch(`/product?product=${encodeURIComponent(product)}`)
        .then(response => response.json())
        .then(data => {
            const price = data.price || 0;
            priceInput.value = price;
            countTotal();
        })
        .catch(err => {
            console.error("載入商品價格失敗：", err);
        });
}

function countTotal() {
    const priceInput  = document.getElementById("priceInput");
    const amountInput = document.getElementById("amountInput");
    const totalInput  = document.getElementById("totalInput");

    if (!priceInput || !amountInput || !totalInput) return;

    const price  = parseInt(priceInput.value, 10)  || 0;
    const amount = parseInt(amountInput.value, 10) || 0;

    totalInput.value = price * amount;
}


// =========================
//  新增訂單
// =========================

function add_order() {
    const customer_name = document.getElementById("customer_name").value.trim();
    const product_name  = document.getElementById("productSelect").value;
    const product_price = parseInt(document.getElementById("priceInput").value, 10) || 0;
    const product_amount = parseInt(document.getElementById("amountInput").value, 10) || 0;
    const product_total  = parseInt(document.getElementById("totalInput").value, 10) || 0;
    const order_status   = document.getElementById("status").value;
    const product_note   = document.getElementById("note").value.trim();

    if (!customer_name || !product_name || product_amount <= 0) {
        alert("請確認：客戶名稱、商品名稱、數量 都已填寫正確。");
        return;
    }

    fetch("/product", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            customer_name,
            product_name,
            product_price,
            product_amount,
            product_total,
            order_status,
            product_note
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("後端回傳錯誤：" + response.status);
        }
        return response.json();
    })
    .then(data => {
        if (data.status === "ok") {
            close_input_table();
            window.location.reload();
        } else {
            alert("新增訂單失敗：" + (data.message || "未知錯誤"));
        }
    })
    .catch(err => {
        console.error("新增訂單失敗：", err);
        alert("新增訂單失敗，請稍後再試。");
    });
}


// =========================
//  刪除訂單
// =========================

function delete_data(order_id) {
    if (!order_id) return;

    if (!confirm("確定要刪除這筆訂單嗎？")) {
        return;
    }

    fetch("/product", {
        method: "DELETE",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ order_id })
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === "ok") {
                window.location.reload();
            } else {
                alert("刪除失敗：" + (data.message || "未知錯誤"));
            }
        })
        .catch(err => {
            console.error("刪除訂單失敗：", err);
        });
}
