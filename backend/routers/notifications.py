from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ..auth import has_role

router = APIRouter()


class NotificationPayload(BaseModel):
	chat_id: int
	text: str


@router.post("/send_telegram_notification")
async def send_telegram_notification_endpoint(
	payload: NotificationPayload,
	current_user: str = Depends(has_role(["Administrator", "Department Head"])),
):
	"""Proxy endpoint that forwards messages to the Telegram bot.

	Importing the Telegram bot lazily avoids requiring the `aiogram` package
	during test collection.
	"""
	try:
		from ..bot.telegram_bot import send_telegram_message

		await send_telegram_message(payload.chat_id, payload.text)
		return {"message": "Notification sent successfully"}
	except Exception as e:  # pragma: no cover - defensive programming
		raise HTTPException(status_code=500, detail=f"Failed to send notification: {e}")
