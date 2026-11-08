from flask import Flask, render_template, request, redirect, url_for, flash
from customer import CustomerManager

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # cần để flash message hoạt động

cm = CustomerManager()

@app.route('/')
def home():
    customers = cm.get_all_customers()
    return render_template('index.html', customers=customers)

@app.route('/add', methods=['POST'])
def add_customer():
    customer_id = request.form.get('id').strip()
    name = request.form.get('name').strip()
    phone = request.form.get('phone').strip()
    email = request.form.get('email').strip()
    address = request.form.get('address').strip()

    if not customer_id or not name or not phone:
        flash("Vui lòng nhập đầy đủ ID, tên và số điện thoại.", "warning")
        return redirect(url_for('home'))

    success, msg = cm.add_customer(customer_id, name, phone, email, address)
    flash(msg, "success" if success else "danger")
    return redirect(url_for('home'))

@app.route('/search', methods=['GET'])
def search_customer():
    phone = request.args.get('phone', '').strip()
    if not phone:
        flash("Vui lòng nhập số điện thoại để tìm.", "warning")
        return redirect(url_for('home'))
    customer = cm.search_customer(phone)
    if customer:
        return render_template('search.html', customer=customer)
    else:
        flash("Không tìm thấy khách hàng phù hợp.", "info")
        return redirect(url_for('home'))

@app.route('/delete/<customer_id>', methods=['POST'])
def delete_customer(customer_id):
    success, msg = cm.delete_customer(customer_id)
    flash(msg, "success" if success else "danger")
    return redirect(url_for('home'))

@app.route('/edit/<customer_id>', methods=['GET', 'POST'])
def edit_customer(customer_id):
    if request.method == 'POST':
        name = request.form.get('name').strip()
        phone = request.form.get('phone').strip()
        email = request.form.get('email').strip()
        address = request.form.get('address').strip()

        if not name or not phone:
            flash("Tên và số điện thoại không được để trống!", "warning")
            return redirect(url_for('edit_customer', customer_id=customer_id))

        success, msg = cm.update_customer(customer_id, name=name, phone=phone, email=email, address=address)
        flash(msg, "success" if success else "danger")
        if success:
            return redirect(url_for('home'))
        else:
            return redirect(url_for('edit_customer', customer_id=customer_id))
    else:
        customer = None
        all_customers = cm.get_all_customers()
        for c in all_customers:
            if c['id'] == customer_id:
                customer = c
                break
        if customer is None:
            flash("Không tìm thấy khách hàng để sửa.", "danger")
            return redirect(url_for('home'))
        return render_template('edit.html', customer=customer)


if __name__ == "__main__":
    app.run(debug=True)
