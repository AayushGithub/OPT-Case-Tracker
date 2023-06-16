import os
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import questionary
import logging
import json
from functools import wraps
import hashlib
import matplotlib.pyplot as plt

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Cache decorator
def cache_result(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        cache_key = hashlib.md5(json.dumps((args, kwargs)).encode('utf-8')).hexdigest()
        cache_file = f".cache/{cache_key}.json"

        if not os.path.exists(".cache"):
            os.makedirs(".cache")

        try:
            with open(cache_file, 'r') as f:
                result = json.load(f)
                logger.info(f"Cache hit for {func.__name__}({args}, {kwargs})")
                return result
        except FileNotFoundError:
            result = func(*args, **kwargs)
            with open(cache_file, 'w') as f:
                json.dump(result, f)
                logger.info(f"Cache miss for {func.__name__}({args}, {kwargs})")
            return result

    return wrapper


@cache_result
def poll_optstatus(casenumber):
    headers = {
        'Accept': 'text/html, application/xhtml+xml, image/jxr, */*',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language':
        'en-US, en; q=0.8, zh-Hans-CN; q=0.5, zh-Hans; q=0.3',
        'Cache-Control': 'no-cache',
        'Connection': 'Keep-Alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'egov.uscis.gov',
        'Referer': 'https://egov.uscis.gov/casestatus/mycasestatus.do',
        'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.10586'
    }
    url = "https://egov.uscis.gov/casestatus/mycasestatus.do"
    data = {"appReceiptNum": casenumber, 'caseStatusSearchBtn': 'CHECK+STATUS'}

    try:
        res = requests.post(url, data=data, headers=headers)
        res.raise_for_status()  # Raise an exception if response status is an error

        soup = BeautifulSoup(res.text, "html.parser")
        status_element = soup.find("h1")
        details_element = soup.find(class_="text-center").find("p")

        if status_element:
            status = status_element.text.strip()
        else:
            status = None

        if details_element:
            details = details_element.text.strip()
        else:
            details = None

        return status, details

    except ConnectionError as e:
        print("Connection Error:", e)
        return None, None


def scrape_case_statuses(case_number, num_cases, enable_logging=True):
    prefix = case_number[:-10]
    start_number = int(case_number[-10:])
    case_numbers = [f"{prefix}{start_number + i:010}" for i in range(-num_cases, num_cases + 1)]

    results = []

    with ThreadPoolExecutor() as executor, tqdm(total=len(case_numbers), desc="Scraping") as pbar:
        for case_num, result in zip(case_numbers, executor.map(poll_optstatus, case_numbers)):
            if result[0] is not None:  # Exclude cases with no meaningful status
                results.append((case_num, result))
            pbar.update(1)

    return results

if __name__ == "__main__":
    case_number = questionary.text("Enter the OPT case number:").ask()
    num_cases = questionary.select(
        "Select the number of cases to search around:",
        choices=["±10", "±20", "±30", "±40", "±50", questionary.Separator(), "Other"]
    ).ask()

    if num_cases == "Other":
        num_cases = questionary.text("Enter the number of cases to search around:").ask()
        num_cases = int(num_cases)
    else:
        num_cases = int(num_cases[1:])  # Extract the number from the selected choice

    # Ask a question if you want to enable logging
    enable_logging = questionary.confirm("Do you want to enable logging?").ask()
    if not enable_logging:
        logger.disabled = True

    results = scrape_case_statuses(case_number, num_cases)

    approved_count = 0
    denied_count = 0
    pending_count = 0

    for case_num, (status, details) in results:
        if status and details:
            print(f"Case Number: {case_num}")
        if status:
            print(f"Status: {status}")
        if details:
            print(f"Details: {details}\n")

        list_of_approved = ["Approved",
                            "Card Was Delivered To Me By The Post Office",
                            "Card Was Picked Up By The United States Postal Service",
                            "Certificate Of Naturalization Was Issued"]

        list_of_denied = ["Denied",
                          "Case Was Rejected Because It Was Improperly Filed",
                          "Interview Cancelled"]

        list_of_pending = ["Received", "Travel Authorization Decision Posted"]

        if any(x in status for x in list_of_approved):
            approved_count += 1
        elif any(x in status for x in list_of_denied):
            denied_count += 1
        elif any(x in status for x in list_of_pending):
            pending_count += 1

    print("\nSummary:")
    print(f"Approved cases: {approved_count}")
    print(f"Denied cases: {denied_count}")
    print(f"Pending cases: {pending_count}")

    generate_chart = questionary.confirm("Do you want to generate a pie chart based on the results?").ask()
    if generate_chart:
        labels = ["Approved", "Denied", "Pending"]
        values = [approved_count, denied_count, pending_count]
        colors = ["green", "red", "yellow"]
        explode = (0.1, 0, 0)
        plt.figure(figsize=(10, 10))
        plt.pie(values, labels=labels, colors=colors, explode=explode, autopct="%1.1f%%", shadow=True, startangle=140)
        plt.axis("equal")
        plt.title("OPT Case Status")
        plt.show()
