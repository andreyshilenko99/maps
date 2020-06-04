import psycopg2
from django.shortcuts import render
import folium
from bs4 import BeautifulSoup
import math
from socket import *


# добавление block и endblock элементов в html с картой


def block():
    with open('templates/map1.html') as inf:
        txt = inf.read()
        soup = BeautifulSoup(txt, "html.parser")
    block_cont = '{% block content %}'
    end_cont = '{% endblock %}'

    soup.append(block_cont)
    soup.append(end_cont)
    # запись в html
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
            # пробуем записать полученные данные в таблицу дб
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
        # отчиска временного листа
        lst.clear()
        return render(request, 'base.html',
                      {'cord1': getLastFromDb()[0],
                       'cord2': getLastFromDb()[1],
                       'cord3': getLastFromDb()[2],
                       'cord4': getLastFromDb()[3],
                       'cord5': getLastFromDb()[4]})
    except IndexError:
        return render(request, 'base.html')


lst = []  # список в котором временно хранятся координаты и расстояние


#  получение значений которые были введены в текстбоксы
def getValue(request):
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
                      {'cord1_1': lst[0],
                       'cord1_2': lst[1],
                       'cord2_1': lst[2],
                       'cord2_2': lst[3],
                       'long': lst[4]})
    except ValueError:
        return render(request, 'base.html')


def getLastFromDb():
    #подключение к дб
    con = psycopg2.connect(
        database="django_db",
        user="user_name",
        password="12345",
        host="127.0.0.1",
        port="5432"
    )
    cur = con.cursor()
    cur.execute("SELECT * from cooords order by id desc")
    result = cur.fetchone()
    return result


def run(request):
    try:
        addr = ('localhost', 7777)
        tcp_socket = socket(AF_INET, SOCK_STREAM)
        tcp_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    # bind - связывает адрес и порт с сокетом
        tcp_socket.bind(addr)
    # listen - запускает прием TCP
        tcp_socket.listen(1)
    # Бесконечный цикл работы программы
        while True:

            #кидаем последнюю запись
            conn, addr = tcp_socket.accept()
            print('client addr: ', addr)
            try:
                getLastFromDb()
                conn.send(bytes(str.encode(str(getLastFromDb()[0]))))
                conn.send(bytes(str.encode(str(getLastFromDb()[1]))))
                conn.send(bytes(str.encode(str(getLastFromDb()[2]))))
                conn.send(bytes(str.encode(str(getLastFromDb()[3]))))
                conn.send(bytes(str.encode(str(getLastFromDb()[4]))))
            except TypeError:
                return render(request, 'base.html')
    except OSError:
       return render(request, 'base.html')
