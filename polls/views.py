import psycopg2
from django.shortcuts import render
import folium
from bs4 import BeautifulSoup
import math


def block():
    with open('templates/map1.html') as inf:
        txt = inf.read()
        soup = BeautifulSoup(txt)
    block_cont = '{% block content %}'
    end_cont = '{% endblock %}'
    # insert it into the document
    soup.append(block_cont)
    soup.append(end_cont)

    # save the file again
    with open('templates/map1.html', "w") as outf:
        outf.write(str(soup))


mappy = folium.Map(width=950, height=950, location=[59.939095, 30.315856], zoom_start=11)
mappy.save('templates/map1.html')
block()


def reset(request):
    map = folium.Map(width=950, height=950, location=[59.939095, 30.315856], zoom_start=11)
    mappy = map
    mappy.save('templates/map1.html')
    block()
    return render(request, 'base.html')


def marker(cord1_1, cord1_2, cord2_1, cord2_2):
    folium.Marker(location=[cord1_1, cord1_2], popup="Метка1", icon=folium.Icon(color='red')).add_to(mappy)
    folium.Marker(location=[cord2_1, cord2_2], popup="Метка2", icon=folium.Icon(color='blue')).add_to(mappy)
    mappy.save('templates/map1.html')
    block()


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
    dist = ad * rad
    dist = round(dist / 1000)

    return dist


def intoDb(request):
    con = psycopg2.connect(
        database="django_db",
        user="user_name",
        password="12345",
        host="127.0.0.1",
        port="5432"
    )

    print("Database opened successfully")
    cur = con.cursor()
    cur.execute(
        "INSERT INTO cooords (long1,width1,long2,width2,total) VALUES (%s,%s,%s,%s,%s)",
        (float(lst[0]), float(lst[1]), float(lst[2]), float(lst[3]), lst[4])
    )

    con.commit()
    print("Record inserted successfully")

    con.close()



lst = []


def get_value(request):
    try:
        lst.append(request.GET.get('cord1.1'))
        lst.append(request.GET.get('cord1.2'))
        lst.append(request.GET.get('cord2.1'))
        lst.append(request.GET.get('cord2.2'))
        lst.append(way(float(lst[0]), float(lst[1]), float(lst[2]), float(lst[3])))
        marker(lst[0], lst[1], lst[2], lst[3])

        return render(request, 'base.html')
    except ValueError:
        return render(request, 'base.html')


def mapp(request):
    return render(request, 'base.html')
