*** Settings ***
Library  SeleniumLibrary
Variables  ../PageObjects/common_elements.py
Variables  ../PageObjects/estimate.py
Resource  ../Config/common.robot
*** Variables ***
${Global_Timeout}  30s

*** Keywords ***
Complete Estimate Stage
    click on  ${select_Estimate}
    sleep  2
    Select Frame   ${stage_frame}
    sleep  2
    click on    ${complete_button}
    Unselect Frame
    log to console  Completed Estimate Stage

Update Repair Estimates in Estimate Stage
    wait element   ${select_Estimate}
    click on   ${select_Estimate}
    sleep  2
    Select Frame   ${mi_frame}
    click on  ${repair_estimate_ribbon}
    wait element   ${div_AirSuspension_Observation}
    click on   ${div_AirSuspension_Observation}
    wait element  ${span_UpdateLabor}
    click on   ${span_UpdateLabor}
    Sleep  5
    input value  ${labor_time}   1.0
    sleep  1
    click on   ${save_button}
    click on   ${button_Back_Estimate}
    click on   ${span_Complete_EstimateStage}
    Unselect Frame



