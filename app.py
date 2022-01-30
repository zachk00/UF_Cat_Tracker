from flask import Flask, jsonify, request, render_template, url_for, redirect
from flask_simple_geoip import SimpleGeoIP
import folium
from folium import IFrame
from folium.plugins import MousePosition
import random
from datetime import datetime
import time
import csv
import base64

from forms import markerForm

app = Flask(__name__)

key = 'at_tf1OeUtMOTp6ytnrecumGzE9Bv3z9'
app.config.update(GEOIPIFY_API_KEY=key)
app.config['SECRET_KEY'] = 'SECRET_KEY'
simple_geoip = SimpleGeoIP(app)


@app.route('/map', methods=['GET', 'POST'])
def map_display():
    start_coords = (29.643399137864876, -82.35417539220363)
    cat_map = folium.Map(location=start_coords, zoom_start=14, tiles="CartoDB Positron", min_zoom=15, width=1000,
                         height=500)
    cat_map.fit_bounds([[29.621414432870953, -82.39113249625309], [29.66370335481807, -82.31791694753599]])

    displayMarkers(cat_map)

    cat_map.save(outfile='templates/folium.html')

    form = markerForm()

    if form.validate_on_submit():

        name = form.cats.data
        # check if it exists

        if name == "Other":
            name = form.other.data
            if name == "":
                name = "Unknown"
        filepath = '0'
        if form.doc.data:
            now = datetime.now()
            str_now = now.strftime("%d_%m_%Y_%H_%M_%S")
            form.doc.data.save('uploads/' + name + '_' + str_now)
            filepath = name + '_' + str_now

        # call get location
        coords = get_location('68.226.4.211')
        # then jacob stores the new point
        icon = ''
        if name in icons.keys():
            icon = name
        else:
            icon = 'Other'

        appendDatabase(name, coords[0], coords[1], icon, filepath)
        cat_map.save(outfile='templates/folium.html')
    return render_template('map.html', form=form)


@app.route('/')
@app.route('/home')
def home():
    animal_list = ['bob', 'sam', 'bill', 'greg']
    return render_template('home.html', animals=animal_list * 2)


def get_location(ip):
    geoip_data = simple_geoip.get_geoip_data()
    if geoip_data['ip'] == '127.0.0.1':

        return 29.646813396872624, -82.3415487053053

    else:
        loc_dict = geoip_data['location']
        coords = (loc_dict['lat'], loc_dict['lng'])
        return coords


# put it here #
catMarkers = []
debug = 'true'

icons = {
    "Alligator": "https://cdn-icons-png.flaticon.com/512/2622/2622233.png",
    "Armadillo": "https://static.wixstatic.com/media/b60bb2_63382cffce9f4f6b851d62b152212677~mv2.png",
    "Apollo": "https://static.wixstatic.com/media/b60bb2_700754aa4e164759beea0bf989438543~mv2.png",
    "Campus Cat #4": "https://static.wixstatic.com/media/b60bb2_700754aa4e164759beea0bf989438543~mv2.png",
    "Tenders": "https://static.wixstatic.com/media/b60bb2_700754aa4e164759beea0bf989438543~mv2.png",
    "Ryan the Engineering Cat": "https://static.wixstatic.com/media/b60bb2_700754aa4e164759beea0bf989438543~mv2.png",
    "Dog": "https://static.wixstatic.com/media/b60bb2_f1dfd1fd25eb4f0a8d96f252d5a14bf9~mv2.png",
    "Raccoon": "https://cdn-icons-png.flaticon.com/512/2301/2301457.png",
    "Other": "https://cdn-icons-png.flaticon.com/512/3135/3135556.png"
}

iconColors = {
    "Alligator": "darkgreen",
    "Apollo": "white",
    "Armadillo": "gray",
    "Campus Cat #4": "pink",
    "Dog": "red",
    "Raccoon": "black",
    "Ryan the Engineering Cat": "cadetblue",
    "Tenders": "orange",
    "Other": "purple"
}


class cat:
    name = ''
    location = (29.643399137864876, -82.35417539220363)
    icon = ''
    image = '0'
    spotTime = 0

    def __init__(self, name, location, icon, image):
        self.name = name
        self.location = location
        self.icon = icon
        if image != '0':
            self.image = "uploads/" + image
        self.spotTime = time.time()

    def timeSince(self):
        # turn seconds to minutes
        if (time.time() - self.spotTime) >= 60:
            return int((time.time() - self.spotTime) / 60)
        else:
            return 0


def displayMarkers(cat_map):
    if debug == 'true':
        loadDatabase()

    if len(catMarkers) > 0:
        for thisCat in catMarkers:

            iconColor = iconColors[thisCat.name]

            if thisCat.image == '0':
                folium.Marker(
                    location=(float(thisCat.location[0]), float(thisCat.location[1])),
                    popup=thisCat.name,
                    icon=folium.DivIcon('<img src="{}" width="36" height="36">'.format(icons[thisCat.icon])),
                    tooltip=thisCat.name + " (Seen " + str(thisCat.timeSince()) + "m ago)"
                ).add_to(cat_map)
            else:
                encoded = base64.b64encode(open(thisCat.image, 'rb').read())
                html = '<img src="data:image/png;base64,{}" width="256" height ="256"/>'.format
                iframe = IFrame(html(encoded.decode('UTF-8'), thisCat.name), width=256, height=256)
                newPopup = folium.Popup(iframe, max_width=300)
                folium.Marker(
                    location=(float(thisCat.location[0]), float(thisCat.location[1])),
                    popup=newPopup,
                    icon=folium.DivIcon('<img src="{}" width="36" height="36">'.format(icons[thisCat.icon])),
                    tooltip="📸 " + thisCat.name + " (Seen " + str(thisCat.timeSince()) + "m ago)"
                ).add_to(cat_map)


"""
            folium.CircleMarker(
                location=(thisCat.location[0], thisCat.location[1]),
                radius=32,
                color=iconColor,
                fill=True,
                fill_color=iconColor,
            ).add_to(cat_map)
"""


def loadDatabase():
    with open('markerDatabase.csv') as f:
        reader = csv.reader(f)
        for row in reader:
            newCat = cat(row[0], (row[1], row[2]), row[3], row[4])
            catMarkers.append(newCat)


def appendDatabase(name, lat, long, icon, image):
    list = [name, lat, long, icon, image]
    with open('markerDatabase.csv', 'a', newline='') as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerow(list)



if __name__ == '__main__':
    app.run()
