
import frappe
from frappe import _

class AddressService:
    def get_customer_from_user(self, user):
        if user == "Guest":
            frappe.throw(_("Please login to proceed"), frappe.PermissionError)
            
        customer_name = frappe.db.get_value("Customer", {"email_id": user}, "name")
        if not customer_name:
            frappe.throw(_("Customer profile not found for this user"), frappe.DoesNotExistError)
        return customer_name

    def resolve_address(self, user, address_data):
        """
        Finds an existing address for the customer with matching line1 and pincode,
        or creates a new one.
        """
        customer = self.get_customer_from_user(user)
        
        # 1. Search for existing address
        # We match on address_line1 and pincode as unique enough for MVP
        filters = {
            "address_line1": address_data.get("address_line1"),
            "pincode": address_data.get("pincode"),
            "disabled": 0
        }
        
        # Filter by link to customer
        # Complex query needed? Or just fetch all addresses for customer and filter in python?
        # Let's try to query Address directly if possible.
        # But Address doesn't have 'customer' field directly, it has 'links'.
        # Efficient way: Get all addresses for customer (we have get_addresses logic)
        
        existing_addresses = self.get_addresses(user)
        
        for addr in existing_addresses:
            # Check match using the formatted dict returned by get_addresses
            # Note: get_addresses returns dicts, not docs
            if (addr.get("address_line1") == address_data.get("address_line1") and 
                addr.get("pincode") == address_data.get("pincode")):
                return addr.get("address_id")
                
        # 2. If no match, create new
        # Map frontend keys to backend keys if different
        # Frontend: address_title, address_line1, city, state, country, pincode, phone
        
        # Ensure we pass a clean dict to create_address
        new_data = {
            "address_title": address_data.get("address_title") or customer,
            "address_line1": address_data.get("address_line1") or address_data.get("street") or "",
            "address_line2": address_data.get("address_line2"),
            "city": address_data.get("city"),
            "state": address_data.get("state"),
            "country": address_data.get("country"),
            "pincode": address_data.get("pincode"),
            "phone": address_data.get("phone")
        }
        
        result = self.create_address(user, new_data)
        return result.get("address_id")

    def create_address(self, user, data):
        customer = self.get_customer_from_user(user)
        
        doc = frappe.new_doc("Address")
        doc.address_title = data.get("address_title") or customer
        doc.address_type = data.get("address_type") or "Shipping"
        doc.address_line1 = data.get("street")
        doc.address_line2 = data.get("address_line2")
        doc.custom_landmark = data.get("landmark") 
        doc.custom_full_name = data.get("fullName")
        doc.city = data.get("city")
        doc.state = data.get("state")
        doc.country = data.get("country")
        doc.pincode = data.get("pincode")
        doc.phone = data.get("phone")
        doc.email_id = user # Set email to user's email
        
        # Link to Customer
        doc.append("links", {
            "link_doctype": "Customer",
            "link_name": customer
        })
        
        doc.save(ignore_permissions=True)
        return self._format_address(doc)

    def get_addresses(self, user):
        customer = self.get_customer_from_user(user)
        
        # Find addresses linked to this customer
        # Address has a child table 'links'. We need to query that.
        addresses = frappe.get_all("Address",
            filters={
                "disabled": 0,
                "name": ["in", [
                    d.parent for d in frappe.db.get_all("Dynamic Link", 
                        filters={"link_doctype": "Customer", "link_name": customer, "parenttype": "Address"}, 
                        fields=["parent"]
                    )
                ]]
            },
            fields=["*"]
        )
        
        return [self._format_address(addr) for addr in addresses]

    def update_address(self, user, address_id, data):
        self._validate_ownership(user, address_id)
        
        doc = frappe.get_doc("Address", address_id)
        
        updatable_fields = ["address_title", "street", "address_line2", "city", "state", "country", "pincode", "phone", "address_type"]
        
        for field in updatable_fields:
            if field in data:
                setattr(doc, field, data[field])
                
        doc.save(ignore_permissions=True)
        return self._format_address(doc)

    def delete_address(self, user, address_id):
        self._validate_ownership(user, address_id)
        frappe.delete_doc("Address", address_id, ignore_permissions=True)
        return {"result": "success"}

    def _validate_ownership(self, user, address_id):
        customer = self.get_customer_from_user(user)
        
        # Check if address is linked to this customer
        is_linked = frappe.db.exists("Dynamic Link", {
            "parent": address_id,
            "parenttype": "Address",
            "link_doctype": "Customer",
            "link_name": customer
        })
        
        if not is_linked:
            frappe.throw(_("Address currently not found or you do not have permission"), frappe.PermissionError)

    def _format_address(self, doc):
        # Convert doc or dict to clean output
        return {
            "id": doc.name,
            "address_title": doc.address_title,
            "address_line1": doc.address_line1,
            "address_line2": doc.address_line2,
            "fullName":doc.custom_full_name,
            "phone":doc.phone, 
            "email":doc.email_id,
            "street":doc.address_line1  ,
            "landmark":doc.custom_landmark,
            "city": doc.city,
            "state": doc.state,
            "country": doc.country,
            "pincode": doc.pincode,
            "is_primary_address": doc.is_primary_address,
            "is_shipping_address": doc.is_shipping_address
        }
