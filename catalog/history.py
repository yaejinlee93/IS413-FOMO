from catalog import models as cmod

class LastFiveMiddleWare:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Get the last-viewed product id list from the session
        ids = request.session.get('last_five', [])
        request.last_five = []

        # Convert the product ids from integers to actual products.

        for item in ids:
            request.last_five.append(cmod.Product.objects.get(id=item))

        response = self.get_response(request)

        # Convert request.last_five to a list of product ids.
        prod_ids = []

        for item in request.last_five:
            prod_ids.append(item.id)

        request.session['last_five'] = prod_ids
        # Save the list of product ids to the session.

        return response
