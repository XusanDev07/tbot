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
    keyboard = [
        [InlineKeyboardButton("Open Chat",
                              web_app=WebAppInfo(
                                  url=f'https://0abc-93-188-83-214.ngrok-free.app/?tg_user_id={update.effective_user.id}'))]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("message", reply_markup=reply_markup)
    # else:
    #     await update.message.reply_text("Failed to fetch data from the site.")


def main() -> None:
    # Replace 'YOUR_TOKEN' with your bot's API token
    TOKEN = "7311771640:AAH2bPWAjcU9sS-4Emv7ylQBWjKPcWucc7Q"
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))

    application.run_polling()


if __name__ == '__main__':
    main()
