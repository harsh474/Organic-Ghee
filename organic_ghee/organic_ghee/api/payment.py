
import frappe
from organic_ghee.organic_ghee.services.payment import PaymentService
from organic_ghee.utils.response import success_response, error_response

payment_service = PaymentService()

@frappe.whitelist()
def create():
    try:
        user = frappe.session.user
        order_id = frappe.form_dict.get("order_id")
        if not order_id:
            return error_response("Order ID is required")
            
        result = payment_service.create_payment_order(user, order_id)
        return success_response(result, "Payment Order Created")
    except Exception as e:
        return error_response(str(e))

@frappe.whitelist()
def verify():
    try:
        user = frappe.session.user
        data = frappe.form_dict
        
        required = ["razorpay_payment_id", "razorpay_order_id", "razorpay_signature", "internal_order_id"]
        # for field in required:
        #     if not data.get(field):
        #         return error_response(f"{field} is required")
        print("data++++++++++++",data) 
        print(data.get("razorpay_payment_id"))
        print( data.get("razorpay_order_id"))
        print(data.get("razorpay_signature"))
        print(  data.get("internal_order_id") )
        result = payment_service.verify_payment(
            user, 
            data.get("razorpay_payment_id"),
            data.get("razorpay_order_id"),
            data.get("razorpay_signature"),
            data.get("internal_order_id") # Internal SO ID
        )
        print("result++++",result)
        return success_response(result, "Payment Verified")
    except Exception as e:
        return error_response(str(e))

@frappe.whitelist(allow_guest=True)
def webhook():
    try:
        data = frappe.request.json
        result = payment_service.handle_webhook(data)
        return success_response(result, "Webhook Received")
    except Exception as e:
        return error_response(str(e))
