*** Settings ***
Library  ../Config/util.py
Library     ExcelLibrary
Resource  ../Resources/Rpp_event_Keyword.robot

*** Variables ***

*** Test Cases ***
TestCaptureEvent
    ${work_order_number}=   Create wo CaptureOnly by TDM
    ${response}=  Pull Data From Dynamo Db    {'table_name': 'rpp-recon-work-order', 'partition_key_index': 'index_work_order_number', 'partition_key': 'work_order_number', 'partition_key_value': '${work_order_number}', 'sort_key': 'sk', 'sort_key_value': 'consignment'}
    ${work_order_key}=  Extract Work Order Key    ${response}
    Sleep   30s
    ${response}=  Look For Capture Event In Order Capture Table    ${work_order_key}
    Validate capture event in rpp-order-capture     ${response}
    ${response}=  Look For Event With WO Number In Dynamodb Table   rpp-recon-work-order    ${work_order_number}    capture
    Should Contain	${response}     Items
    Validate capture event in rpp-recon-work-order      ${response}
