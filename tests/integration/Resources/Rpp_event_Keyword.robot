*** Settings ***
Library  SeleniumLibrary
Library  ../Config/util.py
Library     ExcelLibrary
Resource  ../Config/env_var.robot

*** Variables ***

*** Keywords ***
Create wo CaptureOnly by TDM
    Open Excel Document    ${DATA.EXCEL_tdm_data}    doc_id=docid
    ${row_num}=     Switch Excel Row
    ${requested_by}=    Read Excel Cell     row_num=2	col_num=1
    ${auction_code}=    Read Excel Cell     ${row_num}     	col_num=2
    ${number_of_items}=     Read Excel Cell     row_num=2	col_num=3
    ${vehicle_status}=  Read Excel Cell     row_num=2	col_num=4
    ${seller_number}=   Read Excel Cell     row_num=2	col_num=5
    ${capture_and_condition}=   Read Excel Cell     row_num=4	col_num=6
    ${response}=  Submit Job Criteria To Tdm    https://manheimtestdata-internal.tdm.manheim.com//api/v3/inventory?requested_by=${requested_by}&auction_code=${auction_code}&number_of_items=${number_of_items}&vehicle_status=${vehicle_status}&seller_number=${seller_number}&capture_and_condition=${capture_and_condition}&initiate_build=true
    ${work_order_number}=  Extract Work Order Number    ${response}
    Close Current Excel Document
    [Return]  ${work_order_number}

Create wo L1withDamage by TDM
    Open Excel Document    ${DATA.EXCEL_tdm_data}    doc_id=docid
    ${row_num}=     Switch Excel Row
    ${requested_by}=    Read Excel Cell     row_num=2	col_num=1
    ${auction_code}=    Read Excel Cell     ${row_num}     	col_num=2
    ${number_of_items}=     Read Excel Cell     row_num=2	col_num=3
    ${vehicle_status}=  Read Excel Cell     row_num=2	col_num=4
    ${seller_number}=   Read Excel Cell     row_num=2	col_num=5
    ${capture_and_condition}=   Read Excel Cell     row_num=6	col_num=6
    ${response}=  Submit Job Criteria To Tdm    https://manheimtestdata-internal.tdm.manheim.com//api/v3/inventory?requested_by=${requested_by}&auction_code=${auction_code}&number_of_items=${number_of_items}&vehicle_status=${vehicle_status}&seller_number=${seller_number}&capture_and_condition=${capture_and_condition}&initiate_build=true
    ${work_order_number}=  Extract Work Order Number    ${response}
    Close Current Excel Document
    [Return]  ${work_order_number}

Create wholesale wo by TDM
    Open Excel Document    ${DATA.EXCEL_tdm_data}    doc_id=docid
    ${row_num}=     Switch Excel Row
    ${requested_by}=    Read Excel Cell     row_num=2	col_num=1
    ${auction_code}=    Read Excel Cell     ${row_num}     	col_num=2
    ${number_of_items}=     Read Excel Cell     row_num=2	col_num=3
    ${vehicle_status}=  Read Excel Cell     row_num=3	col_num=4
    ${seller_number}=   Read Excel Cell     row_num=3	col_num=5
    ${capture_and_condition}=   Read Excel Cell     row_num=4	col_num=6
    ${response}=  Submit Job Criteria To Tdm    https://manheimtestdata-internal.tdm.manheim.com//api/v3/inventory?requested_by=${requested_by}&auction_code=${auction_code}&number_of_items=${number_of_items}&vehicle_status=${vehicle_status}&seller_number=${seller_number}&capture_and_condition=${capture_and_condition}&initiate_build=true
    ${work_order_number}=  Extract Work Order Number    ${response}
    Close Current Excel Document
    [Return]  ${work_order_number}

