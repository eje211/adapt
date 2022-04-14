"""
Main script for the Adapt test.
"""

from rest import MockRestService


def run():
    """
    Produces the demo output for the application.
    """
    print('Scraping the data.')
    rest_service = MockRestService()
    print('Producing the JSON.\n\n')
    print(rest_service.respond())


if __name__ == '__main__':
    run()
