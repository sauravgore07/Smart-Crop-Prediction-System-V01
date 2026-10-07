import { useEffect, useRef } from 'react'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl:       'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl:     'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
})

export default function MapView({ onLocationSelect, selectedLocation }) {
  const mapRef      = useRef(null)
  const mapInstance = useRef(null)
  const markerRef   = useRef(null)

  // Always hold the latest onLocationSelect without re-initialising the map.
  // The click handler below reads this ref, so it never goes stale.
  const onLocationSelectRef = useRef(onLocationSelect)
  useEffect(() => {
    onLocationSelectRef.current = onLocationSelect
  }, [onLocationSelect])

  // ── Initialise map once ───────────────────────────────────────────────────
  useEffect(() => {
    if (mapInstance.current) return

    const map = L.map(mapRef.current, {
      center: [20.5937, 78.9629],
      zoom: 5,
    })

    const satellite = L.tileLayer(
      'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
      { attribution: 'Tiles © Esri', maxZoom: 19 }
    )
    const labels = L.tileLayer(
      'https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}',
      { maxZoom: 19 }
    )
    const street = L.tileLayer(
      'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
      { attribution: '© OpenStreetMap contributors', maxZoom: 19 }
    )

    L.layerGroup([satellite, labels]).addTo(map)
    L.control.layers({ '🛰️ Satellite': L.layerGroup([satellite, labels]), '🗺️ Street': street }).addTo(map)

    map.on('click', (e) => {
      const { lat, lng } = e.latlng
      placeMarker(map, lat, lng, `${lat.toFixed(4)}, ${lng.toFixed(4)}`)
      // Read from the ref — always gets the current callback, never stale
      onLocationSelectRef.current?.({ lat, lng, name: `Lat: ${lat.toFixed(4)}, Lng: ${lng.toFixed(4)}` })
    })

    mapInstance.current = map
    setTimeout(() => map.invalidateSize(), 300)
  }, [])   // still runs once — the ref handles freshness

  // ── Sync externally selected location onto the map ────────────────────────
  useEffect(() => {
    if (!selectedLocation || !mapInstance.current) return
    const { lat, lng, name } = selectedLocation
    placeMarker(mapInstance.current, lat, lng, name ?? `${lat.toFixed(4)}, ${lng.toFixed(4)}`)
    mapInstance.current.setView([lat, lng], 10)
  }, [selectedLocation])

  function placeMarker(map, lat, lng, label) {
    if (markerRef.current) map.removeLayer(markerRef.current)
    markerRef.current = L.marker([lat, lng])
      .addTo(map)
      .bindPopup(label)
      .openPopup()
  }

  return <div ref={mapRef} id="map" />
}