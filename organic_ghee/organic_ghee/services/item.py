import frappe

class ItemService:

    def get_items_list(self, page=1, page_size=20):
        start = (int(page) - 1) * int(page_size)

        items = frappe.get_all(
            "Item",
            filters={
                "item_group": "Products",
                "is_sales_item": 1,
                "disabled": 0,
                "has_variants": 0
            },
            fields=[
                "name",
                "item_code",
                "item_name",
                "description",
                "image",
                "custom_shortdescription",
                "custom_type",
                "custom_rating",
                "custom_review",
                "custom_in_stock_"
            ],
            start=start,
            page_length=int(page_size)
        )

        return [self._serialize_item(item) for item in items]

    def get_item_details(self, item_code):
        if not frappe.db.exists("Item", item_code):
            frappe.throw("Item not found", frappe.DoesNotExistError)

        item = frappe.get_doc("Item", item_code)
        return self._serialize_item(item, is_doc=True)

    # ---------------- PRIVATE HELPERS ---------------- #

    def _serialize_item(self, item, is_doc=False):
        item_code = item.item_code if is_doc else item.get("item_code")

        prices = self._get_item_prices(item_code)

        return {
            "id": item.name,
            "name": item.item_name if is_doc else item.get("item_name"),
            "description": item.description if is_doc else item.get("description"),
            "shortDescription": (
                item.custom_shortdescription
                if is_doc else item.get("custom_shortdescription")
            ),
            "type": item.custom_type if is_doc else item.get("custom_type"),
            "image": item.image if is_doc else item.get("image"),
            "prices": prices,
            "inStock": bool(
                item.custom_in_stock_ if is_doc else item.get("custom_in_stock_")
            ),
            "rating": item.custom_rating if is_doc else item.get("custom_rating"),
            "reviews": item.custom_review if is_doc else item.get("custom_review")
        }

    def _get_item_prices(self, item_code):
        prices = {}

        item_prices = frappe.get_all(
            "Item Price",
            filters={
                "item_code": item_code,
                "price_list": "Standard Selling"
            },
            fields=["uom", "price_list_rate"]
        )

        for row in item_prices: 
            if row.uom =="Litre":
                prices["1L"] = row.price_list_rate
            else :
                prices[row.uom] = row.price_list_rate

        return prices
