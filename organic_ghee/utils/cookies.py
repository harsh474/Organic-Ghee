import frappe

def set_samesite_none():
    """
    Override cookie settings to support cross-origin requests.
    This is a more aggressive approach that patches the cookie manager.
    """
    # Method 1: Override cookies in cookie_manager
    if hasattr(frappe.local, 'cookie_manager') and frappe.local.cookie_manager:
        for cookie_name, cookie in frappe.local.cookie_manager.cookies.items():
            cookie['samesite'] = 'None'
            cookie['secure'] = True
    
    # Method 2: Patch the response to modify Set-Cookie headers
    if hasattr(frappe.local, 'response') and frappe.local.response:
        # Ensure response headers exist
        if not hasattr(frappe.local.response, 'headers'):
            frappe.local.response.headers = {}
        
        # Set CORS headers
        origin = frappe.get_request_header('Origin')
        if origin:
            frappe.local.response.headers['Access-Control-Allow-Origin'] = origin
        else:
            frappe.local.response.headers['Access-Control-Allow-Origin'] = 'https://organic-order-craft.vercel.app'
        
        frappe.local.response.headers['Access-Control-Allow-Credentials'] = 'true'
        frappe.local.response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        frappe.local.response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Frappe-CSRF-Token, X-Requested-With'
        frappe.local.response.headers['Access-Control-Expose-Headers'] = 'Set-Cookie'
        
        # Override Set-Cookie headers if they exist
        if hasattr(frappe.local.response, 'set_cookie'):
            original_set_cookie = frappe.local.response.set_cookie
            
            def patched_set_cookie(key, value='', max_age=None, expires=None, 
                                  path='/', domain=None, secure=True, httponly=False, 
                                  samesite='None'):
                return original_set_cookie(
                    key, value, max_age, expires, path, domain, 
                    secure=True, httponly=httponly, samesite='None'
                )
            
            frappe.local.response.set_cookie = patched_set_cookie

def handle_options_request():
    """Handle CORS preflight requests"""
    if frappe.request.method == "OPTIONS":
        frappe.local.response = frappe._dict({
            "http_status_code": 200,
            "headers": {
                "Access-Control-Allow-Origin": frappe.get_request_header("Origin") or "https://organic-order-craft.vercel.app",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Frappe-CSRF-Token, X-Requested-With",
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Max-Age": "3600"
            }
        })
        return True
    return False