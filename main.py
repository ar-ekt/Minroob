from configparser import ConfigParser
from minroob_app import MinroobApp

if __name__ == "__main__":
    config = ConfigParser()
    config.read("config.ini")
    api_id = config["client_api"]["api_id"]
    api_hash = config["client_api"]["api_hash"]

    MinroobApp(api_id, api_hash).run()
