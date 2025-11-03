*** Settings ***
Library  SeleniumLibrary
Variables  ../PageObjects/common_elements.py
Variables   ../PageObjects/parts_estimate.py
Resource  ../Config/common.robot
Resource  ../Resources/Repair_Keyword.robot
Resource  ../Resources/Parts_Keyword.robot
Resource  ../Resources/Audit_Keyword.robot
Resource  ../Resources/QualityControl_Keyword.robot
Resource  ../Resources/Delivery_Keyword.robot

*** Variables ***

*** Keywords ***
Verify Parts Estimate Stage Is Available for AI
    #wait element    ${select_part_estimate}
    ${parts_est_status} =   Run Keyword And Return Status    wait until element is visible    ${select_part_estimate}
    log to console     ${parts_est_status}
    IF   '${parts_est_status}'=='True'
       Add Part In Part Estimate Stage
       Validate Repair Process Order with Damages and Parts
    ELSE
       Validate Repair Process Order with Damages and Parts
    END

Verify Parts Estimate Stage Is Available for Non-AI
    #wait element    ${select_part_estimate}
    ${parts_est_status} =   Run Keyword And Return Status    wait until element is visible    ${select_part_estimate}
    log to console     ${parts_est_status}
    IF   '${parts_est_status}'=='True'
       Add Part In Part Estimate Stage
       Complete Approve Stage
       Complete Part Stage
       completerepairstage
       Complete Quality Control Stage
       Complete Audit Stage AI
       CompleteDeliveryStage
    ELSE
       Complete Approve Stage
       completerepairstage
       Complete Quality Control Stage
       Complete Audit Stage AI
       CompleteDeliveryStage
    END



Add Part In Part Estimate Stage
    click on    ${select_part_estimate}
    sleep  2
    Select Frame   ${stage_frame}
    click on    ${repair_estimate_ribbon}
    sleep   3
    ${part_list}    create list    55
    ${data_part_name_list}   create list    57
    ${data_part_source_list}   create list    59
    FOR   ${i}  IN RANGE  1
         FOR    ${part}  ${data_part_name}    ${data_part_source}   IN ZIP      ${part_list}   ${data_part_name_list}    ${data_part_source_list}
                 Add Part to Damage      ${part}  ${data_part_name}    ${data_part_source}
         END
    END
    click on    ${back_button}
    click on    ${complete_button}
    Unselect Frame


Add Part to Damage
    [Arguments]     ${part_row}   ${data_part_name_row}    ${data_part_source_row}
    ${data_part}=    get excel value    ${DATA.EXCEL_US734800RP}      ${part_row}
    ${part_estimates}=  create element by text   ${data_part}
    click on    ${part_estimates}
    click on    ${part_estimates}${add_part_icon}
    sleep   2
    ${data_part_name}=    get excel value   ${DATA.EXCEL_US734800RP}      ${data_part_name_row}
    ${partn}=   set variable  ${data_part_name}
    input value     ${part_name}    ${partn}
    click on    ${part_source}
    ${data_part_source}=    get excel value   ${DATA.EXCEL_US734800RP}       ${data_part_source_row}
    ${psource}=  create element by text   ${data_part_source}
    click on    ${psource}

    ${pnum}=    get excel value   ${DATA.EXCEL_US734800RP}       61
    input value     ${part_num}     ${pnum}
    ${pquantity}=    get excel value   ${DATA.EXCEL_US734800RP}       63
    input value     ${part_quantity}    ${pquantity}
    ${puprice}=    get excel value    ${DATA.EXCEL_US734800RP}       64
    input value     ${part_unit_price}      ${puprice}
    click on    ${save_button}
    sleep   6


Verify Parts Estimate Stage Is Available OR Not
    #wait element    ${select_part_estimate}
    ${parts_est_status} =   Run Keyword And Return Status    wait until element is visible    ${select_part_estimate}
    log to console     ${parts_est_status}
    IF   '${parts_est_status}'=='True'
       Add Part In Part Estimate Stage
    ELSE
       Validate Repair Process Order with Damages and Parts
    END