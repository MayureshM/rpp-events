*** Settings ***
Library  SeleniumLibrary
Variables  ../PageObjects/login.py
Variables  ../PageObjects/worklog.py
Variables  ../PageObjects/admin.py
Variables  ../PageObjects/mechanical_inspection.py
Variables  ../PageObjects/estimate.py
Variables  ../PageObjects/parts_estimate.py
Variables  ../PageObjects/approve.py
Variables  ../PageObjects/parts.py
Variables  ../PageObjects/repair.py
Variables  ../PageObjects/quality_control.py
Variables  ../PageObjects/audit.py
Resource  ../Config/common.robot


*** Variables ***

*** Keywords ***

Verify Quality Control Stage
    click on  ${select_quality_control}
    sleep  5
    Select Frame   ${stage_frame}
    unselect frame
Verify Quality Control Stage Without Completing the QC
    click on  ${select_quality_control}
    sleep  2
    sleep   2
    Select Frame   ${stage_frame}
    sleep   10
    click on    ${work_completed_ribbon}
    click on    ${pass_all}
    click on    ${back_button}
    click on    ${final_question}
    click on    ${emissions_passed}
    click on    ${perform_a_full_firmware_update}
    click on    ${state_safety_inspection_passed}
    click on    ${vehicle_qualifies_as_certified}
    click on    ${back_button}
    sleep   5

Verify loopback to Repair from Quality Control stage
    sleep   3
    click on    ${return_to_repair}
    sleep   3
    click on    ${complete_button}
    click on    ${select_quality_control}


Complete Quality Control Stage
    click on  ${select_quality_control}
    sleep  2
    sleep   2
    Select Frame   ${stage_frame}
    sleep   10
    click on    ${work_completed_ribbon}
    click on    ${pass_all}
    click on    ${back_button}
    click on    ${final_question}
    click on    ${emissions_passed}
    click on    ${perform_a_full_firmware_update}
    click on    ${state_safety_inspection_passed}
    click on    ${vehicle_qualifies_as_certified}
    click on    ${back_button}
    sleep   5
    click on    ${complete_qc}
    unselect frame
    log to console   Completed Quality Control stage
Verify loopback to Mechanical Inspection from Quality Control Stage
    wait element   ${LoopBack_AddObservations}
    click on   ${LoopBack_AddObservations}


Complete Quality Control Stage After Loopback
    click on  ${select_quality_control}
    sleep  2
    sleep   2
    Select Frame   ${stage_frame}
    sleep   10
    click on    ${work_completed_ribbon}
    click on    ${pass_all}
    click on    ${back_button}
    sleep   5
    click on    ${complete_qc}
    unselect frame


