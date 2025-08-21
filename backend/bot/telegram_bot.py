#!/usr/bin/env python

import frappe
from aiogram import Bot


async def send_telegram_message(chat_id: int, text: str) -> None:
	"""Sends a message to a Telegram chat using the configured bot."""
	bot_token = frappe.conf.get("telegram_bot_token")

	if not bot_token:
		frappe.log_error("Telegram bot token not set in site_config.json", "Telegram Bot Error")
		return

	bot = Bot(token=bot_token)
	try:
		await bot.send_message(chat_id=chat_id, text=text)
	except Exception as e:
		frappe.log_error(f"Failed to send Telegram message: {e!s}", "Telegram Bot Error")
	finally:
		# Close the bot session to avoid resource warnings
		await bot.session.close()