Validate event in rpp-order-image
    [Arguments]    ${response}
    ${validate_data1}=   Extract Data From Response      ${response}     serviceCategoryStatus
    Should Match    ${validate_data1}   CAPT:CN
    ${validate_data2}=   Extract Data From Response      ${response}     status
    Should Match    ${validate_data2}   COMPLETED

Validate event in rpp-recon-vehicle
    [Arguments]    ${response}
    ${validate_data1}=   Extract Data From Recon Vehicle Response      ${response}     status
    Should Match    ${validate_data1}   COMPLETED
    ${validate_data2}=   Extract Data From Recon Vehicle Response      ${response}     type
    Should Match    ${validate_data2}   CAPT

Validate capture event in rpp-order-capture
    [Arguments]    ${response}
    ${validate_data1}=   Extract Data From Response      ${response}     status
    Should Match    ${validate_data1}   COMPLETED
    ${validate_data2}=   Extract Data From Response      ${response}     type
    Should Match    ${validate_data2}   CAPT

Validate capture event in rpp-recon-work-order
    [Arguments]    ${response}
    ${validate_data1}=   Extract Capture Type From Recon Work Order Response      ${response}     type
    Should Match    ${validate_data1}   CAPT
    ${validate_data2}=   Extract Capture Status From Recon Work Order Response      ${response}     capture_status
    Should Match    ${validate_data2}   COMPLETED

Validate condition event in rpp-order-condition
    [Arguments]    ${response}
    ${validate_data1}=   Extract Data From Response      ${response}     status
    Should Match    ${validate_data1}   COMPLETED
    ${validate_data2}=   Extract Data From Response      ${response}     type
    Should Match    ${validate_data2}   CR/SO

Validate condition event in rpp-recon-work-order
    [Arguments]    ${response}
    ${validate_data1}=   Extract Data From Recon Work Order Response      ${response}     status
    Should Match    ${validate_data1}   COMPLETED
    ${validate_data2}=   Extract Data From Recon Work Order Response      ${response}     type
    Should Match    ${validate_data2}   CR/SO

Validate offering event in rpp-order-offering
    [Arguments]    ${response}
    ${validate_data1}=   Extract Data From Response      ${response}     status
    Should Match    ${validate_data1}   ACTIVE

Validate offering event in rpp-recon-work-order
    [Arguments]    ${response}
    ${validate_data1}=   Extract Offering Type From Recon Work Order Response      ${response}     status
    Should Match    ${validate_data1}   ACTIVE

Validate retailrecon event in rpp-order-retailrecon
    [Arguments]    ${response}
    ${validate_active_task}=   Extract Active Task From RetailRecon Response      ${response}     activeTasks    type
    Should Match    ${validate_active_task}   Mechanical Inspection
    ${validate_complete_task1}=   Extract Complete Task 1 From RetailRecon Response      ${response}     completedTasks    taskName
    Should Match    ${validate_complete_task1}   Mechanical Inspection
    ${validate_complete_task2}=   Extract Complete Task 2 From RetailRecon Response      ${response}     completedTasks     taskName
    Should Match    ${validate_complete_task2}   Vehicle Qualification

Validate retailrecon event in rpp-order-retailrecon after completed Delivery stages
   [Arguments]    ${response}
   ${validate_complete_task}=  extract complete task from retailrecon response     ${response}     completedTasks    taskName
    Should Contain    ${validate_complete_task}     Vehicle Qualification
    Should Contain    ${validate_complete_task}     Mechanical Inspection
    Should Contain    ${validate_complete_task}     Diagnose
    Should Contain    ${validate_complete_task}     Estimate
    Should Contain    ${validate_complete_task}     Parts Estimate
    Should Contain    ${validate_complete_task}     Approve
    Should Contain    ${validate_complete_task}     Parts
    Should Contain    ${validate_complete_task}     Repair
    Should Contain    ${validate_complete_task}     Quality Control
    Should Contain    ${validate_complete_task}     Audit
    Should Contain    ${validate_complete_task}     Delivery