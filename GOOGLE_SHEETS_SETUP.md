# Google Sheets Integration Setup Guide

This guide will help you set up the Google Sheets API integration for the SEO scraper.

## Prerequisites

1. A Google account
2. Python with pip installed
3. The required Python packages (install with `pip install -r requirements.txt`)

## Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Enter a project name (e.g., "SEO Scraper")
4. Click "Create"

## Step 2: Enable Google Sheets API

1. In your Google Cloud project, go to "APIs & Services" → "Library"
2. Search for "Google Sheets API"
3. Click on "Google Sheets API" and then "Enable"

## Step 3: Create Service Account Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "Service Account"
3. Fill in the service account details:
   - Name: "seo-scraper-service"
   - Description: "Service account for SEO scraper"
4. Click "Create and Continue"
5. Skip the optional steps and click "Done"

## Step 4: Generate JSON Key

1. In the Credentials page, click on your service account
2. Go to the "Keys" tab
3. Click "Add Key" → "Create new key"
4. Choose "JSON" format
5. Click "Create"
6. The JSON file will download automatically

## Step 5: Set Up the Credentials File

1. Rename the downloaded JSON file to `credentials.json`
2. Place it in the same directory as your `seo_selenium_scraper.py` file
3. **Important**: Add `credentials.json` to your `.gitignore` file to keep it secure

## Step 6: Share Google Sheets (Optional)

If you want to use an existing Google Sheets file:

1. Create a new Google Sheets file or use an existing one
2. Click "Share" in the top right
3. Add your service account email (found in the credentials.json file) with "Editor" permissions
4. The service account email will look like: `seo-scraper-service@your-project-id.iam.gserviceaccount.com`

## Usage

Once set up, the scraper will automatically:

1. Create a new Google Sheets file named "SEO Scraper Results" (or use existing if shared)
2. Create two worksheets:
   - "AIO Results": Contains the main scraping results
   - "Domain Analysis": Contains domain frequency analysis
3. Export all results directly to Google Sheets
4. Print the Google Sheets URL for easy access

## Troubleshooting

### Common Issues:

1. **"Service account not found"**: Make sure the credentials.json file is in the correct location
2. **"Permission denied"**: Ensure the Google Sheets API is enabled in your Google Cloud project
3. **"Spreadsheet not found"**: The script will create a new spreadsheet if it doesn't exist

### Security Notes:

- Never commit `credentials.json` to version control
- The service account has limited permissions and can only access files you explicitly share
- You can revoke access anytime from the Google Cloud Console

## Example Output

When the script runs successfully, you'll see output like:

```
[INFO] Opened existing spreadsheet: SEO Scraper Results
[INFO] Exported 5 results to Google Sheets
[INFO] Exported domain analysis to Google Sheets
[INFO] Google Sheets URL: https://docs.google.com/spreadsheets/d/1ABC...XYZ
[SUCCESS] Results exported to Google Sheets: https://docs.google.com/spreadsheets/d/1ABC...XYZ
``` 