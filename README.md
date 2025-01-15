# Twitter Stakeholder Monitoring Tool
A Streamlit-based web application for monitoring and analyzing Twitter activity of selected stakeholders. This tool allows users to track and extract relevant tweets based on custom search criteria and time periods.

## Features

- Interactive stakeholder selection from a predefined list
- Custom date range selection for tweet monitoring
- Keyword-based search functionality
- Bulk stakeholder selection option
- Export capabilities to Excel
- Concurrent processing for efficient data retrieval
- Clean and intuitive user interface

## Technical Details
Built with:

Streamlit for the web interface
snscrape for Twitter data extraction
pandas for data manipulation
concurrent.futures for parallel processing
xlsxwriter for Excel export functionality

## Usage
The application provides a user-friendly interface where you can:

- Select custom date ranges for tweet monitoring
- Choose specific stakeholders or select all
- Enter keywords for filtering tweets
- Export results to Excel for further analysis
