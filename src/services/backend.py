from typing import Dict
import logging
import requests

logger = logging.getLogger(__name__)


def send_post_to_backend(url: str, payload: Dict[str, str]) -> None:
    """
    Sends a post to the backend for processing. 
    """
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        logger.error(f"Failed to send post to backend: {response.status_code}, {response.text}")
    else:
        logger.info(f"Post sent successfully to {url} with payload: {payload}")

def send_get_to_backend(url: str, payload: Dict[str, str]) -> Dict[str, str]:
    """
    Sends a GET request to the backend with the given payload.
    Args:
        url (str): The URL to send the GET request to.
        payload (Dict[str, str]): The payload to include in the GET request.
    Returns:    
        Dict[str, str]: The response from the backend as a dictionary.
    """ 
    response = requests.get(url, params=payload)
    if response.status_code != 200:
        logger.error(f"Failed to get response from backend: {response.status_code}, {response.text}")    
    else:
        logger.info(f"GET request sent successfully to {url} with payload: {payload}")
        return response.json()