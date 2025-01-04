# people.py

customers = [
    {"id": "132101451", "name": "나수빈", "branch": "만안지점"},
    {"id": "132301452", "name": "나수진", "branch": "호평지점"}
]

def get_customer_by_id(customer_id):
    return next((customer for customer in customers if customer["id"] == customer_id), None)
