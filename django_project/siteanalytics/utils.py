import ipinfo

def get_IP_details(ip_addr, token):
    handler = ipinfo.getHandler(token)
    return handler.getDetails(ip_addr)
