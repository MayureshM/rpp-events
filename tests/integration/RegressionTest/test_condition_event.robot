*** Settings ***
Library  ../Config/util.py
Library     ExcelLibrary
Resource  ../Resources/Rpp_event_Keyword.robot
*** Variables ***


*** Test Cases ***
TestImageEvent
    ${work_order_number}=   Create wo L1withDamage by TDM
    ${response}=  Pull Data From Dynamo Db    {'table_name': 'rpp-recon-work-order', 'partition_key_index': 'index_work_order_number', 'partition_key': 'work_order_number', 'partition_key_value': '${work_order_number}', 'sort_key': 'sk', 'sort_key_value': 'consignment'}
    ${work_order_key}=  Extract Work Order Key    ${response}
    Sleep   50s
    ${response}=  Look For Event With WO Key In Dynamodb Table     rpp-order-condition    ${work_order_key}    condition
    Validate condition event in rpp-order-condition     ${response}
    ${response}=  Look For Event With WO Number In Dynamodb Table   rpp-recon-work-order    ${work_order_number}  condition
    Should Contain	${response}	Items
    Validate condition event in rpp-recon-work-order        ${response}



