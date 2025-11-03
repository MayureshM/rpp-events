from common_elements import get_element_by_text
import json

def get_tire_description(json_data):
    data = json.load(json_data)
    descriptions = []
    for x in data['approvedWork']:
        if 'Test Tire' in x['description']:
            descriptions.append(x['description'])
    return descriptions

select_delivery = "xpath://a[contains(text(),'Delivery')]"
finalize = "xpath://span[contains(text(),'Finalize')]"
api = "xpath:" + get_element_by_text('See Request/Response')

json_data = "xpath:(//*[@class='json-data'])[1]"


select_Delivery = "xpath://a[contains(text(),'Delivery')]"
button_CompleteDeliveryStage = "xpath://span[contains(text(),'Finalize')]"
