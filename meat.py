#meat.py

meat_items = [
    {"name": "삼겹 구이용(1kg)", "price": 19000},
    {"name": "닭고기(1kg)", "price": 10000},
    {"name": "자..가자!", "price": 77777},
    {"name": "삼겹 보쌈용(1kg)", "price": 20000}
]

def update_meat_items(new_items):
    global meat_items
    meat_items = new_items
