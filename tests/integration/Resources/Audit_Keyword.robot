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
Variables  ../PageObjects/delivery.py
Resource  ../Config/common.robot

*** Keywords ***

Complete Audit Stage AI
    wait element  ${select_audit}
    click on  ${select_audit}
    sleep   2
    Select Frame   ${stage_frame}
    click on    ${complete_button}
    #click on    ${warning_button}
    unselect frame
    sleep   2
    log to console   Completed Audit stage

Complete Audit Stage
    wait element  ${select_audit}
    click on  ${select_audit}
    sleep   2
    Select Frame   ${stage_frame}
    click on    ${complete_button}
    #click on    ${warning_button}
    unselect frame
    sleep   2
    log to console   Completed Audit stage
