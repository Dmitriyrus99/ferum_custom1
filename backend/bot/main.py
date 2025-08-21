#!/usr/bin/env python

import asyncio
import logging

import frappe
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
API_TOKEN = frappe.conf.get("telegram_bot_token")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def send_welcome(message: types.Message):
	"""This handler will be called when user sends `/start` command"""
	await message.reply("Hi!\nI'm Ferum Bot!\nPowered by aiogram.")


@dp.message(Command("updatestatus"))
async def update_status(message: types.Message):
	"""This handler will be called when user sends `/updatestatus` command"""
	try:
		_, request_name, new_status = message.text.split()
	except ValueError:
		await message.reply("Usage: /updatestatus <request_name> <new_status>")
		return

	telegram_user_id = message.from_user.id

	# Get the ERPNext user associated with the Telegram user ID
	erpnext_user = frappe.get_value("User", {"telegram_user_id": telegram_user_id}, "name")

	if not erpnext_user:
		await message.reply("Your Telegram account is not linked to an ERPNext user.")
		return

	# Get the Service Request
	try:
		service_request = frappe.get_doc("ServiceRequest", request_name)
	except frappe.DoesNotExistError:
		await message.reply(f"Service Request {request_name} not found.")
		return

	# Check if the user is the assigned engineer
	if service_request.assigned_to != erpnext_user:
		await message.reply("You are not assigned to this request.")
		return

	# Update the status
	try:
		service_request.status = new_status
		service_request.save(ignore_permissions=True)  # Ignore permissions to allow bot to update
		await message.reply(f"Service Request {request_name} status updated to {new_status}.")
	except Exception as e:
		await message.reply(f"Failed to update status: {e}")


async def main():
	"""Start the bot."""
	# Start polling
	await dp.start_polling(bot)


if __name__ == "__main__":
	asyncio.run(main())
