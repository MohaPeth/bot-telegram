import logging
from telegram import (
    LabeledPrice,
    Update,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
    PreCheckoutQueryHandler,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = "6122190064:AAFJcJa79k74vxcPZdGTbK9N39RmnV8EnBY"
PAYMENT_PROVIDER_TOKEN = "284685063:TEST:ZjliODllMDQ1MTJh"

ACTION, ACHAT, VENTE, MODE, MOBILE, CARD_ACHAT, CARD_VENTE, CONFIRM = range(8)
recap = []


async def start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    reply_keyboard = [["Acheter", "Vendre"]]

    await update.message.reply_text(
        "Bonjour, que voulez-vous faire ?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            resize_keyboard=True,
            one_time_keyboard=True,
            input_field_placeholder="Acheter ou Vendre ?"
        ),
    )
    return ACTION


async def action_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text == "Acheter":
        achat_keyboard = [["XAF vers BTC", "XOF vers BTC"],
                          ["EUR vers BTC", "USD vers BTC"]]
        await update.message.reply_text(
            "Quelle conversion voulez-vous effectuer ?",
            reply_markup=ReplyKeyboardMarkup(
                achat_keyboard,
                resize_keyboard=True,
                one_time_keyboard=True,
                input_field_placeholder="XAF vers BTC, XOF vers BTC, EUR vers BTC ou USD vers BTC ?",
            )
        )
        recap.insert(0, "Achat")
        return ACHAT
    else:
        vendre_keyboard = [["BTC vers EUR", "BTC vers USD"],
                           ["BTC vers RUB"]]
        await update.message.reply_text(
            "Quelle conversion voulez-vous effectuer ?",
            reply_markup=ReplyKeyboardMarkup(
                vendre_keyboard,
                one_time_keyboard=True, input_field_placeholder="Acheter ou Vendre ?",
            )
        )
        recap.insert(0, "Vente")
        return VENTE


async def achat_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text == "XAF vers BTC":
        xaf_btc_keyboard = [["Airtel Money", "Carte Bancaire"]]
        await update.message.reply_text(
            "Quelle mode de paiement voulez-vous utiliser ?",
            reply_markup=ReplyKeyboardMarkup(
                xaf_btc_keyboard,
                resize_keyboard=True,
                one_time_keyboard=True,
                input_field_placeholder="Airtel Money ou Carte Bancaire ?",
            )
        )
        recap.insert(1, "XAF vers BTC")
        return MODE
    elif update.message.text == "XOF vers BTC":
        xof_btc_keyboard = [["Orange Money", "Carte Bancaire"]]
        await update.message.reply_text(
            "Quelle mode de paiement voulez-vous utiliser ?",
            reply_markup=ReplyKeyboardMarkup(
                xof_btc_keyboard,
                resize_keyboard=True,
                one_time_keyboard=True,
                input_field_placeholder="Orange Money ou Carte Bancaire ?",
            )
        )
        recap.insert(1, "XOF vers BTC")
        return MODE
    elif update.message.text == "EUR vers BTC":
        eur_btc_keyboard = [["Carte Bancaire"]]
        await update.message.reply_text(
            "Quelle mode de paiement voulez-vous utiliser ?",
            reply_markup=ReplyKeyboardMarkup(
                eur_btc_keyboard,
                resize_keyboard=True,
                one_time_keyboard=True,
                input_field_placeholder="Carte Bancaire ?",
            )
        )
        recap.insert(1, "EUR vers BTC")
        return MODE
    elif update.message.text == "USD vers BTC":
        usd_btc_keyboard = [["Carte Bancaire"]]
        await update.message.reply_text(
            "Quelle mode de paiement voulez-vous utiliser ?",
            reply_markup=ReplyKeyboardMarkup(
                usd_btc_keyboard,
                resize_keyboard=True,
                one_time_keyboard=True,
                input_field_placeholder="Carte Bancaire ?",
            )
        )
        recap.insert(1, "USD vers BTC")
        return MODE


async def vente_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text == "BTC vers EUR":
        recap.insert(1, "BTC vers EUR")
        return MODE
    else:
        recap.insert(1, "BTC vers USD")
        return MODE
    


async def mode_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text == "Airtel Money":
        await update.message.reply_text("Paiement par Airtel money.\n LIEN_VERS_PAIEMENT_Ici")
        return MOBILE
    elif update.message.text == "Orange Money":
        return MOBILE
    elif update.message.text == "Carte Bancaire":
        await update.message.reply_text(
            "Entre le montant: ",
        )
        return CARD_ACHAT
    elif recap[1] == "BTC vers EUR" or recap[1] == "BTC vers EUR":
        return CARD_VENTE


async def card_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    recap.insert(2, int(update.message.text))
    devise = ""
    if recap[1] == "EUR vers BTC":
        devise = "EUR"
    else:
        devise = "USD"

    chat_id = update.message.chat_id
    title = recap[0]
    description = f"Vous voulez {recap[0]}er des {recap[1]} de {recap[2]}."
    payload = "Custom-Payload"
    currency = devise
    price = recap[2]
    prices = [LabeledPrice("Test", price * 100)]

    await context.bot.send_invoice(
        chat_id,
        title,
        description,
        payload,
        PAYMENT_PROVIDER_TOKEN,
        currency,
        prices,
        need_name=True,
        need_phone_number=True,
        need_email=True,
    )


async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Answers the PreQecheckoutQuery"""
    query = update.pre_checkout_query
    # check the payload, is this from your bot?
    if query.invoice_payload != "Custom-Payload":
        # answer False pre_checkout_query
        await query.answer(ok=False, error_message="Something went wrong...")
    else:
        await query.answer(ok=True)


async def successful_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Confirms the successful payment."""
    # do something after successfully receiving payment?
    await update.message.reply_text("Thank you for your payment!")


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> no:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(BOT_TOKEN).build()

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler(
            command="start", callback=start_callback)],
        states={
            ACTION: [MessageHandler(filters=filters.Regex("^(Acheter|Vendre)$"), callback=action_callback)],
            ACHAT: [MessageHandler(filters=filters.Regex("^(XAF vers BTC|XOF vers BTC|EUR vers BTC|USD vers BTC)$"),
                                   callback=achat_callback)],
            VENTE: [MessageHandler(filters=filters.Regex("^(BTC vers EUR|BTC vers USD)$"),
                                   callback=vente_callback)],
            MODE: [MessageHandler(filters=filters.Regex("^(Airtel Money|Orange Money|Carte Bancaire)$"),
                                  callback=mode_callback)],
            CARD_ACHAT: [MessageHandler(filters=filters.ALL,
                                        callback=card_payment_callback)],
        },
        fallbacks=[CommandHandler(command="cancel", callback=cancel)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler(
        command="start", callback=start_callback))
    application.add_handler(PreCheckoutQueryHandler(
        callback=precheckout_callback))

    application.add_handler(
        MessageHandler(filters=filters.SUCCESSFUL_PAYMENT,
                       callback=successful_payment_callback)
    )

    application.run_polling()


if __name__ == "__main__":
    main()
