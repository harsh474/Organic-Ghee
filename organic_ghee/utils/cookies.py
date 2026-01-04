import frappe

def set_cookie_attributes():
    """Override cookie attributes for cross-origin requests"""
    if frappe.local.response.cookies:
        for cookie in frappe.local.response.cookies.values():
            cookie["samesite"] = "None"
            cookie["secure"] = True
