*** Settings ***
Library  ../Config/util.py
Library     ExcelLibrary
Resource  ../Resources/Rpp_event_Keyword.robot
*** Variables ***


*** Test Cases ***
TestOfferingEventWholesale
    ${work_order_number}=   Create wholesale wo by TDM
    Sleep   60s
    ${response}=  Pull Data From Dynamo Db    {'table_name': 'rpp-recon-work-order', 'partition_key_index': 'index_work_order_number', 'partition_key': 'work_order_number', 'partition_key_value': '${work_order_number}', 'sort_key': 'sk', 'sort_key_value': 'consignment'}
    ${work_order_key}=  Extract Work Order Key    ${response}
    Sleep   30s
    ${response}=  Look For Offering Event In Order Offering Table    ${work_order_key}
    Validate offering event in rpp-order-offering       ${response}
    ${response}=  Look For Event With WO Number In Dynamodb Table   rpp-recon-work-order    ${work_order_number}    offering
    Should Contain	${response}     Items
    Validate offering event in rpp-recon-work-order     ${response}



