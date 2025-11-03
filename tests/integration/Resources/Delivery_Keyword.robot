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



*** Variables ***

*** Keywords ***

CompleteDeliveryStage
    wait element  ${select_delivery}
    click on    ${select_delivery}
    sleep       1
    Select Frame   ${stage_frame}
    click on    ${finalize}
    sleep       5
    click on    ${ok_button}
    Unselect Frame
    log to console  Completed Delivery stage
