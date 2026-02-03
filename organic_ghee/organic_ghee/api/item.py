
import frappe
from organic_ghee.organic_ghee.services.item import ItemService
from organic_ghee.utils.response import success_response, error_response

item_service = ItemService()

@frappe.whitelist(allow_guest=True)
@frappe.cache(ttl=600)

def get_all_items(page=1, page_size=20):
    try:
        data = item_service.get_items_list(page, page_size)
        return success_response(data, "Items Fetched Successfully")
    except Exception as e:
        return error_response(str(e))

@frappe.whitelist(allow_guest=True)
def get_item(item_code):
    try:
        data = item_service.get_item_details(item_code)
        return success_response(data, "Item Details Fetched Successfully")
    except Exception as e:
        return error_response(str(e))
