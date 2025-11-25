# RegioJet Delays API

Real-time bus/train delay monitoring for RegioJet public transportation in Czech Republic.

**Live Demo:** [https://ptomes1987.github.io/regiojet-delays/regiojet_demo.html](https://ptomes1987.github.io/regiojet-delays/regiojet_demo.html)

## What is this?

A reverse-engineered API wrapper for RegioJet's real-time departure/arrival data. Works from Termux on Android!

## Features

- Real-time delays for any RegioJet station
- Works on Termux (Android)
- Python API wrapper
- Bash script for quick checks
- HTML demo page

## Quick Start

### Bash (one-liner)
```bash
curl -s "https://brn-ybus-pubapi.sa.cz/restapi/routes/17902024/departures?limit=5" | python3 -c "import sys,json; [print(f'{b[\"number\"]}: {b.get(\"delay\",0)} min') for b in json.load(sys.stdin)]"
```

### Python
```python
from regiojet_api import RegioJetAPI

api = RegioJetAPI()
delays = api.get_departures_from('KARLOVY_VARY_TERMINAL')
for bus in delays:
    print(f"Bus {bus['number']}: {bus.get('delay', 0)} min delay")
```

### Bash script
```bash
./regiojet_delays_WORKING.sh
```

## API Endpoints

Base URL: `https://brn-ybus-pubapi.sa.cz/restapi`

| Endpoint | Description |
|----------|-------------|
| `/routes/{stationId}/departures` | Get departures |
| `/routes/{stationId}/arrivals` | Get arrivals |

### Station IDs

| Station | ID |
|---------|-----|
| Karlovy Vary Terminal | 17902024 |
| Karlovy Vary Tržnice | 17902023 |
| Sokolov Terminal | 721181001 |
| Praha Florenc | 10204003 |
| Cheb | 721181002 |

## How it was made

Reverse-engineered using Claude Code + Gemini CLI on Termux (Android Pixel 8 Pro).

The challenge: Find the hidden API that powers RegioJet's real-time delay display.

Solution:
1. Analyzed RegioJet website JS bundles
2. Found obfuscated API endpoints
3. Decoded station IDs from webpack chunks
4. Built working Python/Bash wrappers

## Files

- `regiojet_api.py` - Full Python API wrapper
- `regiojet_delays_WORKING.sh` - Simple bash script
- `regiojet_demo.html` - Interactive HTML demo

## Author

Created by Petr Tomeš using Claude Code (Opus 4.5) + Gemini 3 Pro Preview

## License

MIT
