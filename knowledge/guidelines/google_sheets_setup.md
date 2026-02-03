
## 6.7 Unified Client SDKs

All external service interactions are encapsulated in `engine/clients/`:

*   **`GeminiClient`**: Google Gemini AI (1.5 Pro/Flash).
    ```python
    gemini = GeminiClient(config, model="gemini-3-pro-preview")
    analysis = gemini.generate_content("Analyze this data...")
    ```
*   **`GoogleSheetClient`**: Spreadsheet Automation.
    ```python
    gs = GoogleSheetClient()
    # Open by Title
    sh = gs.open_sheet("Payment Report 2026")
    # Write DataFrame
    gs.write_dataframe(df, "Payment Report 2026", "Daily Data")
    ```
*   **`BaseClient`**: Abstract base for standarized configuration and logging.

## 6.8 Google Sheet Configuration
To enable Auto-Reporting to Google Sheets:

1.  **Service Account**: Ensure `secrets/kiwi-*.json` is present and `GOOGLE_APPLICATION_CREDENTIALS` is set.
2.  **Shared Folder (Critical)**: Create a Google Drive Folder and share it with the Service Account Email (Editor Role).
3.  **Config**: Add the `folder_id` to your App Config:
    ```yaml
    delivery:
      google_drive:
        folder_id: "${GOOGLE_DRIVE_FOLDER_ID}" # Use Env Var
        share_with: ["user@example.com"]
    ```
4.  **Workflow**: The script will automatically create Sheets in this folder, bypassing Service Account storage quotas.
