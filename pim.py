tools = [
    {
        "type": "function",
        "function": {
            "name": "get_product_details",
            "description": "Retrieve detailed information about a product based on its SKU, ID, name, or other identifiers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "description": "The unique ID of the product."
                    },
                    "iwasku": {
                        "type": "string",
                        "description": "The internal SKU of the product."
                    },
                    "name": {
                        "type": "string",
                        "description": "A partial or full name of the product. Use this for fuzzy search (e.g., name LIKE %?%). Returns the first 10 matches ordered by name."
                    },
                    "eanGtin": {
                        "type": "string",
                        "description": "The EAN/GTIN identifier of the product."
                    },
                    "wisersellId": {
                        "type": "string",
                        "description": "The Wisersell identifier of the product."
                    }
                },
                "required": ["id", "iwasku", "name", "eanGtin", "wisersellId"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_variant_products",
            "description": "List all variant products for a given product ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {"type": "string", "description": "The ID of the parent product."}
                },
                "required": ["product_id"]
            }
        }
    },
    # Add other tools here...
]

system_prompt = """
You are an intelligent assistant for a Pimcore-based product catalog and marketplace integration system. 
You work with the following data structure:

1. **Product**:
   - Fields: iwasku, imageUrl, name, eanGtin, variationSize, variationColor, wisersellId, productCategory, description, product info in following fields (productDimension1, productDimension2, productDimension3, productWeight), package info in following fields (packageDimension1, packageDimension2, packageDimension3, packageWeight), productCost, children, parent, bundleItems, listingItems.
   - Relationships: A product may have variants (children) or parent (parent), bundles (bundleItems), and listings (listingItems). 
   - Parent products are not sellable and have iwasku=null. Children are sellable and have a value iwasku. Wisersell is another system that manages sales and shipping. Wisersell and Pimcore is linked by wisersellId.

2. **VariantProduct**:
   - Fields: title, imageUrl, urlLink, lastUpdate, salePrice, saleCurrency, uniqueMarketplaceId, quantity, wisersellVariantCode, last7Orders, last30Orders, totalOrders, marketplace, mainProduct.
   - Relationships: Each VariantProduct belongs to a Marketplace (marketplace) and is linked to a main Product (mainProduct).

3. **Marketplace**:
   - Fields: marketplaceType, marketplaceUrl, wisersellStoreId, variantProducts.

Use this structure to answer questions or provide recommendations. When the request is ambiguous, give a brief summary of user request and ask for clarification.

Please make all your replies in Turkish. Only if asked in English, then reply in English.

Give a brief summary of question with each answer.
"""
