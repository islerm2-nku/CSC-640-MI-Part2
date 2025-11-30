## 1. Upload
```bash
curl -X 'POST' \
  'http://localhost/telemetry/upload' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer YOUR_OAUTH_TOKEN' \
  -H 'Content-Type: multipart/form-data' \
  -F 'telemetry_file=@formulair04_summit summit raceway 2025-11-18 18-14-42.ibt' \
  -F 'attributes=Lap,RPM,Speed,LapDistPct,FuelLevel,OnPitRoad,PlayerIncidents,RFpressure,LFpressure,RRpressure,LRpressure'
```

## 2. List Sessions
```bash
curl -X 'GET' \
  'http://localhost/sessions/' \
  -H 'accept: application/json'
```

## 3. 