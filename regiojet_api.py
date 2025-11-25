#!/usr/bin/env python3
"""
RegioJet Bus/Train API Wrapper
Professional Python library for accessing RegioJet public transportation API

Author: Generated for RegioJet Delay Monitoring
Version: 1.0.0
"""

import json
import sys
from datetime import datetime
from typing import List, Dict, Optional, Any
import urllib.request
import urllib.error


class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    RESET = '\033[0m'


class RegioJetAPI:
    """
    Main API wrapper class for RegioJet public transportation API

    Base URL: https://brn-ybus-pubapi.sa.cz/restapi
    """

    BASE_URL = "https://brn-ybus-pubapi.sa.cz/restapi"

    # Common station IDs
    STATIONS = {
        'KARLOVY_VARY_TERMINAL': 17902024,
        'KARLOVY_VARY_TRZNICE': 17902023,
        'SOKOLOV_TERMINAL': 721181001,
        'SOKOLOV_TESOVICE': 721181000,
        'PRAHA_FLORENC': 10204003,
        'CHEB': 721181002,
    }

    def __init__(self, language: str = 'cs'):
        """
        Initialize RegioJet API client

        Args:
            language: Language code (cs, en, de, etc.)
        """
        self.language = language
        self.headers = {
            'Accept': 'application/json',
            'X-Lang': self.language,
            'User-Agent': 'RegioJetAPI/1.0'
        }

    def _make_request(self, endpoint: str) -> Any:
        """
        Make HTTP GET request to API

        Args:
            endpoint: API endpoint (without base URL)

        Returns:
            Parsed JSON response

        Raises:
            urllib.error.HTTPError: On HTTP errors
            json.JSONDecodeError: On invalid JSON response
        """
        url = f"{self.BASE_URL}{endpoint}"

        try:
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                data = response.read().decode('utf-8')
                return json.loads(data)
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            print(f"{Colors.RED}HTTP Error {e.code}: {e.reason}{Colors.RESET}")
            print(f"Response: {error_body}")
            raise
        except urllib.error.URLError as e:
            print(f"{Colors.RED}URL Error: {e.reason}{Colors.RESET}")
            raise
        except json.JSONDecodeError as e:
            print(f"{Colors.RED}JSON Decode Error: {e}{Colors.RESET}")
            raise

    def get_arrivals(self, station_id: int, limit: int = 20) -> List[Dict]:
        """
        Get arriving buses/trains at a station

        Args:
            station_id: Station ID
            limit: Maximum number of results (default: 20)

        Returns:
            List of arrival dictionaries
        """
        endpoint = f"/routes/{station_id}/arrivals?limit={limit}"
        return self._make_request(endpoint)

    def get_departures(self, station_id: int, limit: int = 20) -> List[Dict]:
        """
        Get departing buses/trains from a station

        Args:
            station_id: Station ID
            limit: Maximum number of results (default: 20)

        Returns:
            List of departure dictionaries
        """
        endpoint = f"/routes/{station_id}/departures?limit={limit}"
        return self._make_request(endpoint)

    def get_all_locations(self) -> List[Dict]:
        """
        Get all available locations (countries, cities, stations)

        Returns:
            List of location dictionaries with hierarchical structure
        """
        endpoint = "/consts/locations"
        return self._make_request(endpoint)

    def find_station(self, search_term: str) -> List[Dict]:
        """
        Search for stations by name

        Args:
            search_term: Station or city name to search for

        Returns:
            List of matching stations with their IDs
        """
        locations = self.get_all_locations()
        results = []

        search_lower = search_term.lower()

        for country in locations:
            for city in country.get('cities', []):
                if search_lower in city['name'].lower():
                    for station in city.get('stations', []):
                        results.append({
                            'city': city['name'],
                            'city_id': city['id'],
                            'station': station['name'],
                            'station_id': station['id'],
                            'fullname': station.get('fullname', ''),
                            'address': station.get('address', 'N/A'),
                        })
                else:
                    for station in city.get('stations', []):
                        if search_lower in station['name'].lower() or \
                           search_lower in station.get('fullname', '').lower():
                            results.append({
                                'city': city['name'],
                                'city_id': city['id'],
                                'station': station['name'],
                                'station_id': station['id'],
                                'fullname': station.get('fullname', ''),
                                'address': station.get('address', 'N/A'),
                            })

        return results

    def find_route(self, from_station_id: int, to_station_id: int,
                   limit: int = 50) -> List[Dict]:
        """
        Find routes between two stations

        Args:
            from_station_id: Departure station ID
            to_station_id: Arrival station ID
            limit: Maximum departures to check (default: 50)

        Returns:
            List of matching routes with connection details
        """
        departures = self.get_departures(from_station_id, limit=limit)
        routes = []

        for route in departures:
            stations = route.get('connectionStations', [])
            station_ids = [s['stationId'] for s in stations]

            if to_station_id in station_ids:
                # Find departure and arrival times
                departure_time = None
                arrival_time = None
                departure_platform = None
                arrival_platform = None

                for station in stations:
                    if station['stationId'] == from_station_id:
                        departure_time = station.get('departure')
                        departure_platform = station.get('platform')
                    if station['stationId'] == to_station_id:
                        arrival_time = station.get('arrival')
                        arrival_platform = station.get('platform')

                routes.append({
                    'number': route.get('number'),
                    'label': route.get('label'),
                    'delay': route.get('delay', 0),
                    'free_seats': route.get('freeSeatsCount', 0),
                    'departure_time': departure_time,
                    'arrival_time': arrival_time,
                    'departure_platform': departure_platform,
                    'arrival_platform': arrival_platform,
                    'vehicle_standard': route.get('vehicleStandard'),
                    'all_stations': stations,
                })

        return routes

    def check_delays(self, from_station_id: int, to_station_id: int,
                     threshold: int = 0) -> List[Dict]:
        """
        Check for delays on routes between two stations

        Args:
            from_station_id: Departure station ID
            to_station_id: Arrival station ID
            threshold: Only show delays >= this value in minutes (default: 0)

        Returns:
            List of routes with delays >= threshold
        """
        routes = self.find_route(from_station_id, to_station_id)

        if threshold > 0:
            return [r for r in routes if r['delay'] >= threshold]

        return routes

    @staticmethod
    def _format_datetime(dt_str: Optional[str]) -> str:
        """Format ISO datetime string to readable format"""
        if not dt_str:
            return "N/A"
        try:
            dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
            return dt.strftime("%H:%M")
        except:
            return dt_str

    @staticmethod
    def _format_delay(delay: int) -> str:
        """Format delay with color coding"""
        if delay == 0:
            return f"{Colors.GREEN}ON TIME{Colors.RESET}"
        elif delay < 10:
            return f"{Colors.YELLOW}+{delay} min{Colors.RESET}"
        else:
            return f"{Colors.RED}+{delay} min{Colors.RESET}"

    def print_routes(self, routes: List[Dict], show_details: bool = True):
        """
        Pretty print route information with colors

        Args:
            routes: List of route dictionaries
            show_details: Show detailed information (default: True)
        """
        if not routes:
            print(f"{Colors.YELLOW}No routes found.{Colors.RESET}")
            return

        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.RESET}")
        print(f"{Colors.BOLD}Found {len(routes)} route(s){Colors.RESET}")
        print(f"{Colors.CYAN}{'='*80}{Colors.RESET}\n")

        for i, route in enumerate(routes, 1):
            # Header
            print(f"{Colors.BOLD}{Colors.BLUE}[{i}] Bus/Train {route.get('number', 'N/A')}{Colors.RESET}")
            print(f"    {Colors.WHITE}{route.get('label', 'N/A')}{Colors.RESET}")

            # Delay status
            delay = route.get('delay', 0)
            delay_str = self._format_delay(delay)
            print(f"    Status: {delay_str}")

            # Times
            dep_time = self._format_datetime(route.get('departure_time'))
            arr_time = self._format_datetime(route.get('arrival_time'))
            print(f"    Departure: {Colors.GREEN}{dep_time}{Colors.RESET}", end="")
            if route.get('departure_platform'):
                print(f" (Platform {route['departure_platform']})", end="")
            print()
            print(f"    Arrival: {Colors.GREEN}{arr_time}{Colors.RESET}", end="")
            if route.get('arrival_platform'):
                print(f" (Platform {route['arrival_platform']})", end="")
            print()

            # Additional info
            if show_details:
                print(f"    Free seats: {route.get('free_seats', 0)}")
                if route.get('vehicle_standard'):
                    print(f"    Vehicle: {route['vehicle_standard']}")

            print()

    def print_delays_summary(self, routes: List[Dict]):
        """
        Print a summary of delays

        Args:
            routes: List of route dictionaries
        """
        if not routes:
            print(f"{Colors.YELLOW}No routes found.{Colors.RESET}")
            return

        total = len(routes)
        on_time = sum(1 for r in routes if r['delay'] == 0)
        delayed = total - on_time
        avg_delay = sum(r['delay'] for r in routes) / total if total > 0 else 0
        max_delay = max(r['delay'] for r in routes) if routes else 0

        print(f"\n{Colors.BOLD}{Colors.CYAN}=== DELAY SUMMARY ==={Colors.RESET}")
        print(f"Total routes: {total}")
        print(f"On time: {Colors.GREEN}{on_time}{Colors.RESET}")
        print(f"Delayed: {Colors.RED}{delayed}{Colors.RESET}")
        print(f"Average delay: {Colors.YELLOW}{avg_delay:.1f} minutes{Colors.RESET}")
        print(f"Maximum delay: {Colors.RED}{max_delay} minutes{Colors.RESET}")
        print()


def main():
    """Example usage and CLI interface"""
    api = RegioJetAPI()

    print(f"{Colors.BOLD}{Colors.MAGENTA}")
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║        RegioJet API - Karlovy Vary → Sokolov Route       ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}\n")

    # Check Karlovy Vary → Sokolov route
    from_station = api.STATIONS['KARLOVY_VARY_TERMINAL']
    to_station = api.STATIONS['SOKOLOV_TERMINAL']

    print(f"{Colors.BOLD}Checking route: Karlovy Vary Terminal → Sokolov Terminal{Colors.RESET}")
    print(f"Station IDs: {from_station} → {to_station}\n")

    try:
        routes = api.find_route(from_station, to_station, limit=50)
        api.print_routes(routes)
        api.print_delays_summary(routes)

        # Show routes with significant delays
        delayed_routes = [r for r in routes if r['delay'] >= 10]
        if delayed_routes:
            print(f"{Colors.BOLD}{Colors.RED}⚠ SIGNIFICANT DELAYS (≥10 min):{Colors.RESET}")
            api.print_routes(delayed_routes, show_details=False)

    except Exception as e:
        print(f"{Colors.RED}Error: {e}{Colors.RESET}")
        sys.exit(1)


if __name__ == "__main__":
    main()
