*** Settings ***
Library  SeleniumLibrary
Library  ExcelLibrary
Library    ../Config/util.py
Resource  ../Resources/Login_Keyword.robot
Resource  ../Resources/VehicleQualification_Keyword.robot
Resource  ../Resources/MechanicalInspection_Keyword.robot
Resource  ../Resources/Diagnose_Keyword.robot
Resource  ../Resources/Worklog_Keyword.robot
Resource  ../Resources/Estimate_Keyword.robot
Resource  ..//Resources/Approve_Keyword.robot
Resource  ../Resources/Repair_Keyword.robot
Resource  ../Resources/Audit_Keyword.robot
Resource  ../Resources/QualityControl_Keyword.robot
Resource  ../Resources/Delivery_Keyword.robot
Resource  ../Resources/Rpp_event_Keyword.robot

Test Setup   Login To RPP
Test Teardown   Logout of Browser
*** Variables ***
*** Test Cases ***


TestRetailReconEvent
    Select Location
    ${work_order_number}=   Create wo CaptureOnly by TDM
    ${response}=  Pull Data From Dynamo Db    {'table_name': 'rpp-recon-work-order', 'partition_key_index': 'index_work_order_number', 'partition_key': 'work_order_number', 'partition_key_value': '${work_order_number}', 'sort_key': 'sk', 'sort_key_value': 'consignment'}
    ${work_order_key}=  Extract Work Order Key    ${response}
    Sleep   180s
    Search Workorder    ${work_order_number}
    Select Vehicle Qualification Stage
    Complete Vehicle Qualification Stage
    ${response}=  Look For Event With WO Key In Dynamodb Table     rpp-order-retailrecon    ${work_order_key}    retail_recon
    Should Contain	${response}	Items
    Validate retailrecon event in rpp-order-retailrecon     ${response}
    ${response}=  Look For Event With WO Number In Dynamodb Table   rpp-recon-work-order    ${work_order_number}  active_task:mechanical_inspection
    Should Contain      ${response}     Items
    ${response}=  Look For Event With WO Number In Dynamodb Table   rpp-recon-work-order    ${work_order_number}  completed_task:vehicle_qualification
    Should Contain      ${response}     Items
    Select Mechanical Inspection Stage
    Adding Damages
    Complete Diagnose
    Complete Estimate Stage
    Add Part In Part Estimate Stage
    Complete Approve Stage
    Complete Part Stage
    CompleteRepairstage
    Complete Quality Control Stage
    Complete Audit Stage
    CompleteDeliveryStage
    Sleep   5s
    ${response}=  Look For Event With WO Key In Dynamodb Table     rpp-order-retailrecon    ${work_order_key}    retail_recon
    Should Contain      ${response}     Items
    Validate retailrecon event in rpp-order-retailrecon after completed Delivery stages      ${response}
    ${response}=  Look For Event With WO Number In Dynamodb Table   rpp-recon-work-order    ${work_order_number}  completed_task:delivery
    Should Contain      ${response}     Items