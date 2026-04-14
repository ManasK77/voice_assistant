# core/info_ops.py
"""
Information operations — time, date, weather, Wikipedia, web search.
"""

import datetime
import logging
import webbrowser

import requests

import config

logger = logging.getLogger("VoiceAssist.InfoOps")


def get_time() -> str:
    """Return the current time as a speakable string."""
    try:
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        return f"The current time is {current_time}"
    except Exception as e:
        logger.error(f"Unexpected error in get_time: {e}", exc_info=True)
        return "Sorry, I couldn't get the current time"


def get_date() -> str:
    """Return today's date as a speakable string."""
    try:
        current_date = datetime.datetime.now().strftime("%A, %d %B %Y")
        return f"Today is {current_date}"
    except Exception as e:
        logger.error(f"Unexpected error in get_date: {e}", exc_info=True)
        return "Sorry, I couldn't get today's date"


def get_weather(city: str = None) -> str:
    """Fetch weather from OpenWeatherMap API."""
    if city is None:
        city = config.DEFAULT_CITY

    if config.WEATHER_API_KEY == "YOUR_OPENWEATHERMAP_API_KEY":
        return "Weather service unavailable. Please set your API key in config.py"

    try:
        url = (
            f"http://api.openweathermap.org/data/2.5/weather"
            f"?q={city}&appid={config.WEATHER_API_KEY}&units=metric"
        )
        response = requests.get(url, timeout=10)
        data = response.json()

        if response.status_code != 200:
            logger.warning(f"Weather API error: {data}")
            return f"Could not get weather for {city}"

        temp = data["main"]["temp"]
        description = data["weather"][0]["description"]
        return f"The weather in {city} is {description} with a temperature of {temp}°C"

    except requests.RequestException as e:
        logger.warning(f"Weather network error: {e}")
        return "Weather service unavailable. Please check your internet connection"
    except Exception as e:
        logger.error(f"Unexpected error in get_weather: {e}", exc_info=True)
        return "Sorry, something went wrong with the weather service"


def wikipedia_summary(query: str) -> str:
    """Get a 2-sentence Wikipedia summary for the given query."""
    try:
        import wikipedia

        wikipedia.set_lang("en")
        result = wikipedia.summary(query, sentences=2)
        return result
    except Exception as e:
        # Handle disambiguation, page errors, and network errors
        error_type = type(e).__name__
        if "DisambiguationError" in error_type:
            try:
                import wikipedia

                options = e.options  # type: ignore
                if options:
                    result = wikipedia.summary(options[0], sentences=2)
                    return result
            except Exception:
                pass
            return f"Multiple results found for {query}. Please be more specific."
        elif "PageError" in error_type:
            return f"No Wikipedia page found for {query}"
        else:
            logger.error(f"Wikipedia error: {e}", exc_info=True)
            return f"Could not look up {query} on Wikipedia"


def web_search(query: str) -> str:
    """Open Google search in the default browser."""
    try:
        url = f"https://www.google.com/search?q={query}"
        webbrowser.open(url)
        return f"Done. Searching Google for {query} successfully."
    except Exception as e:
        logger.error(f"Web search error: {e}", exc_info=True)
        return "Sorry, I couldn't open the browser for searching"
