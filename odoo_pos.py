import xmlrpc.client
from typing import Dict, List, Optional

class OdooAPI:
    def __init__(self, url: str, db: str, username: str, password: str):
        """Initialize Odoo API connection"""
        self.url = url
        self.db = db
        self.username = username
        self.password = password
        
        # XML-RPC interfaces
        self.common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')
        self.models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')
        
        # Authenticate and get user id
        self.uid = self.common.authenticate(self.db, self.username, self.password, {})

    def search_products(self, 
                       code: Optional[str] = None, 
                       name: Optional[str] = None) -> List[Dict]:
        """Search for products based on code or name"""
        domain = [('available_in_pos', '=', True)]
        
        if code:
            domain.append(('default_code', 'ilike', code))
        if name:
            domain.append(('name', 'ilike', name))

        # Fields to retrieve
        fields = [
            'name',
            'default_code',
            'list_price',      # retail price
            'standard_price',  # cost price
            'pos_price',       # special POS price if available
        ]

        # Search and read products
        products = self.models.execute_kw(
            self.db, self.uid, self.password,
            'product.product',
            'search_read',
            [domain],
            {'fields': fields}
        )

        return products

def main():
    # Configuration (these should be in a config file in production)
    ODOO_URL = "http://your-odoo-server"
    ODOO_DB = "your-database"
    ODOO_USERNAME = "your-username"
    ODOO_PASSWORD = "your-password"

    try:
        # Initialize API
        api = OdooAPI(ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD)
        
        # Example searches
        print("\n=== Search by product code ===")
        code_results = api.search_products(code="TEST001")
        for product in code_results:
            print(f"""
Product Code: {product.get('default_code', 'N/A')}
Name: {product.get('name', 'N/A')}
Retail Price: {product.get('list_price', 0.0)}
POS Price: {product.get('pos_price', 'Same as retail')}
---""")

        print("\n=== Search by product name ===")
        name_results = api.search_products(name="Chair")
        for product in name_results:
            print(f"""
Product Code: {product.get('default_code', 'N/A')}
Name: {product.get('name', 'N/A')}
Retail Price: {product.get('list_price', 0.0)}
POS Price: {product.get('pos_price', 'Same as retail')}
---""")

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()