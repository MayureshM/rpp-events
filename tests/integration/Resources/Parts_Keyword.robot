*** Settings ***
Library  SeleniumLibrary
Variables  ../PageObjects/common_elements.py
Variables  ../PageObjects/parts.py
Resource  ../Config/common.robot
*** Variables ***

*** Keywords ***
Complete Part Stage
    click on  ${select_parts}
    sleep   2
    Select Frame   ${stage_frame}
    FOR     ${i}    IN RANGE    1
        click on    ${part_items}
    END
    Unselect Frame
    sleep   2


Verify Workorder is in Parts/Repair Stage
    ${parts_status} =   Run Keyword And Return Status    wait until element is visible    ${select_parts}
    log to console     ${parts_status}
    IF   '${parts_status}'=='True'
        wait element    ${select_parts}
    ELSE
        wait element   ${select_Repair}
    END