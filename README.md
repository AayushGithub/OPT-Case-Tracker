# OPT Case Tracker

#### Track your OPT case status with Python. Scrape USCIS website, get real-time updates.

**OPT Case Tracker** is a Python application that allows users to track the status of their OPT (Optional Practical Training) cases on the USCIS (United States Citizenship and Immigration Services) website. It provides a convenient way to scrape case statuses for a given OPT case number and a specified number of cases to search around that number.

## Features

- Scrapes case statuses
- Multiprocessing and threading for faster scraping
- Progress updates with a progress bar
- Summary statistics of approved, denied, and pending cases
- Caching for faster subsequent runs
- Optional Logging support
- Optional Graphical representation of summary statistics

## Usage

1. Clone the repository and navigate to the project directory.
2. Install the required dependencies listed in `requirements.txt`.
3. Run the `main.py` script.
4. Enter the OPT case number and select the number of cases to search around.
5. The app will display a progress bar and retrieve the case statuses.
6. Once the scraping is complete, the app will display the case numbers, statuses, and summary statistics.

## Dependencies

- `beautifulsoup4`
- `requests`
- `tqdm`
- `questionary`
- `matplotlib`

Refer to `requirements.txt` for specific versions.

---

**Note:** This project was developed for educational purposes and to showcase web scraping techniques. Use it responsibly and respect the USCIS website's terms of use.

