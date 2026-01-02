
import frappe
from frappe import _
from frappe.utils import add_days, nowdate, flt
from ..serializers.order import order_detail_serializer
import json

class OrderService:
    
     
    @frappe.whitelist()
    def get_customer_from_user(self, user):
        if user == "Guest":
            frappe.throw(_("Please login to proceed"), frappe.PermissionError)
            
        customer_name = frappe.db.get_value("Customer", {"email_id": user}, "name")
        if not customer_name:
            frappe.throw(_("Customer profile not found for this user"), frappe.DoesNotExistError)
        return customer_name

    
    @frappe.whitelist()
    def create_order(self, user, items, address):
        # Allow address_data_or_id to be ID (str) or Dict
        from organic_ghee.organic_ghee.services.address import AddressService
        from organic_ghee.organic_ghee.services.payment import PaymentService
        # print("items++++++",items)
        print("address++++++123",address) 
        address_data_or_id = address.get("id")
        print("address_data_or_id+++++++",address_data_or_id)
        address_service = AddressService()
        payment_service = PaymentService()
        
        customer = self.get_customer_from_user(user)
        
        # 1. Resolve Address
        if isinstance(address_data_or_id, dict):
            address_id = address_service.resolve_address(user, address_data_or_id)
        else:
            address_id = address_data_or_id
        
        print("customer+++++++++",customer) 
        # Validate Address ownership
        if not frappe.db.exists("Dynamic Link", {
            "parent": address_id, "parenttype": "Address", 
            "link_doctype": "Customer", "link_name": customer
        }):
            frappe.throw(_("Invalid Address selected"), frappe.PermissionError)
        
        print("address_id+++++++++after",address_id)  

        # Prepare Order Items
        so_items = []
        for item in items:
            # Map 'id' to 'item_code' if present (Support for provided frontend structure)
            item_code = item.get("productId") or item.get("item_code")
            # Qty might be missing in item dict if it's just product info, default to 1 or check logic
            # User said "array of object such that each object will have ... quantity" in Phase 5
            # But in Phase 6 request snippet "items: [ {id:..., productId:...} ]" - qty missing in snippet?
            # Assigning default 1 if missing for safety, OR expecting 'qty' key.
            # Usually cart items have qty.
            qty = flt(item.get("qty") or 1)
            
            if qty <= 0:
                continue
                
            # Fetch Price (Backend Validation)
            price = frappe.db.get_value("Item Price", 
                {"item_code": item_code, "price_list": "Standard Selling"}, 
                "price_list_rate"
            )
            
            if not price:
                 # Fallback to standard rate in Item if Item Price not found
                price = frappe.db.get_value("Item", item_code, "standard_rate") or 0.0

            so_items.append({
                "item_code": item_code,
                "qty": qty,
                "rate": price,
                "delivery_date": add_days(nowdate(), 7)
            })
        
        print("so_items",so_items)
        if not so_items:
            frappe.throw(_("No valid items in order"), frappe.ValidationError)

        try: 
              # Create Sales Order
            so = frappe.new_doc("Sales Order")
            so.customer = customer
            so.set_warehouse = "Finished Goods - E"
            so.transaction_date = nowdate()
            so.delivery_date = add_days(nowdate(), 7)
            so.customer_address = address_id
             # ✅ Correct way to add items
            for item in so_items:
                so.append("items", {
                    "item_code": item.get("item_code"),
                    "qty": item.get("qty"),
                    "rate": item.get("rate")
                })

            so.save(ignore_permissions=True)
            so.submit() # Submit immediately
            frappe.db.commit() 
            print("sales order is ",so)
        except Exception as e:
            print("Error while creating sales order as e",e) 
            return e
        
        # 2. Generate Payment Link
        payment_data = payment_service.create_payment_order(user, so.name)
        
        return {
            "order_id": so.name,
            "status": so.status,
            "grand_total": so.grand_total,
            "payment": payment_data
        }

    def get_orders(self, user):
        customer = self.get_customer_from_user(user)
        print("customer++++++++++",customer)
        orders = frappe.get_all("Sales Order",  
            filters={"customer": customer},
            fields=["name", "transaction_date", "grand_total", "status", "delivery_date","shipping_address"],
            order_by="transaction_date desc"
        )  
        
        resposne = []
        for order in orders  :
            items =  self.get_order_from_child_item(order.name) 
            print("item+++",items)
            order["items"]= items or [] 
            print("order++++++++++",order)
            data = order_detail_serializer(order)
            print("data++",data)
            resposne.append(data)
            
        return resposne
    
    def get_order_from_child_item(self,name): 
        try:
            items  = frappe.frappe.db.get_all('Sales Order Item', filters={"parent":name,"parenttype":"Sales Order"}, fields=["name","item_code","item_name","qty","amount"])
        except Exception as e: 
            print("Error while getting item as ",e)
        return items
    
    def get_order_details(self, user, order_id):
        customer = self.get_customer_from_user(user)
        
        if not frappe.db.exists("Sales Order", {"name": order_id, "customer": customer}):
            frappe.throw(_("Order not found"), frappe.DoesNotExistError)
            
        doc = frappe.get_doc("Sales Order", order_id)
        
        return {
            "order_id": doc.name,
            "status": doc.status,
            "transaction_date": doc.transaction_date,
            "grand_total": doc.grand_total,
            "taxes": doc.total_taxes_and_charges,
            "shipping_address": doc.customer_address,
            "items": [{
                "item_code": d.item_code,
                "item_name": d.item_name,
                "qty": d.qty,
                "rate": d.rate,
                "amount": d.amount
            } for d in doc.items]
        }

    def cancel_order(self, user, order_id):
        customer = self.get_customer_from_user(user)
        
        if not frappe.db.exists("Sales Order", {"name": order_id, "customer": customer}):
            frappe.throw(_("Order not found"), frappe.DoesNotExistError)
            
        doc = frappe.get_doc("Sales Order", order_id)
        
        if doc.docstatus == 2:
            frappe.throw(_("Order already cancelled"), frappe.ValidationError)
            
        if doc.status in ["Completed", "Closed"]:
            frappe.throw(_("Cannot cancel completed order"), frappe.ValidationError)
            
        doc.cancel()
        return {"result": "Order Cancelled Successfully", "status": doc.status}



