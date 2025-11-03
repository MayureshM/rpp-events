*** Settings ***
Library  SeleniumLibrary
Variables  ../PageObjects/worklog.py
Variables  ../PageObjects/common_elements.py
Variables  ../PageObjects/admin.py
Resource  ../Config/env_var.robot
Resource  ../Config/common.robot

*** Variables ***
${search_value}    No Work Orders Found
*** Keywords ***
Select Location
    ${auction}=     switch site
    go to page   ${auction}

Search Workorder
    [Arguments]    ${work_order_num}
    sleep   5
    input value     ${txt_search_work_order}     ${work_order_num}
    sleep   1
    Press Keys    ${txt_search_work_order}    ENTER
    sleep   10
    log to console  "Completed Worklog"  +    ${work_order_num}



