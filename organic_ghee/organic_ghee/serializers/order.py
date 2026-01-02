def order_item_serializer(item):
    print("order_item_serializer++++++++",item)
    return {
        "itemCode": item.item_code,
        "name": item.item_name,
        "quantity": item.qty,
        "price": item.amount
    }


def order_detail_serializer(order):
    try: 
        print("order_detail_serializer+++++",order["items"])  
        
        items = []  
        for item in order["items"] :  
            data = order_item_serializer(item)
            items.append(data)
            
        data = {
            "id": order.name,
            "status": order.status,
            "date": order.transaction_date,
            "total": order.grand_total,
            "addresss": order.customer_address or None,
            "items": items
        }
        return data
    except Exception as e: 
        print("error while searlixze the data ++++",e) 
        return []
    
