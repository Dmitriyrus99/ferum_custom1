## Development Notes

This document outlines areas that require further development or manual configuration beyond the initial setup.

### 1. Google Sheets Integration

The `sync_to_google_sheets` method in `ferum_custom/ferum_custom/doctype/Invoice/invoice.py` has been updated with a more detailed placeholder. To enable actual synchronization with Google Sheets, you need to:

*   **Install `gspread`:** Add `gspread` to your ERPNext bench's `requirements.txt` or install it directly in your Frappe environment.
    ```bash
    # Example for bench
    cd /path/to/your/frappe-bench
    pip install gspread
    bench restart
    ```
*   **Refer to `backend/google_integration_notes.md`** for detailed instructions on setting up Google Cloud Project, enabling APIs, creating credentials (Service Account recommended), and configuring environment variables (`GOOGLE_APPLICATION_CREDENTIALS` or similar).
*   **Ensure Service Account access:** Share your Google Sheet (`Ferum Invoices Tracker` or your chosen name) with the email address of your Google Service Account.

### 2. Google Drive Integration

The `before_insert` and `on_trash` methods in `ferum_custom/ferum_custom/doctype/CustomAttachment/custom_attachment.py` have been updated with more detailed placeholders for Google Drive integration. To enable actual synchronization with Google Drive, you need to:

*   **Install `google-api-python-client`:** Add `google-api-python-client` to your ERPNext bench's `requirements.txt` or install it directly in your Frappe environment.
    ```bash
    # Example for bench
    cd /path/to/your/frappe-bench
    pip install google-api-python-client
    bench restart
    ```
*   **Refer to `backend/google_integration_notes.md`** for detailed instructions on setting up Google Cloud Project, enabling APIs, creating credentials (Service Account recommended), and configuring environment variables (`GOOGLE_APPLICATION_CREDENTIALS` or similar).
*   **Ensure Service Account access:** Share the relevant Google Drive folders with the email address of your Google Service Account.

### 4. Telegram Bot

A new service `telegram-bot` has been added to `docker-compose.yml` to run the Telegram bot. This service depends on the `frappe` service and runs the `backend/bot/main.py` script. To enable the bot, you need to:

*   **Set environment variables:** Ensure that `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` are set in your `.env` file.
*   **Link Telegram users to ERPNext users:** The bot identifies ERPNext users based on their Telegram user ID. You need to add a custom field `telegram_user_id` to the `User` doctype in ERPNext and populate it with the Telegram user IDs of the respective users.