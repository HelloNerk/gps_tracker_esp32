from flask import Flask, request, jsonify, render_template_string
from datetime import datetime

app = Flask(__name__)

# Lista en memoria para guardar coordenadas
gps_data = []

# Página HTML con mapa Leaflet y botón de borrado
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Mapa GPS en tiempo real</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.3/dist/leaflet.css"/>
  <script src="https://unpkg.com/leaflet@1.9.3/dist/leaflet.js"></script>
  <style>
    body { margin: 0; padding: 0; font-family: sans-serif; }
    #map { width: 100vw; height: 100vh; }
    #controls {
      position: absolute;
      top: 10px;
      left: 50%;
      transform: translateX(-50%);
      z-index: 1000;
      background: white;
      padding: 10px 15px;
      border-radius: 8px;
      box-shadow: 0 2px 6px rgba(0,0,0,0.2);
    }
    button {
      background-color: #0078d7;
      border: none;
      color: white;
      padding: 8px 12px;
      border-radius: 5px;
      cursor: pointer;
    }
    button:hover {
      background-color: #005fa3;
    }
  </style>
</head>
<body>
  <div id="controls">
    <button onclick="clearMarkers()">🗑️ Borrar marcadores</button>
  </div>
  <div id="map"></div>

  <script>
    const map = L.map('map').setView([0, 0], 2);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '© OpenStreetMap'
    }).addTo(map);

    let markers = [];
    let polyline = null;

    async function updateMap() {
      const res = await fetch('/api/gps');
      const data = await res.json();

      // Limpiar marcadores anteriores
      markers.forEach(m => map.removeLayer(m));
      if (polyline) map.removeLayer(polyline);

      if (data.length === 0) return;

      const latlngs = [];

      data.forEach(point => {
        const marker = L.marker([point.lat, point.lon]).addTo(map);
        marker.bindPopup(`📍 ${point.lat.toFixed(5)}, ${point.lon.toFixed(5)}<br>${point.time}`);
        markers.push(marker);
        latlngs.push([point.lat, point.lon]);
      });

      polyline = L.polyline(latlngs, { color: 'blue' }).addTo(map);
      map.fitBounds(polyline.getBounds());
    }

    async function clearMarkers() {
      const res = await fetch('/api/gps/clear', { method: 'POST' });
      const result = await res.json();
      alert(result.message);
      updateMap();
    }

    updateMap();
    setInterval(updateMap, 5000);
  </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/api/gps', methods=['GET', 'POST'])
def gps():
    global gps_data

    if request.method == 'POST':
        data = request.json
        if data and 'lat' in data and 'lon' in data:
            data['time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            gps_data.append(data)
            print(f"📍 Nueva coordenada: {data}")
        return jsonify({"status": "ok"})

    return jsonify(gps_data)

@app.route('/api/gps/clear', methods=['POST'])
def clear_gps():
    global gps_data
    gps_data = []
    print("🧹 Todos los marcadores han sido borrados.")
    return jsonify({"status": "ok", "message": "Todos los marcadores han sido borrados."})

@app.route('/ping')
def ping():
    return jsonify({"status": "alive"})

# Azure ejecutará esta variable automáticamente
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
