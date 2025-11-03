*** Settings ***
Library  ../Config/util.py
Library     ExcelLibrary
Resource  ../Resources/Rpp_event_Keyword.robot
*** Variables ***
*** Test Cases ***
TestImageEvent
    ${work_order_number}=   Create wo CaptureOnly by TDM
    ${response}=  Pull Data From Dynamo Db    {'table_name': 'rpp-recon-work-order', 'partition_key_index': 'index_work_order_number', 'partition_key': 'work_order_number', 'partition_key_value': '${work_order_number}', 'sort_key': 'sk', 'sort_key_value': 'consignment'}
    ${work_order_key}=  Extract Work Order Key    ${response}
    Sleep   20s
    ${response}=  Look For Event With WO Key In Dynamodb Table     rpp-order-image    ${work_order_key}    image
    Should Contain	    ${response}	    Items
    Validate event in rpp-order-image     ${response}
    ${response}=  Look For Event With WO Number In Dynamodb Table   rpp-recon-vehicle    ${work_order_number}  capture
    Should Contain	${response}	Items
    Validate event in rpp-recon-vehicle     ${response}
    ${response}=  Look For Event With WO Number In Dynamodb Table   rpp-recon-vehicle    ${work_order_number}  image
    Should Contain	${response}	Items
