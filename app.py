from flask import Flask, render_template, request, redirect, url_for, flash, session
from people import get_customer_by_id
from meat import meat_items
from datetime import datetime  # 주문 시간을 추가하기 위해 datetime을 임포트

app = Flask(__name__)
app.secret_key = "your_secret_key"  # 세션을 위한 비밀키 설정

# 주문 내역을 저장할 딕셔너리
orders = {}
delivery_orders = {}

# 기본 홈 페이지 (주문 선택)
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        customer_id = request.form.get("customer_id")
        action = request.form.get("action")
        customer = get_customer_by_id(customer_id)

        if customer:
            if action == "direct_pickup":
                return redirect(url_for("hand", customer_id=customer_id))
            elif action == "delivery_pickup":
                return redirect(url_for("car", customer_id=customer_id))
        else:
            flash("올바르지 않은 아이디입니다.")
    return render_template("index.html")

# 직접 수령 주문 페이지
@app.route("/hand/<customer_id>", methods=["GET", "POST"])
def hand(customer_id):
    customer = get_customer_by_id(customer_id)
    if not customer:
        flash("올바르지 않은 아이디입니다.")
        return redirect(url_for("index"))

    existing_order = orders.get(customer_id)

    if request.method == "POST":
        if existing_order:
            flash("이미 주문을 완료한 고객입니다.")
            return redirect(url_for("hand", customer_id=customer_id))

        selected_items = request.form.getlist("items")
        quantities = request.form.getlist("quantities")
        order_details = []
        total_price = 0

        for item, quantity in zip(selected_items, quantities):
            quantity = int(quantity)
            meat_item = next(m for m in meat_items if m["name"] == item)
            price = meat_item["price"] * quantity
            order_details.append({"item": item, "quantity": quantity, "price": price})
            total_price += price

        # 주문 시간을 추가하여 주문 내역에 저장
        order_time = datetime.now().strftime("%Y년 %m월 %d일 %H시 %M분")
        orders[customer_id] = {"customer": customer, "details": order_details, "total_price": total_price, "order_time": order_time}
        flash("주문이 완료되었습니다.")
        return redirect(url_for("hand", customer_id=customer_id))
    
    return render_template("hand.html", customer=customer, meat_items=meat_items, existing_order=existing_order)

# 주문 삭제
@app.route("/delete_order/<customer_id>", methods=["POST"])
def delete_order(customer_id):
    if customer_id in orders:
        del orders[customer_id]
        flash("주문이 취소되었습니다.")
    return redirect(url_for("hand", customer_id=customer_id))

# 배달 수령 주문 페이지
@app.route("/car/<customer_id>", methods=["GET", "POST"])
def car(customer_id):
    customer = get_customer_by_id(customer_id)
    if not customer:
        flash("올바르지 않은 아이디입니다.")
        return redirect(url_for("index"))

    existing_delivery_order = delivery_orders.get(customer_id)

    if request.method == "POST":
        sender_name = request.form.get("sender_name")
        sender_contact = request.form.get("sender_contact")
        sender_address = request.form.get("sender_address")
        receiver_name = request.form.get("receiver_name")
        receiver_contact = request.form.get("receiver_contact")
        receiver_address = request.form.get("receiver_address")

        # 필수 정보 체크
        if not all([sender_name, sender_contact, sender_address, receiver_name, receiver_contact, receiver_address]):
            flash("주문 정보를 올바르게 입력해주십시오")
            return redirect(url_for("car", customer_id=customer_id))

        if existing_delivery_order:
            flash("이미 배달 주문을 완료한 고객입니다.")
            return redirect(url_for("car", customer_id=customer_id))

        selected_items = request.form.getlist("items")
        quantities = request.form.getlist("quantities")

        order_details = []
        total_price = 0

        for item, quantity in zip(selected_items, quantities):
            quantity = int(quantity)
            meat_item = next(m for m in meat_items if m["name"] == item)
            price = meat_item["price"] * quantity
            order_details.append({"item": item, "quantity": quantity, "price": price})
            total_price += price

        delivery_orders[customer_id] = {
            "customer": customer,
            "details": order_details,
            "total_price": total_price,
            "sender": {
                "name": sender_name,
                "contact": sender_contact,
                "address": sender_address
            },
            "receiver": {
                "name": receiver_name,
                "contact": receiver_contact,
                "address": receiver_address
            }
        }
        flash("배달 주문이 완료되었습니다.")
        return redirect(url_for("car", customer_id=customer_id))
    
    return render_template("car.html", customer=customer, meat_items=meat_items, existing_delivery_order=existing_delivery_order)

# 배달 주문 삭제
@app.route("/delete_delivery_order/<customer_id>", methods=["POST"])
def delete_delivery_order(customer_id):
    if customer_id in delivery_orders:
        del delivery_orders[customer_id]
        flash("배달 주문이 취소되었습니다.")
    return redirect(url_for("car", customer_id=customer_id))

# 관리자 페이지
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        # 관리자 비밀번호 입력 폼
        return render_template("admin.html")
    return render_template("admin.html")

# 관리자 비밀번호 검증 및 페이지 이동
@app.route("/admin_action", methods=["POST"])
def admin_action():
    password = request.form.get("password")
    action = request.form.get("action")

    if password == "admin123":  # 비밀번호 검증
        if action == "view_orders":
            return redirect(url_for("view_orders"))
        elif action == "co":
            return redirect(url_for("co"))
    else:
        flash("잘못된 관리자 비밀번호입니다.")
        return redirect(url_for("admin"))

# 주문 내역 보기
@app.route("/view_orders", methods=["GET"])
def view_orders():
    # 관리자가 로그인한 상태일 때만 접근 가능
    return render_template("view_orders.html", orders=orders)

# 배달 수령 주문 내역 보기
@app.route("/co", methods=["GET"])
def co():
    # 관리자가 로그인한 상태일 때만 접근 가능
    return render_template("co.html", delivery_orders=delivery_orders)

if __name__ == "__main__":
    app.run(debug=True)
