#app.py 이 주석은 삭제하지 말 것

from flask import Flask, render_template, request, redirect, url_for, flash, session
from people import get_customer_by_id
from meat import meat_items
from datetime import datetime
import pytz  # 추가

app = Flask(__name__)
app.secret_key = "your_secret_key"  # 세션을 위한 비밀키 설정

# 주문 내역을 저장할 딕셔너리
orders = {}
delivery_orders = {}

# 한국 시간으로 변환하는 함수
def get_korean_time():
    korean_tz = pytz.timezone('Asia/Seoul')
    return datetime.now(korean_tz).strftime('%Y년 %m월 %d일 %H시 %M분')

# 배달 수령 주문 총 금액에 배송비를 추가하는 함수
DELIVERY_FEE = 5000  # 현재 설정된 배송비
def calculate_total_with_delivery_fee(total_price):
    return total_price + DELIVERY_FEE  # 향후 배송비가 변경될 경우 이 값을 수정


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
        recognition_number = request.form.get("recognition_number")
        order_details = []
        total_price = 0

        for item, quantity in zip(selected_items, quantities):
            quantity = int(quantity)
            meat_item = next(m for m in meat_items if m["name"] == item)
            price = meat_item["price"] * quantity
            order_details.append({"item": item, "quantity": quantity, "price": price})
            total_price += price

        order_time = get_korean_time()  # 한국 시간으로 주문 시간 설정
        orders[customer_id] = {
            "customer": customer,
            "details": order_details,
            "total_price": total_price,
            "order_time": order_time,
            "recognition_number": recognition_number,
        }
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

    # 기존 주문 내역을 가져옵니다. 여러 건의 주문이 가능하도록 리스트로 변경합니다.
    existing_delivery_orders = delivery_orders.get(customer_id, [])

    if request.method == "POST":
        sender_name = request.form.get("sender_name")
        sender_contact = request.form.get("sender_contact")
        sender_address = request.form.get("sender_address")
        receiver_name = request.form.get("receiver_name")
        receiver_contact = request.form.get("receiver_contact")
        receiver_address = request.form.get("receiver_address")
        recognition_number = request.form.get("recognition_number")

        if not all([sender_name, sender_contact, sender_address, receiver_name, receiver_contact, receiver_address, recognition_number]):
            flash("주문 정보를 올바르게 입력해주십시오")
            return redirect(url_for("car", customer_id=customer_id))

        # 여러 개의 주문을 받을 수 있도록 폼 데이터를 처리합니다.
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

        total_price_with_delivery = calculate_total_with_delivery_fee(total_price)

        order_time = get_korean_time()
        new_order = {
            "customer": customer,
            "details": order_details,
            "total_price": total_price_with_delivery,  # 배송비 포함된 총 금액 저장
            "sender": {
                "name": sender_name,
                "contact": sender_contact,
                "address": sender_address
            },
            "receiver": {
                "name": receiver_name,
                "contact": receiver_contact,
                "address": receiver_address
            },
            "recognition_number": recognition_number,
            "order_time": order_time
        }

        # 고객의 배달 주문 목록에 새로운 주문을 추가합니다.
        if customer_id not in delivery_orders:
            delivery_orders[customer_id] = []
        delivery_orders[customer_id].append(new_order)

        flash("배달 주문이 완료되었습니다.")
        return redirect(url_for("car", customer_id=customer_id))

    return render_template("car.html", customer=customer, meat_items=meat_items, existing_delivery_orders=existing_delivery_orders)




# 배달 주문 삭제
@app.route("/delete_delivery_order/<customer_id>/<order_index>", methods=["POST"])
def delete_delivery_order(customer_id, order_index):
    if customer_id in delivery_orders:
        try:
            # 고객의 배달 주문 리스트에서 해당 주문 인덱스를 찾아 삭제
            del delivery_orders[customer_id][int(order_index)]
            flash("배달 주문이 취소되었습니다.")
        except IndexError:
            flash("주문을 찾을 수 없습니다.")
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
    return render_template("view_orders.html", orders=orders, meat_items=meat_items)

# 배달 수령 주문 내역 보기
@app.route("/co", methods=["GET"])
def co():
    # 관리자가 로그인한 상태일 때만 접근 가능
    return render_template("co.html", delivery_orders=delivery_orders, meat_items=meat_items)


if __name__ == "__main__":
    app.run(debug=True)
