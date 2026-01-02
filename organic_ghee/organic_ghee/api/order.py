
import frappe
import json
from organic_ghee.organic_ghee.services.order import OrderService
from organic_ghee.utils.response import success_response, error_response

order_service = OrderService()

@frappe.whitelist(allow_guest=True)
def create():
    try:
        user = frappe.session.user
        data = frappe.form_dict
        
        items_json = data.get("items")
        if isinstance(items_json, str):
            items = json.loads(items_json)
        else:
            items = items_json
            
        # Address can be ID or JSON Object
        address_input = data.get("address") 
        if not address_input:
            # Fallback to old key
            address_input = data.get("address_id")
            
        if isinstance(address_input, str):
             # check if it's a json string
            try:
                if address_input.startswith("{"):
                     address_input = json.loads(address_input)
            except:
                pass # Treat as ID string
        
        if not items:
            return error_response("Items are required")
        if not address_input:
            return error_response("Address (object or ID) is required")
            
        result = order_service.create_order(user, items, address_input)
        return success_response(result, "Order Created Successfully")
    except Exception as e:
        frappe.log_error("Order Create Error")
        return error_response(str(e))

@frappe.whitelist()
def list():
    try:
        user = frappe.session.user
        result = order_service.get_orders(user)
        return success_response(result, "Orders Fetched Successfully")
    except Exception as e:
        return error_response(str(e))

@frappe.whitelist()
def details():
    try:
        user = frappe.session.user
        order_id = frappe.form_dict.get("order_id")
        if not order_id:
            return error_response("Order ID is required")
            
        result = order_service.get_order_details(user, order_id)
        return success_response(result, "Order Details Fetched Successfully")
    except Exception as e:
        return error_response(str(e))

@frappe.whitelist()
def cancel():
    try:
        user = frappe.session.user
        order_id = frappe.form_dict.get("order_id")
        if not order_id:
            return error_response("Order ID is required")
            
        result = order_service.cancel_order(user, order_id)
        return success_response(result, "Order Cancelled Successfully")
    except Exception as e:
        return error_response(str(e))
