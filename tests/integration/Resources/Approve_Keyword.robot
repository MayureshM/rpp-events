*** Settings ***
Library  SeleniumLibrary
Variables  ../PageObjects/common_elements.py
Variables  ../PageObjects/approve.py
Resource  ../Config/common.robot


*** Keywords ***
Complete Approve Stage
    click on  ${select_approve}
    sleep  6
    Select Frame   ${stage_frame}
    wait element    ${button_ApproveAll}
    click on    ${button_ApproveAll}

    click on    ${ok_button}
    sleep   1
    click on    ${complete_button}
    click on    ${ok_button}
    unselect frame
    log to console  Completed Approve stage

Select Complete from Approve Stage
    click on  ${select_approve}
    sleep  4
    Select Frame   ${stage_frame}
    click on    ${complete_button}
    click on    ${ok_button}
    unselect frame
    log to console  Completed Approve stage

Verify Approve Stage
    click on   ${select_approve}
    sleep  4
    Select Frame   ${stage_frame}

CompleteApproveStageWithApprovedsandDeclinedWork
    Wait Until Element Is Visible   ${select_Approve}     timeout=10s
    Click Element  ${select_Approve}
    sleep  2
    Select Frame   ${mi_frame}
    Wait Until Element Is Visible   ${button_Decline_Labor}   timeout=30s
    Click Element   ${button_ApproveAll}
    Wait Until Element Is Visible  ${button_ApproveALl_OK}     timeout=10s
    click Element   ${button_ApproveALl_OK}
    Wait Until Element Is Visible   ${button_Decline_Labor}    timeout=10s
    click Element   ${button_Decline_Labor}
    Sleep  1
    click Element   ${button_Complete_ApproveStage}
    Wait Until Element Is Visible  ${div_Success_Approval}    timeout=20s
    click Element   ${button_ApproveALl_OK}
    Unselect Frame
    Wait Until Element Is Visible   ${select_Parts}


LoopBack From Approve To Estimate
    wait element   ${select_Approve}
    click on  ${select_Approve}
    sleep  2
    Select Frame   ${mi_frame}
    wait element  ${button_ReEstimate}
    click on   ${button_ReEstimate}
    Unselect Frame
    wait element   ${select_Estimate}

Validate Repair Process Order with Damages and Parts
    Log to console   "Repair Process Order  started"
    get repairprocessorder status from rpp-auto-integrate table
    IF  '${wo_po_status}'=='Authorized'
       RELOAD PAGE
       Verify Workorder is in Parts/Repair Stage
    ELSE
       Navigate Back to IP
    END


Validate Repair Process Order with no Damages
    Log to console   "Repair Process Order  started"
    get repairprocessorder status from rpp-auto-integrate table
    IF  '${wo_po_status}'=='Authorized'
        RELOAD PAGE
        CompleteRepairstage with no Damage
        Complete Quality Control Stage
        Complete Audit Stage AI
        CompleteDeliveryStage
    ELSE
        Navigate Back to IP
    END

Validate Repair Process Order For AutoApproval
    Log to console   "Repair Process Order  started"
    get repairprocessorder status from rpp-auto-integrate table
    IF  '${wo_po_status}'=='Authorized'
        RELOAD PAGE
        Verify Approve Stage
    END
Validate Repair Process Order For AwaitingFM
    Log to console   "Repair Process Order  started"
    get repairprocessorder status from rpp-auto-integrate table
    IF  '${wo_po_status}'=='AwaitingFM'
        RELOAD PAGE
        Verify Approve Stage
   END

Validate Repair Process Order For NotAuthorized
    Log to console   "Repair Process Order  started"
    get repairprocessorder status from rpp-auto-integrate table
    IF  '${wo_po_status}'=='NotAuthorized'
        RELOAD PAGE
        Verify Approve Stage
    END

Validate Repair Process Order For PartialAuthorization
    Log to console   "Repair Process Order  started"
    get repairprocessorder status from rpp-auto-integrate table
    IF  '${wo_po_status}'=='PartialAuthorization'
        RELOAD PAGE
        Verify Approve Stage
    END


Reject Fron Approve Stage
    sleep   5
    wait element    ${select_Reject}
    click on    ${select_Reject}
    wait element   ${reject_reason_dialog}
    click on   ${reject_reason_dropdown}
    ${reject_reason}=    get excel value    ${DATA.EXCEL_US734800RP}      75
    ${reject_reason_type}=  create element by text     ${reject_reason}
    click on    ${reject_reason_type}
    click on   ${reject_ok}

