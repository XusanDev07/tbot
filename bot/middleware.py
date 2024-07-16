from django.utils.deprecation import MiddlewareMixin


class TrackViewedProductsMiddleware(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        if 'product_id' in view_kwargs:
            product_id = view_kwargs['product_id']
            viewed_products = request.session.get('viewed_products', [])

            if product_id not in viewed_products:
                viewed_products.append(product_id)
                if len(viewed_products) > 5:
                    viewed_products.pop(0)

            request.session['viewed_products'] = viewed_products
