from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from telegram.error import BadRequest
from telegram.ext import ContextTypes, CallbackContext
from asgiref.sync import sync_to_async

from bot.custom import get_baskets, get_product_names, get_product_details, add_basket, basket_check
from bot.keyboard import MAIN_KEYBOARD
from bot.models import User, Product, Basket

counters = {}


async def edit_basket(update: Update, context: CallbackContext, product_name: str, user_id: int, key=None) -> None:
    counter_key = generate_counter_key(user_id, product_name)

    # Fetch current basket information
    basket = await sync_to_async(Basket.objects.filter(user__tg_user_id=user_id, product__name=product_name).first)()
    if not basket:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="This product is not in your basket.")
        return
    if key == 'save':
        basket.product_number = product_name
        return

    counters[counter_key] = basket.product_number

    # Display current quantity and options to modify it
    inline_keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"+1", callback_data=f"edit_add_1_{product_name}"),
            InlineKeyboardButton(f"{counters[counter_key]}", callback_data=f"edit_number_{product_name}"),
            InlineKeyboardButton(f"-1", callback_data=f"edit_subtract_1_{product_name}")
        ],
        [
            InlineKeyboardButton(f"Save changes", callback_data=f"save_changes_{product_name}"),
            InlineKeyboardButton(f"Cancel", callback_data=f"cancel_edit_{product_name}")
        ]
    ])
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Editing {product_name} in your basket. Current quantity: {basket.product_number}",
        reply_markup=inline_keyboard
    )


def generate_counter_key(tg_user_id, product_name):
    return f"{tg_user_id}_{product_name}"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_user_id = update.message.from_user.id
    user = await sync_to_async(User.objects.filter(tg_user_id=tg_user_id).first)()

    if user and user.phone_number:
        reply_markup = ReplyKeyboardMarkup(MAIN_KEYBOARD, resize_keyboard=True)

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Welcome back! Please choose an option:",
            reply_markup=reply_markup
        )
    else:
        keyboard = [[KeyboardButton("📞 Send a phone number", request_contact=True)]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Please share your phone number by pressing the button below.",
            reply_markup=reply_markup
        )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text.lower() == "hello":
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Hi there! How can I help you today?")
    elif str(update.message.text) == eval(repr(MAIN_KEYBOARD[0][0])):
        keyboard = [
            [InlineKeyboardButton("Open Chat",
                                  web_app=WebAppInfo(
                                      url=f'https://botfront.tramplin.uz//?tg_user_id={update.effective_user.id}'))]
        ]

        reply_markup_ = InlineKeyboardMarkup(keyboard)
        # await update.message.reply_text("message", reply_markup=reply_markup_)
        names = await sync_to_async(list)(Product.objects.values_list('name', flat=True))
        wrapped_names = [names[i:i + 3] for i in range(0, len(names), 3)]
        if not any(sublist == ['⬅️ Back'] for sublist in wrapped_names):
            wrapped_names.append(['⬅️ Back'])
        reply_markup = ReplyKeyboardMarkup(wrapped_names, resize_keyboard=True)
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Welcome to the 🛍 Katalog section, select a product type",
                                       reply_markup=reply_markup_)
    elif update.message.text == eval(repr(MAIN_KEYBOARD[1][0])):
        names = await sync_to_async(list)(Product.objects.filter(sale=True).values_list('name', flat=True))
        wrapped_names = [names[i:i + 3] for i in range(0, len(names), 3)]
        if not any(sublist == ['⬅️ Back'] for sublist in wrapped_names):
            wrapped_names.append(['⬅️ Back'])

        reply_markup = ReplyKeyboardMarkup(wrapped_names, resize_keyboard=True)
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Welcome to the 😍 Aksiya section, select a product type",
                                       reply_markup=reply_markup)
    elif update.message.text == eval(repr(MAIN_KEYBOARD[1][1])):
        baskets = await get_baskets(update.message.from_user.id)
        if baskets:
            for basket in baskets:
                inline_keyboard = InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton(f"Jami: {basket['product_number']}",
                                             callback_data=f"None"),
                        InlineKeyboardButton(f"Bekkor qilish ✖", callback_data=f"delete_{basket['product_name']}"),
                        # InlineKeyboardButton(f"O'zgartirish", callback_data=f"edit_basket_{basket['product_name']}")
                    ]
                ])
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=basket['product_image'],
                    caption=f"Name: {basket['product_name']}\nDescription: {basket['product_description']}\nQuantity: {basket['product_quantity']}\nNarxi: {basket['price']}",
                    reply_markup=inline_keyboard
                )
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="You have no orders in your basket.")
    elif update.message.text == eval(repr(MAIN_KEYBOARD[2][0])):
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="@nrx_xusan")
    elif update.message.text == "⬅️ Back":
        reply_markup = ReplyKeyboardMarkup(MAIN_KEYBOARD, resize_keyboard=True)
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Welcome back! Please choose an option:",
                                       reply_markup=reply_markup)

    else:
        product_names = await get_product_names()
        if update.message.text in product_names:
            product_details = await get_product_details(update.message.text)
            counter_key = generate_counter_key(update.message.from_user.id, product_details['name'])
            if counter_key not in counters:
                counters[counter_key] = 1

            inline_keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(f"+1", callback_data=f"add_1_{product_details['name']}"),
                    InlineKeyboardButton(f"{counters[counter_key]}",
                                         callback_data=f"number_{product_details['name']}"),
                    InlineKeyboardButton(f"-1", callback_data=f"subtract_1_{product_details['name']}")
                ],
                [
                    InlineKeyboardButton(f"Savatga qo'shish 🛒", callback_data=f"add_to_cart_{product_details['name']}")
                ]
            ])
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=product_details['image_url'],
                caption=f"Name: {product_details['name']}\nDescription: {product_details['description']}\nNarxi: {product_details['cost']}",
                reply_markup=inline_keyboard
            )
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, no such section was found")


