
import frappe
from organic_ghee.organic_ghee.services.auth import AuthService
from  organic_ghee.utils.response import success_response, error_response

auth_service = AuthService()

@frappe.whitelist(allow_guest=True)
def signup(email, password, name, phone):
    try:
        data = auth_service.signup(email, password, name, phone)
        return success_response(data, "Signup Successful")
    except Exception as e:
        frappe.log_error("Signup Error")
        return error_response(str(e))

@frappe.whitelist(allow_guest=True)
def login(email, password):
    try:
        data = auth_service.login(email, password)
        return success_response(data, "Login Successful")
    except Exception as e:
        frappe.log_error("Login Error")
        return error_response(str(e))

@frappe.whitelist()
def logout():
    try:
        auth_service.logout()
        return success_response(None, "Logged out successfully")
    except Exception as e:
        return error_response(str(e))

@frappe.whitelist(allow_guest=True)
def me():
    try: 
        print("me++++++++++++++++++++++",frappe.request.method)
        if frappe.request.method == "POST" or frappe.request.method == "PUT":
            # Handle Update
            # frappe.form_dict contains all params including those in body
            args = frappe.form_dict
            data = auth_service.update_profile(**args)
            return success_response(data, "Profile Updated")
        else:
            # Handle Get
            data = auth_service.get_customer_profile()
            return success_response(data, "Profile Fetched")
    except Exception as e:
        return error_response(str(e))
