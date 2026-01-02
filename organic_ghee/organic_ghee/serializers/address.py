

def order_detail_serializer(add): 
    new_add = {  
        "id":add.name,
        "full_name":add.full_name,
        "phone":add.phone, 
        "email":add.email_id,
        "street":add.address_line1  , 
        "landmark":add.address_line1,
        "city":add.city , 
        "state":add.state,
        "pincode":add.pincode
        }
    return new_add


