from bot.models import User, Basket, Product
from asgiref.sync import sync_to_async


# async def get_baskets(tg_user_id):
#     try:
#         user = await sync_to_async(User.objects.get)(tg_user_id=tg_user_id)
#         baskets = await sync_to_async(list)(
#             Basket.objects.filter(user=user).values_list('product__name', 'product_number', 'user__username'))
#         print(baskets)
#
#         formatted_baskets = [f"{basket}({product_number})_{user__id}" for basket, product_number, user__id in baskets]
#         return formatted_baskets
#         # return baskets
#     except User.DoesNotExist:
#         return None

@sync_to_async
def get_baskets(tg_user_id):
    user = User.objects.get(tg_user_id=tg_user_id)
    baskets = Basket.objects.filter(user=user).select_related('product')
    return [
        {
            'product_name': basket.product.name,
            'product_number': basket.product_number,
            'product_description': basket.product.desc,
            'product_image': basket.product.img,
            'price': basket.product_number * basket.product.cost,
            'product_quantity': basket.product_number
        }
        for basket in baskets
    ]


async def get_product_details(product_name):
    product = await sync_to_async(Product.objects.get)(name=product_name)
    return {
        'id': product.id,
        'name': product.name,
        'description': product.desc,
        'image_url': product.img,
        'cost': product.cost,
        'qoldiq': product.residual,
    }


async def get_product_names():
    names = await sync_to_async(list)(Product.objects.values_list('name', flat=True))
    return names


@sync_to_async
def create_basket_sync(product_id, product_number, tg_user_id):
    user = User.objects.get(tg_user_id=tg_user_id)
    Basket.objects.create(product_id=product_id, product_number=product_number, user=user)
    return


async def add_basket(product_id: int, product_number: int, user: int):
    try:
        await create_basket_sync(product_id, product_number, user)
    except Exception as e:
        print(f"Error adding product to basket: {e}")


@sync_to_async
def get_user(tg_user_id):
    return User.objects.get(tg_user_id=tg_user_id)


@sync_to_async
def get_basket(user, product_name):
    return Basket.objects.filter(user=user, product__name=product_name).select_related('product').first()


@sync_to_async
def delete_basket(basket):
    basket.delete()


@sync_to_async
def update_product_residual(product, amount):
    product.residual += amount
    product.save()


async def basket_check(user_id, product_name):
    user = await get_user(user_id)
    basket = await get_basket(user, product_name)

    if basket:
        product = basket.product
        await update_product_residual(product, basket.product_number)
        await delete_basket(basket)


