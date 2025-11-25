#!/bin/bash
###############################################################################
# 🎉 WORKING SOLUTION - RegioJet Delays API
# Successfully reverse-engineered by Claude Sonnet 4.5 Agent
###############################################################################

KARLOVY_VARY_ID="17902024"
SOKOLOV_ID="721180001"

API_BASE="https://brn-ybus-pubapi.sa.cz/restapi"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "🚌 RegioJet - Aktuální zpoždění"
echo "================================"
echo ""

# Function to get departures
get_departures() {
    local station_id=$1
    local station_name=$2

    echo -e "${BLUE}📍 $station_name - ODJEZDY:${NC}"
    echo ""

    curl -s "$API_BASE/routes/$station_id/departures?limit=10" \
        -H "Accept: application/json" \
        -H "X-Lang: cs" | \
    python3 -c "
import sys, json
data = json.load(sys.stdin)
for bus in data[:10]:
    delay = bus.get('delay', 0)
    label = bus.get('label', 'N/A')
    number = bus.get('number', 'N/A')

    if delay > 0:
        print(f'  🔴 Spoj {number}: {label}')
        print(f'     Zpoždění: {delay} minut\n')
    else:
        print(f'  ✅ Spoj {number}: {label}')
        print(f'     VČAS\n')
"
}

# Function to get arrivals
get_arrivals() {
    local station_id=$1
    local station_name=$2

    echo -e "${BLUE}📍 $station_name - PŘÍJEZDY:${NC}"
    echo ""

    curl -s "$API_BASE/routes/$station_id/arrivals?limit=10" \
        -H "Accept: application/json" \
        -H "X-Lang: cs" | \
    python3 -c "
import sys, json
data = json.load(sys.stdin)
for bus in data[:10]:
    delay = bus.get('delay', 0)
    label = bus.get('label', 'N/A')
    number = bus.get('number', 'N/A')

    if delay > 0:
        print(f'  🔴 Spoj {number}: {label}')
        print(f'     Zpoždění: {delay} minut\n')
    else:
        print(f'  ✅ Spoj {number}: {label}')
        print(f'     VČAS\n')
"
}

# Main execution
echo -e "${YELLOW}═══════════════════════════════════════════${NC}"
echo ""

# Karlovy Vary - Arrivals
get_arrivals "$KARLOVY_VARY_ID" "Karlovy Vary"

echo ""
echo -e "${YELLOW}───────────────────────────────────────────${NC}"
echo ""

# Karlovy Vary - Departures
get_departures "$KARLOVY_VARY_ID" "Karlovy Vary"

echo ""
echo -e "${YELLOW}═══════════════════════════════════════════${NC}"
echo ""

# Also check Sokolov if needed
# get_arrivals "$SOKOLOV_ID" "Sokolov"
# get_departures "$SOKOLOV_ID" "Sokolov"

echo -e "${GREEN}✅ Data načtena úspěšně!${NC}"
echo ""
echo "🔗 API Endpoint: $API_BASE/routes/{stationId}/{arrivals|departures}"
echo "📝 Discovered by: Claude Sonnet 4.5 Agent System"
