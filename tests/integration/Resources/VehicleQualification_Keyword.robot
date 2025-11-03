*** Settings ***
Library  SeleniumLibrary
Variables  ../PageObjects/common_elements.py
Variables  ../PageObjects/vehicle_qualification.py
Resource  ../Config/env_var.robot
Resource  ../Config/common.robot
Resource  ../Resources/MechanicalInspection_Keyword.robot
Resource  ../Resources/Diagnose_Keyword.robot



*** Variables ***
*** Keywords ***
Vehicle Inspection Stage
    wait element  ${select_vehicle_qualification}
    click on  ${select_vehicle_qualification}
    Sleep  5
    Select frame  ${iframe_vq}
    click on  ${initial_questions}
    click on  ${yes_button}
    click on  ${vq_top_link}
    click on  ${spn_vq_complete}
    sleep  5
    Unselect Frame
    sleep   5
Select Vehicle Qualification Stage
    Sleep   5
    wait element  ${select_vehicle_qualification}
    click on  ${select_vehicle_qualification}
    Sleep  5
    Select frame  ${iframe_vq}
    click on  ${initial_questions}
    click on  ${yes_button}
    click on  ${vq_top_link}

Complete Vehicle Qualification Stage
    click on  ${spn_vq_complete}
    sleep  5
    Unselect Frame
    sleep   5
Click on Vehicle Qualification Stage
    Sleep   5
    wait element  ${select_vehicle_qualification}
    click on  ${select_vehicle_qualification}
    Sleep  5
    Select frame  ${iframe_vq}

Adding Additional Fees In Vehicle Inspection Stage
    click on   ${Fees_ribbon}
    ${data_fee}=    get excel value    ${DATA.EXCEL_US734800RP}      8
    ${fee_type}=  create element by text   ${data_fee}
    click on  ${fee_type}${fee_checkbox}
    click on  ${vq_top_link}



Validate Vehicle API Without Damages
    get validate vehicleAPI status with excel data WO
    log to console   "validation started without damages"
    IF  '${wo_slu_exc}'=='SUCCESS'
        NavigatetoMI
        Verify Diagnose Task for AI
    ELSE IF  '${wo_slu_exc}'=='NO_VALUE'
        NavigatetoMI
        Verify Diagnose Task for Non-AI
    ELSE
        Verify Rejected message
    END



Validate Vehicle API With Damages
    get validate vehicleAPI status with excel data WO
    log to console   "validation started with Damages"
    IF  '${wo_slu_exc}'=='SUCCESS'
        Add Damages from Mechanical Inspection Stage
        Adding Damages
        Verify Diagnose Task for AI
    ELSE IF  '${wo_slu_exc}'=='NO_VALUE'
        Add Damages from Mechanical Inspection Stage
        Adding Damages
        Verify Diagnose Task for Non-AI
    ELSE
        Verify Rejected message
    END
Validate Vehicle API Status
    get validate vehicleAPI status with excel data WO
    log to console   "Fetched the Validation API Response Status"
    IF  '${wo_slu_exc}'=='SUCCESS'
        RELOAD PAGE
    ELSE IF  '${wo_slu_exc}'=='NO_VALUE'
        RELOAD PAGE
    ELSE
        RELOAD PAGE
    END
