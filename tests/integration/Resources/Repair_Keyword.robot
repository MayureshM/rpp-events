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
Variables  ../PageObjects/common_elements.py
Resource  ../Config/common.robot




*** Variables ***

*** Keywords ***

CompleteRepairstage
    wait element   ${select_Repair}
    click on  ${select_Repair}
    sleep  2
    Select Frame   ${stage_frame}
    wait element   ${span_Fees}
    click on   ${span_Fees}
    wait element  ${button_Work_Complete}
    click on   ${button_Work_Complete}
    wait element  ${button_WorkCredit}
    click on   ${button_WorkCredit}
    wait element  ${button_OK}
    click on   ${button_OK}
#    wait element  ${button_Work_Complete}
#    click on   ${button_Work_Complete}
#    wait element  ${button_WorkCredit}
#    click on   ${button_WorkCredit}
#    wait element  ${button_OK}
#    click on   ${button_OK}
    click on   ${button_Back}
    click on   ${span_MECH_SHOP}
    wait element  ${button_Work_Complete}
    click on   ${button_Work_Complete}
#    wait element  ${button_WorkCredit}
#    click on   ${button_WorkCredit}
#    wait element  ${button_OK}
#    click on   ${button_OK}
    click on   ${button_Back}
#    click on   ${span_MECH_SUBLET_SHOP}
#    wait element  ${button_Work_Complete}
#    click on   ${button_Work_Complete}
#    wait element  ${button_WorkCredit}
#    click on   ${button_WorkCredit}
#    wait element  ${button_OK}
#    click on   ${button_OK}
#    click on   ${button_Back}
    click on   ${span_PARTS_SHOP}
    wait element  ${button_Work_Complete}
    click on   ${button_Work_Complete}
    wait element  ${button_WorkCredit}
    click on   ${button_WorkCredit}
    wait element  ${button_OK}
    click on   ${button_OK}
    click on   ${button_Back}
    wait element   ${button_CompleteRepairStage}
    sleep   2
    click on   ${button_CompleteRepairStage}
    Unselect Frame

CompleteRepairstage with no Damage
    wait element   ${select_Repair}
    click on  ${select_Repair}
    sleep  2
    Select Frame   ${stage_frame}
    wait element   ${span_Fees}
    click on   ${span_Fees}
    wait element  ${button_Work_Complete}
    click on   ${button_Work_Complete}
    wait element  ${button_WorkCredit}
    click on   ${button_WorkCredit}
    wait element  ${button_OK}
    click on   ${button_OK}
    click on   ${button_Back}
    reload page
    wait element   ${button_CompleteRepairStage}
    sleep   4
    click on   ${button_CompleteRepairStage}
    Unselect Frame

Complete Repairs Without Clicking Complete Button in Repair Stage
    wait element   ${select_Repair}
    click on  ${select_Repair}
    sleep  2
    Select Frame   ${stage_frame}
    wait element   ${span_Fees}
    click on   ${span_Fees}
    wait element  ${button_Work_Complete}
    click on   ${button_Work_Complete}
    wait element  ${button_WorkCredit}
    click on   ${button_WorkCredit}
    wait element  ${button_OK}
    click on   ${button_OK}
    wait element  ${button_Work_Complete}
    click on   ${button_Work_Complete}
    wait element  ${button_WorkCredit}
    click on   ${button_WorkCredit}
    wait element  ${button_OK}
    click on   ${button_OK}
    click on   ${button_Back}
    click on   ${span_MECH_SHOP}
    wait element  ${button_Work_Complete}
    click on   ${button_Work_Complete}
   # wait element  ${button_WorkCredit}
   # click on   ${button_WorkCredit}
    wait element  ${button_Work_Complete}
    click on   ${button_Work_Complete}
    click on   ${button_Back}
    click on   ${span_MECH_SUBLET_SHOP}
    wait element  ${button_Work_Complete}
    click on   ${button_Work_Complete}
    wait element  ${button_WorkCredit}
    click on   ${button_WorkCredit}
    wait element  ${button_OK}
    click on   ${button_OK}
    click on   ${button_Back}
    click on   ${span_PARTS_SHOP}
    wait element  ${button_Work_Complete}
    click on   ${button_Work_Complete}
    wait element  ${button_WorkCredit}
    click on   ${button_WorkCredit}
    wait element  ${button_OK}
    click on   ${button_OK}
    click on   ${button_Back}


LoopBack To MechanicalInspection from Repair Stage
    wait element   ${select_Repair}
    Click Element  ${select_Repair}
    sleep  2
    Select Frame   ${mi_frame}
    wait element  ${LoopBack_AddObservations}
    click on   ${LoopBack_AddObservations}
    wait element   ${div_Test_drive}
    Unselect Frame

Complete Repair for additional Fee added with loopback from Repair Stage
    wait element   ${select_Repair}
    click on  ${select_Repair}
    sleep  2
    Select Frame   ${stage_frame}
    wait element   ${span_Fees}
    click on   ${span_Fees}
    wait element  ${button_Work_Complete}
    click on   ${button_Work_Complete}
    wait element  ${button_WorkCredit}
    click on   ${button_WorkCredit}
    wait element  ${button_OK}
    click on   ${button_OK}
    click on   ${button_Back}
    sleep   2
    click on   ${button_CompleteRepairStage}
    Unselect Frame

