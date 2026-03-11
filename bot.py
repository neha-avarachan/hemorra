import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from database import db, User, BloodRequest, DonorResponse
from datetime import datetime, timedelta
from app import app

BOT_TOKEN = "YOUR_TOKEN_HERE"

# --- /start command ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    
    with app.app_context():
        # Check if this telegram is already linked
        user = User.query.filter_by(telegram_chat_id=chat_id).first()
        
        if user:
            await update.message.reply_text(
                f"Welcome back {user.name}! 🩸\n"
                f"You are registered as an {user.blood_group} donor.\n"
                f"You will receive alerts when someone needs your blood group."
            )
        else:
            await update.message.reply_text(
                "👋 Welcome to Hemorra!\n\n"
                "To link your Telegram to your donor account, "
                "please send your registered college email address."
            )
            context.user_data['waiting_for_email'] = True

# --- Handle text messages ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    text = update.message.text.strip()

    with app.app_context():

        # --- Linking email ---
        if context.user_data.get('waiting_for_email'):
            user = User.query.filter_by(email=text).first()
            
            if user:
                user.telegram_chat_id = chat_id
                db.session.commit()
                context.user_data['waiting_for_email'] = False
                await update.message.reply_text(
                    f"✅ Successfully linked!\n\n"
                    f"Hello {user.name}! You are now registered as "
                    f"an {user.blood_group} donor in Hemorra.\n\n"
                    f"You will receive blood request alerts here. "
                    f"Make sure your notifications are turned on! 🔔"
                )
            else:
                await update.message.reply_text(
                    "❌ Email not found. Please make sure you are "
                    "registered on the Hemorra website first.\n\n"
                    "Visit the website and register as a donor, "
                    "then come back and send your email here."
                )
            return

        # --- YES response ---
        if text.upper() == "YES":
            user = User.query.filter_by(telegram_chat_id=chat_id).first()
            
            if not user:
                await update.message.reply_text(
                    "Please link your account first by sending /start"
                )
                return

            # Find their most recent notified request
            response = DonorResponse.query.join(BloodRequest).filter(
                DonorResponse.donor_id == user.id,
                DonorResponse.status == 'notified',
                BloodRequest.status == 'active'
            ).order_by(DonorResponse.created_at.desc()).first()

            if response:
                response.status = 'confirmed'
                db.session.commit()

                blood_req = BloodRequest.query.get(response.request_id)
                await update.message.reply_text(
                    f"Thank you! 🙏\n\n"
                    f"The requester's number is {blood_req.requester_phone}\n"
                    f"Please call them directly to coordinate.\n\n"
                    f"After donating, reply DONE so we can "
                    f"update your donor status. 🩸"
                )
            else:
                await update.message.reply_text(
                    "No active request found. "
                    "The request may have already been fulfilled."
                )
            return

        # --- NO response ---
        if text.upper() == "NO":
            user = User.query.filter_by(telegram_chat_id=chat_id).first()
            
            if not user:
                await update.message.reply_text(
                    "Please link your account first by sending /start"
                )
                return

            response = DonorResponse.query.join(BloodRequest).filter(
                DonorResponse.donor_id == user.id,
                DonorResponse.status == 'notified',
                BloodRequest.status == 'active'
            ).order_by(DonorResponse.created_at.desc()).first()

            if response:
                response.status = 'declined'
                db.session.commit()

            await update.message.reply_text(
                "No problem! We'll check back next time.\n"
                "Thank you for being registered 🙏"
            )
            return

        # --- DONE response ---
        if text.upper() == "DONE":
            user = User.query.filter_by(telegram_chat_id=chat_id).first()
            
            if not user:
                await update.message.reply_text(
                    "Please link your account first by sending /start"
                )
                return

            # Mark unavailable for 90 days
            user.is_available = False
            user.next_eligible_date = datetime.utcnow() + timedelta(days=90)
            user.donate_count += 1

            # Mark the response as donated
            response = DonorResponse.query.join(BloodRequest).filter(
                DonorResponse.donor_id == user.id,
                DonorResponse.status == 'confirmed',
                BloodRequest.status == 'active'
            ).order_by(DonorResponse.created_at.desc()).first()

            if response:
                response.status = 'donated'
                # Mark request as fulfilled
                response = DonorResponse.query.filter_by(
                           donor_id=donor.id,
                           status='confirmed'
            ).order_by(DonorResponse.id.desc()).first()

            if response:
               blood_request = BloodRequest.query.get(response.request_id)
            if blood_request:
               blood_request.status = 'fulfilled'
               db.session.commit()

            await update.message.reply_text(
                f"You're a hero! 🎉\n\n"
                f"You have donated {user.donate_count} time(s).\n"
                f"You will be marked unavailable for 90 days.\n"
                f"You can donate again after "
                f"{user.next_eligible_date.strftime('%d %B %Y')}.\n\n"
                f"Thank you for saving a life! 🩸"
            )
            return

        # --- Default response ---
        await update.message.reply_text(
            "I didn't understand that.\n\n"
            "If you received a blood request, reply:\n"
            "YES — to confirm you can donate\n"
            "NO — if you cannot donate right now\n"
            "DONE — after you have donated\n\n"
            "Send /start to link your account."
        )

# --- Run the bot ---
def run_bot():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot is running...")
    application.run_polling()

if __name__ == '__main__':
    run_bot()