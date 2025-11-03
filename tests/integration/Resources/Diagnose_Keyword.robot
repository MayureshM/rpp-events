*** Settings ***
Library  SeleniumLibrary
Variables  ../PageObjects/common_elements.py
Variables  ../PageObjects/mechanical_inspection.py
Variables  ../PageObjects/estimate.py
Variables  ../PageObjects/diagnose.py
Resource  ../Config/common.robot
Resource  ../Resources/Estimate_Keyword.robot
Resource  ../Resources/Part_Estimate_Keyword.robot
Resource  ../Resources/Repair_Keyword.robot
Resource  ../Resources/Parts_Keyword.robot
*** Variables ***

*** Keywords ***
Verify Diagnose Task for AI
    #wait element    ${select_diagnose}
    ${diagnose_status} =    Run Keyword And Return Status     wait until element is visible    ${select_diagnose}
    log to console     ${diagnose_status}
    IF  '${diagnose_status}'=='True'
        Complete Diagnose
        Complete Estimate Stage
        Verify Parts Estimate Stage Is Available for AI
    ELSE
        Complete Estimate Stage
        Verify Parts Estimate Stage Is Available for AI
    END

Verify Diagnose Task for Non-AI
    #wait element    ${select_diagnose}
    ${diagnose_status} =    Run Keyword And Return Status     wait until element is visible    ${select_diagnose}
    log to console     ${diagnose_status}
    IF  '${diagnose_status}'=='True'
        Complete Diagnose
        Complete Estimate Stage
        Verify Parts Estimate Stage Is Available for Non-AI
    ELSE
        Complete Estimate Stage
        Verify Parts Estimate Stage Is Available for Non-AI
    END
Complete Diagnose
    click on    ${select_diagnose}
    sleep   5
    select frame   ${stage_frame}
    click on  ${complete_DiagnoseStage}
    unselect frame

Verify Diagnose Task
    #wait element    ${select_diagnose}
    ${diagnose_status} =    Run Keyword And Return Status     wait until element is visible    ${select_diagnose}
    log to console     ${diagnose_status}
    IF  '${diagnose_status}'=='True'
        Complete Diagnose
    ELSE
        Complete Estimate Stage
    END