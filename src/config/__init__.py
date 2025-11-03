from app_config import App_Config
from dynamodb import DynamoDB
from parameter_store import Parameter_Store
from secret_manager import Secret_Manager

from util import LOGGER


class Config:
    def __init__(self, data_provider="App_Config"):
        class_map = {
            "App_Config": App_Config,
            "Secret_Manager": Secret_Manager,
            "DynamoDB": DynamoDB,
            "Parameter_Store": Parameter_Store,
        }

        try:
            self.provider = class_map[data_provider]
        except KeyError as e:
            error_message = "Unknown data provider. Valid types are: "
            for key in class_map.keys():
                error_message += " " + key
            LOGGER.exception({"message": error_message, "error": e})

    def get(self):
        return self.provider.get()
