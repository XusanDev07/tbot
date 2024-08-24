# from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
# from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
#
# # Initialize the counter
# counter = 1
#
# # Define the command handler
# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     global counter
#     keyboard = [
#         [
#             InlineKeyboardButton("+", callback_data='plus'),
#             InlineKeyboardButton("-", callback_data='minus'),
#             InlineKeyboardButton(f"Count: {counter}", callback_data='count')
#         ]
#     ]
#
#     reply_markup = InlineKeyboardMarkup(keyboard)
#
#     await update.message.reply_text('Please choose:', reply_markup=reply_markup)
#
# # Define the button handler
# async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     global counter
#     query = update.callback_query
#     await query.answer()
#
#     # Update the counter based on the button pressed
#     if query.data == 'plus':
#         counter += 1
#     elif query.data == 'minus':
#         # Check if counter is greater than 1 before decrementing
#         if counter > 1:
#             counter -= 1
#         else:
#             # Optionally, you can notify the user that counter cannot be less than 1
#             await query.answer("Counter cannot be less than 1")
#             return
#
#     # Update the inline buttons with the new counter value
#     keyboard = [
#         [
#             InlineKeyboardButton("+", callback_data='plus'),
#             InlineKeyboardButton("-", callback_data='minus'),
#             InlineKeyboardButton(f"Count: {counter}", callback_data='count')
#         ]
#     ]
#
#     reply_markup = InlineKeyboardMarkup(keyboard)
#     await query.edit_message_text(text="Please choose:", reply_markup=reply_markup)
#
# def main() -> None:
#     # Replace 'YOUR_TOKEN' with your bot's token
#     application = Application.builder().token("7311771640:AAH2bPWAjcU9sS-4Emv7ylQBWjKPcWucc7Q").build()
#
#     application.add_handler(CommandHandler('start', start))
#     application.add_handler(CallbackQueryHandler(button))
#
#     application.run_polling()
#
# if __name__ == '__main__':
#     main()
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackContext


def fetch_data():
    url = 'https://back.tramplin.uz/all_registrants/'
    response = requests.get(url)
    print(response)
    if response.status_code == 200:
        return response.json()  # Assuming the API returns JSON data
    else:
        return None


async def start(update: Update, context: CallbackContext) -> None:
    # data = fetch_data()
    # if data:
    #     messages = []
    #     for item in data:
    #         messages.append(
    #             f"ID: {item['id']}\n"
    #             f"Username: {item['username']}\n"
    #             f"Phone: {item['phone']}\n"
    #             f"Location: {item['location']}\n"
    #             f"Created Time: {item['created_time']}\n"
    #             "-----------------------------"
    #         )
    #     message = "\n".join(messages)
    #     keyboard = [
    #         [InlineKeyboardButton("More Details", url="https://back.tramplin.uz")]
    #     ]
    #
    #     reply_markup = InlineKeyboardMarkup(keyboard)
    # keyboard = [
    #  [InlineKeyboardButton("Open Chat",
    #                              web_app=WebAppInfo(
    #                             url=f'https://botfront.tramplin.uz/?tg_user_id={update.effective_user.id}'))]
    # ]

    # reply_markup = InlineKeyboardMarkup(keyboard)
    # await update.message.reply_text("message", reply_markup=reply_markup)
    # else:
    #     await update.message.reply_text("Failed to fetch data from the site.")
    args = context.args
    if args:
        param = args[0]
        # Process the parameter (e.g., send a message or perform some action)
        await update.message.reply_text(f'Parameter received: {param}')
    else:
        await update.message.reply_text('No parameter received.')


def main() -> None:
    # Replace 'YOUR_TOKEN' with your bot's API token
    TOKEN = "7311771640:AAH2bPWAjcU9sS-4Emv7ylQBWjKPcWucc7Q"
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))

    application.run_polling()


if __name__ == '__main__':
    main()
import json
import requests

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MjUwMjg2OTQsImlhdCI6MTcyMjQzNjY5NCwicm9sZSI6InVzZXIiLCJzaWduIjoiMTc4ZTFhN2EwYjNjMjY3YjJmZmU4NDI4ODdkMDJkNDE1NGY2OTc0N2ZlMjRjNGQ5NzQ5YWE3Y2Y1ZGUyNzcwNSIsInN1YiI6IjUifQ.S7ZkrXHQMpL2qqZbwRU5xtwkxxdd5g0xvZMCynpHLAE"


def send_sms(otp, phone):
    url = "https://notify.eskiz.uz/api/message/sms/send"
    msg = f"Maxfiy kod {otp}"

    data = json.dumps({
        "phone_number": str(phone),
        "message": msg,
        "from": 4546,
        "callback_url": "http://0000.uz/test.php"
    })

    headers = f"Bearer {token}"
    response = requests.post(url, data=data, headers=headers)
    return response


from django.core.mail import send_mail


def send_email(OTP, email):
    subject = 'Xusandan salom'
    message = f'One Time Password {OTP}'
    from_email = 'xusanxalilov707@gmail.com'
    recipient_list = [f'{email}']

    send_mail(subject, message, from_email, recipient_list)
