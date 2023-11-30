import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime, timedelta

def get_meal_url_for_date(meal_type, target_date):
    return f"https://www.mealtify.com/univ/pusan/gumjeong-student/meal/{target_date}/{meal_type}"

def scrape_and_write_to_csv(url, meal_type, csv_file, target_date):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error: Failed to retrieve the page. Status code: {response.status_code}")
        return
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    menu_elements = soup.find_all('td', class_='px-4 py-3 text-center')
    menu_values = [element.text for element in menu_elements]

    # Extract only the first value from each element
    menu_list = [menu_values[i] for i in range(0, len(menu_values), 3)]

    # CSV 파일에 작성 함수
    def write_to_csv(menu_data):
        with open(csv_file, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(menu_data)

    # 메뉴 리스트에서 '총 칼로리' 항목을 찾아 나누기
    calories_index = None
    for i, item in enumerate(menu_list):
        if '총 칼로리:' in item:
            calories_index = i
            break

    # 메뉴 리스트를 나누기
    if calories_index is not None:
        menu_part1 = " ".join(menu_list[:calories_index])
        menu_part2 = " ".join(menu_list[calories_index + 1:])
    else:
        menu_part1 = " ".join(menu_list)
        menu_part2 = ""

    # CSV 파일에 작성
    write_to_csv([menu_part1, meal_type, target_date])
    write_to_csv([menu_part2, meal_type, target_date]) if calories_index is not None else None

# Define meal types
meal_types = ["breakfast", "lunch", "dinner"]

# Define CSV file path
csv_file_path = "menu_student.csv"

# Write header to CSV file
with open(csv_file_path, mode='w', encoding='utf-8', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["메뉴", "타입", "시간"])

# Loop through next 5 days or until Saturday
current_date = datetime.now()
start_of_week = current_date - timedelta(days=current_date.weekday())

# Loop through weekdays (Monday to Friday) of the current week
for _ in range(5):
    target_date = start_of_week.strftime("%Y-%m-%d")
    
    # Loop through meal types and scrape, and write to CSV
    for meal_type in meal_types:
        meal_url = get_meal_url_for_date(meal_type, target_date)
        scrape_and_write_to_csv(meal_url, meal_type, csv_file_path, target_date)
    
    start_of_week += timedelta(days=1)

print("이번주 월요일부터 금요일까지의 파일이 생성되었습니다.")