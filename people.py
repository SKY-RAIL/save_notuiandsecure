# people.py

customers = [
    {"id": "132301451", "name": "나수빈", "branch": "1지점"},
    {"id": "132301452", "name": "나수빈2", "branch": "2지점"},
    {"id": "132301453", "name": "나수빈3", "branch": "3지점"},
    {"id": "132301454", "name": "나수빈4", "branch": "4지점"},
    {"id": "132301455", "name": "나수빈5", "branch": "5지점"},
    {"id": "132301456", "name": "나수빈6", "branch": "6지점"},
    {"id": "132301457", "name": "나수빈7", "branch": "7지점"},
    {"id": "132301458", "name": "나수빈8", "branch": "8지점"},
    {"id": "132301459", "name": "나수빈9", "branch": "9지점"},
    {"id": "132301460", "name": "나수빈10", "branch": "10지점"},
    
]

def get_customer_by_id(customer_id):
    return next((customer for customer in customers if customer["id"] == customer_id), None)
