from decimal import Decimal
from django.conf import settings
from .models import Variant, Product

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    # Changed 'variant_id' to 'item_id' here
    def add(self, item_id, quantity=1, override_quantity=False):
        item_id = str(item_id)
        if item_id not in self.cart:
            self.cart[item_id] = {'quantity': 0, 'price': str(self.get_item_price(item_id))}
        
        if override_quantity:
            self.cart[item_id]['quantity'] = quantity
        else:
            self.cart[item_id]['quantity'] += quantity
        self.save()

    def save(self):
        self.session.modified = True

    # Changed 'variant_id' to 'item_id' here
    def remove(self, item_id):
        item_id = str(item_id)
        if item_id in self.cart:
            del self.cart[item_id]
            self.save()

    def get_item_price(self, item_id):
        try:
            variant = Variant.objects.get(id=item_id)
            return variant.product.base_price + variant.price_adjustment
        except Variant.DoesNotExist:
            product = Product.objects.get(id=item_id)
            return product.base_price


    def update(self, item_id, quantity):
        item_id = str(item_id)
        if item_id in self.cart:
            if quantity > 0:
                self.cart[item_id]['quantity'] = quantity
            else:
                # If quantity is 0, remove the item
                del self.cart[item_id]
            self.save()

    def __iter__(self):
        item_ids = self.cart.keys()
        for item_id in item_ids:
            item = self.cart[str(item_id)]
            
            try:
                variant = Variant.objects.get(id=item_id)
                product = variant.product
                variant_name = f"{variant.name}: {variant.value}"
            except Variant.DoesNotExist:
                product = Product.objects.get(id=item_id)
                variant = None
                variant_name = "Standard"

            item['product'] = product
            item['variant'] = variant
            item['variant_name'] = variant_name
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

           

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.save()