async def button_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    callback_data = query.data
    try:
        product_name = callback_data.split("_")[-1]
        user_id = query.from_user.id
        counter_key = generate_counter_key(user_id, product_name)

        if callback_data.startswith('delete'):
            await basket_check(user_id, product_name)
            await query.delete_message()
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Buyurtma o'chirib yuborildi")
            return
        elif callback_data.startswith("add_1_") or callback_data.startswith("edit_1_"):
            counters[counter_key] += 1
        elif callback_data.startswith("subtract_1_") or callback_data.startswith("edit_subtract_1_"):
            if counters[counter_key] > 1:
                counters[counter_key] -= 1
        elif callback_data.startswith("add_to_cart_"):

            await query.delete_message()

            product = await sync_to_async(Product.objects.get)(name=product_name)
            if product.residual < counters[counter_key]:
                await context.bot.send_message(chat_id=query.message.chat_id,
                                               text="Sorry, we don't have enough product in stock.")
            else:
                product.residual -= counters[counter_key]
                await sync_to_async(product.save)()
                await add_basket(product_id=product.id, product_number=counters[counter_key], user=user_id)

                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text=f"Added {counters[counter_key]} of {product_name} to the cart."
                )
            counters[counter_key] = 1
            return
        elif callback_data.startswith("edit_basket_"):
            await edit_basket(update, context, product_name, user_id)
            return
        elif callback_data.startswith("save_changes_"):
            await edit_basket(user_id, product_name, counters[counter_key], key='save')
            await query.edit_message_text(
                text=f"Updated {product_name} quantity to {counters[counter_key]} in your basket.")
            return
        elif callback_data == "" or None:
            return
        inline_keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(f"+1", callback_data=f"add_1_{product_name}"),
                InlineKeyboardButton(f"{counters[counter_key]}", callback_data=f"number_{product_name}"),
                InlineKeyboardButton(f"-1", callback_data=f"subtract_1_{product_name}")
            ],
            [
                InlineKeyboardButton(f"Savatga qo'shish 🛒", callback_data=f"add_to_cart_{product_name}")
            ]
        ])

        await query.edit_message_reply_markup(reply_markup=inline_keyboard)
    except BadRequest as e:
        await query.edit_message_text(text="An error occurred: Could not edit message")


@sync_to_async
def get_or_create_user(tg_user_id, phone_number, username):
    user, created = User.objects.get_or_create(tg_user_id=tg_user_id, defaults={'username': username})
    user.phone_number = phone_number
    user.save()
    return user, created


async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    phone_number = contact.phone_number
    tg_user_id = update.message.from_user.id
    username = update.message.from_user.username

    await get_or_create_user(tg_user_id, phone_number, username)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Thanks for sharing your phone number: {phone_number}"
    )

    reply_markup = ReplyKeyboardMarkup(MAIN_KEYBOARD, resize_keyboard=True)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Please choose an option:",
        reply_markup=reply_markup
    )


async def command_not_found(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Sorry, I didn't understand that command."
    )
