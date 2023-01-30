import requests
from bs4 import BeautifulSoup
from prettytable import PrettyTable
from time import sleep


headers = {"Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
           "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                         "(KHTML, like Gecko) Chrome/106.0.0.0 YaBrowser/22.11.5.715 Yowser/2.5 Safari/537.36"}


print("Поиск авто на сайте дром.ру")
sleep(1)
print("-" * 40)
prices = input("1/5.Укажите диапазон цен через пробел: ").split()
mileage = input("2/5.Укажите минимальный и максимальный пробег через пробел: ").split()
year = input("3/5.Год машины от и до через пробел: ").split()
distance = int(input("4/5 Искать объявления в радиусе:\n1. Только Санкт-Петербург\n2. Санкт-Петербург + 100 км"
                     "\n3. Санкт-Петербург + 200 км\n4. Санкт-Петербург + 500 км\nУкажите число: "))
sort_by = int(input(f"5/5 Сортировать по: \n1. Новые объявления\n2. Старые объявления"
                    f"\n3. С низкой ценой\n4. С высокой ценой\n5. С отличной ценой\nУкажите число: "))
url = f"https://spb.drom.ru/auto/all/page1?minprice={prices[0]}&" \
      f"maxprice={prices[1]}&minyear={year[0]}&maxyear={year[1]}" \
      f"&inomarka=1&unsold=1&minprobeg={mileage[0]}&maxprobeg={mileage[1]}&"


def pretty_table(model_info, main_info, price_info, link_info):
    table = PrettyTable(["Название модели", "Информация", "Цена", "Ссылка"])
    table.add_row([model_info, main_info, price_info, link_info])
    print(table)


def get_distance_search():
    dist = ""
    if distance == 1:
        pass
    elif distance == 2:
        dist += "100"
    elif distance == 3:
        dist += "200"
    elif distance == 4:
        dist += "500"

    return dist


def get_url_content(link: str):
    url_response = requests.get(link, headers=headers)
    soup = BeautifulSoup(url_response.text, "html.parser")
    try:
        get_parser = soup.find_all("a", class_="css-xb5nz8 e1huvdhj1")
        if get_parser:
            return get_parser
        else:
            get_response = soup.find("div", class_="css-1evbgq9 e1lm3vns0").get_text()
            if get_response:
                print(get_response)

    except AttributeError:
        pass


def get_count_of_pages():
    url_response = requests.get(url, headers=headers)
    soup = BeautifulSoup(url_response.text, "html.parser")
    try:
        get_count = soup.find("a", class_="css-192eo94 e1px31z30").get_text()
        if get_count:
            count_split = get_count.split()[0]
            pages_count = int(count_split) // 20
            return get_count, pages_count
    except AttributeError:
        print("Ошибка! Страниц по такому запросу не найдено.")


def order_by():
    order = ""
    if sort_by == 1:
        order += "order_d=desc"
    elif sort_by == 2:
        order += "order_d=asc"
    elif sort_by == 3:
        order += "order=price"
    elif sort_by == 4:
        order += "order=price&order_d=desc"
    elif sort_by == 5:
        order += "order=price_category"

    return order


def parsing(value: str):
    info_list = []
    result = get_url_content(link=value)
    for i in result:
        info_list.append(
            {
                "Модель": i.find("div", class_="css-17lk78h e3f4v4l2").get_text(),
                "Информация": i.find("div", class_="css-1fe6w6s e162wx9x0").get_text(),
                "Цена": i.find("div", class_="css-1dv8s3l eyvqki91").get_text(),
                "Ссылка": i.get("href")
            }
        )
    for elem in info_list:
        for key in elem:
            if key == "Модель":
                model = elem[key]
            elif key == "Информация":
                info = elem[key]
            elif key == "Цена":
                price = elem[key]
            elif key == "Ссылка":
                link = elem[key]

        pretty_table(model_info=model, main_info=info, price_info=price, link_info=link)


if __name__ == "__main__":
    order = order_by()
    dist = get_distance_search()
    for page in range(1, get_count_of_pages()[1] + 1):
        print(f"Парсинг {page} страницы...")
        main_url = f"https://spb.drom.ru/auto/all/page{page}?minprice={prices[0]}&" \
            f"maxprice={prices[1]}&minyear={year[0]}&maxyear={year[1]}" \
            f"&inomarka=1&unsold=1&minprobeg={mileage[0]}&maxprobeg={mileage[1]}&{order}&distance={dist}"
        parsing(value=main_url)
        sleep(1)

    print(f"По вашему запросу было найдено {get_count_of_pages()[0]}\nБыло выведено: "
          f"{get_count_of_pages()[1] * 20}/{get_count_of_pages()[0]}")
    print(f"Для дальнейшего ознакомления Вы можете перейти по ссылке {main_url}")
