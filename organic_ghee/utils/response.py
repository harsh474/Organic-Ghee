
import frappe

def success_response(data=None, message="Success"):
    return {
        "status_code": 200,
        "message": message,
        "data": data
    }

def error_response(message="Something went wrong", status_code=400):
    frappe.response['http_status_code'] = status_code
    return {
        "status_code": status_code,
        "message": message,
        "error": message
    }
