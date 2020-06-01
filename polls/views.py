import psycopg2
from django.shortcuts import render
import folium
from bs4 import BeautifulSoup
import math
import socket

# добавление block и endblock элементов в html с картой
def block():
    with open('templates/map1.html') as inf:
        txt = inf.read()
        soup = BeautifulSoup(txt, "html.parser")
    block_cont = '{% block content %}'
    end_cont = '{% endblock %}'

    soup.append(block_cont)
    soup.append(end_cont)

    with open('templates/map1.html', "w") as outf:
        outf.write(str(soup))


# отчистка от маркеров
def map():
    mappy = folium.Map(width=950, height=950, location=[59.939095, 30.315856], zoom_start=11)  # карта
    mappy.save('templates/map1.html')
    block()
    return mappy


# сброс маркеров и значиней в текстбоксах
def reset(request):
    map()
    lst.clear()
    return render(request, 'base.html')


# добавление маркеров нв карту
def marker(cord1_1, cord1_2, cord2_1, cord2_2):
    mappy = map()
    folium.Marker(location=[cord1_1, cord1_2], popup="Метка1", icon=folium.Icon(color='red')).add_to(mappy)
    folium.Marker(location=[cord2_1, cord2_2], popup="Метка2", icon=folium.Icon(color='blue')).add_to(mappy)
    mappy.save('templates/map1.html')
    block()


# расчет расстояния между точками
def way(cord1_1, cord1_2, cord2_1, cord2_2):
    rad = 6372795
    # в радианах
    lat1 = cord1_1 * math.pi / 180
    lat2 = cord2_1 * math.pi / 180
    long1 = cord1_2 * math.pi / 180
    long2 = cord2_2 * math.pi / 180

    # косинусы и синусы широт и разницы долгот
    cl1 = math.cos(lat1)
    cl2 = math.cos(lat2)
    sl1 = math.sin(lat1)
    sl2 = math.sin(lat2)
    delta = long2 - long1
    cdelta = math.cos(delta)
    sdelta = math.sin(delta)

    # вычисления длины большого круга
    y = math.sqrt(math.pow(cl2 * sdelta, 2) + math.pow(cl1 * sl2 - sl1 * cl2 * cdelta, 2))
    x = sl1 * sl2 + cl1 * cl2 * cdelta
    ad = math.atan2(y, x)
    dist = round(ad * rad / 1000)

    return dist


# запись координат и расстояния в бд
def intoDb(request):
    try:
        map()
        con = psycopg2.connect(
            database="django_db",
            user="user_name",
            password="12345",
            host="127.0.0.1",
            port="5432"
        )

        print("Database opened successfully")
        cur = con.cursor()
        try:
            cur.execute(
                "INSERT INTO cooords (long1,width1,long2,width2,total) VALUES (%s,%s,%s,%s,%s)",
                (float(lst[0]), float(lst[1]), float(lst[2]),
                float(lst[3]), lst[4])
            )
        except ValueError:
            return render(request, 'base.html')

        con.commit()
        print("Record inserted successfully")

        con.close()
        lst.clear()
        return render(request, 'base.html')
    except IndexError:
        return render(request, 'base.html')


lst = []  # список в котором временно хранятся координаты и расстояние


#  получение значений которые были введены в текстбоксы
def get_value(request):
    try:
        if lst:
            lst.clear()
            map()
        lst.append(request.POST.get('cord1.1'))
        lst.append(request.POST.get('cord1.2'))
        lst.append(request.POST.get('cord2.1'))
        lst.append(request.POST.get('cord2.2'))
        lst.append(way(float(lst[0]), float(lst[1]), float(lst[2]), float(lst[3])))
        marker(lst[0], lst[1], lst[2], lst[3])
        return render(request, 'base.html',
                      {'cord1_1': lst[0], 'cord1_2': lst[1], 'cord2_1': lst[2], 'cord2_2': lst[3], 'long': lst[4]})
    except ValueError:
        return render(request, 'base.html')


def run(request):
    # Задаем адрес сервера
    SERVER_ADDRESS = ('localhost', 8686)

    # Настраиваем сокет
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(SERVER_ADDRESS)
    server_socket.listen(10)
    print('server is running, please, press ctrl+c to stop')

    # Слушаем запросы
    while True:
        connection, address = server_socket.accept()
        print("new connection from {address}".format(address=address))

        data = connection.recv(1024)
        print(str(data))

        connection.send(bytes('Hello from server!', encoding='UTF-8'))

        connection.close()
