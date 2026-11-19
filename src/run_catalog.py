import os
import sys
from flask import Flask, flash, redirect, render_template, request, url_for

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
TEMPLATES_DIR = os.path.join(SRC_DIR, "templates")

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

import product

product.init_catalog_tables()

app = Flask(__name__, template_folder=TEMPLATES_DIR)
app.secret_key = "tv2-catalog-pos-secret-key"


@app.route("/")
def index():
    return redirect(url_for("catalog"))


@app.route("/catalog", methods=["GET"])
def catalog():
    return render_template(
        "catalog.html",
        categories=product.get_all_categories(),
        active_categories=product.get_active_categories(),
        products=product.get_all_products(),
    )


@app.route("/catalog/category/add", methods=["POST"])
def add_category_route():
    ok, msg, cat = product.add_category(
        name=request.form.get("name", ""),
        description=request.form.get("description", ""),
    )
    flash(msg, cat)
    return redirect(url_for("catalog"))


@app.route("/catalog/category/<int:category_id>/toggle", methods=["POST"])
def toggle_category_route(category_id: int):
    ok, msg, cat = product.toggle_category_status(category_id)
    flash(msg, cat)
    return redirect(url_for("catalog"))


@app.route("/catalog/product/add", methods=["POST"])
def add_product_route():
    ok, msg, cat = product.add_product(
        sku=request.form.get("sku", ""),
        name=request.form.get("name", ""),
        category_id=request.form.get("category_id", ""),
        price=request.form.get("price", "0"),
        stock=request.form.get("stock", "0"),
        description=request.form.get("description", ""),
    )
    flash(msg, cat)
    return redirect(url_for("catalog"))


@app.route("/catalog/product/<int:product_id>/edit", methods=["GET", "POST"])
def edit_product_route(product_id: int):
    current_product = product.get_product_by_id(product_id)
    if not current_product:
        flash("Không tìm thấy sản phẩm cần sửa.", "danger")
        return redirect(url_for("catalog"))

    if request.method == "POST":
        ok, msg, cat = product.update_product(
            product_id=product_id,
            sku=request.form.get("sku", ""),
            name=request.form.get("name", ""),
            category_id=request.form.get("category_id", ""),
            price=request.form.get("price", "0"),
            stock=request.form.get("stock", "0"),
            description=request.form.get("description", ""),
            is_active=request.form.get("is_active", "0"),
        )
        flash(msg, cat)
        if ok:
            return redirect(url_for("catalog"))
        current_product = product.get_product_by_id(product_id)

    return render_template(
        "edit_product.html",
        product=current_product,
        categories=product.get_all_categories(),
    )


@app.route("/catalog/product/<int:product_id>/toggle", methods=["POST"])
def toggle_product_route(product_id: int):
    ok, msg, cat = product.toggle_product_status(product_id)
    flash(msg, cat)
    return redirect(url_for("catalog"))


@app.route("/pos-search", methods=["GET"])
def pos_search():
    keyword = request.args.get("q", "").strip()
    selected_category_id = request.args.get("category_id", "").strip()
    only_in_stock = request.args.get("in_stock", "") in ("1", "true", "on")
    product_id_raw = request.args.get("product_id", "").strip()

    results = product.search_products_pos(
        keyword=keyword,
        category_id=selected_category_id,
        only_in_stock=only_in_stock,
    )

    selected_product = None
    if product_id_raw.isdigit():
        selected_product = product.get_product_by_id(int(product_id_raw))

    return render_template(
        "pos_search.html",
        categories=product.get_all_categories(),
        products=results,
        keyword=keyword,
        selected_category_id=selected_category_id,
        only_in_stock=only_in_stock,
        selected_product=selected_product,
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5002, debug=False)
