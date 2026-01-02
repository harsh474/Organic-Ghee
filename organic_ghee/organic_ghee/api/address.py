
import frappe
from organic_ghee.organic_ghee.services.address import AddressService
from organic_ghee.utils.response import success_response, error_response

address_service = AddressService()

@frappe.whitelist()
def create():
    try:
        user = frappe.session.user
        data = frappe.form_dict
        result = address_service.create_address(user, data)
        return success_response(result, "Address Created Successfully")
    except Exception as e:
        return error_response(str(e))

@frappe.whitelist()
def list():
    try:
        user = frappe.session.user
        result = address_service.get_addresses(user) 
        response = [] 
        
        return success_response(result, "Addresses Fetched Successfully")
    except Exception as e:
        return error_response(str(e))

@frappe.whitelist()
def update():
    try:
        user = frappe.session.user
        data = frappe.form_dict
        address_id = data.get("address_id")
        if not address_id:
            return error_response("Address ID is required")
            
        result = address_service.update_address(user, address_id, data)
        return success_response(result, "Address Updated Successfully")
    except Exception as e:
        return error_response(str(e))

@frappe.whitelist()
def delete():
    try:
        user = frappe.session.user
        address_id = frappe.form_dict.get("address_id")
        if not address_id:
            return error_response("Address ID is required")
            
        result = address_service.delete_address(user, address_id)
        return success_response(result, "Address Deleted Successfully")
    except Exception as e:
        return error_response(str(e))
