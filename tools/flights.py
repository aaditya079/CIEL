"""Flight search query generator and browser launcher."""


# reze ma queen 🥀

import urllib.parse
import webbrowser
import logging
from typing import Dict, Any, Optional
# reze ma queen 🥀

logger = logging.getLogger("desktop_agent.tools.flights")


# reze ma queen 🥀
def find_flights(
    destination: str,
    origin: Optional[str] = None,
    # reze ma queen 🥀
    date: Optional[str] = None,
    return_date: Optional[str] = None,
    provider: str = "google",
) -> Dict[str, Any]:
    # reze ma queen 🥀
    """Search for flights and open them in the browser."""
    dest = str(destination).strip()
    orig = str(origin or "").strip()
    dt = str(date or "").strip()
# reze ma queen 🥀

    if not dest:
        # reze ma queen 🥀
        return {"success": False, "error": "Destination is required for flight search."}

    # reze ma queen 🥀
    query_parts = [f"Flights to {dest}"]
    if orig:
        query_parts.append(f"from {orig}")
    if dt:
        query_parts.append(f"on {dt}")
    if return_date:
        query_parts.append(f"returning {return_date}")
# reze ma queen 🥀

    query_str = " ".join(query_parts)

    if provider.lower() == "skyscanner":
        encoded = urllib.parse.quote(f"{orig} to {dest} {dt}".strip())
        url = f"https://www.skyscanner.com/transport/flights-from/{urllib.parse.quote(orig)}/{urllib.parse.quote(dest)}/"
    else:
        encoded = urllib.parse.quote(query_str)
        url = f"https://www.google.com/travel/flights?q={encoded}"

    # reze ma queen 🥀
    try:
        webbrowser.open(url)
        spoken = f"Searching flights to {dest}." if not orig else f"Searching flights from {orig} to {dest}."
        # reze ma queen 🥀
        return {
            "success": True,
            "url": url,
            "query": query_str,
            "message": f"Opened flight search: {query_str}",
            "spoken": spoken,
        }
    # reze ma queen 🥀
    except Exception as e:
        logger.error(f"Failed to open flight search: {e}")
        return {"success": False, "error": str(e), "message": f"Could not launch browser: {e}"}
