*** Settings ***
Library  SeleniumLibrary
Variables  ../PageObjects/common_elements.py
Variables  ../PageObjects/mechanical_inspection.py
Variables  ../PageObjects/estimate.py
Resource  ../Config/common.robot

*** Variables ***

*** Keywords ***

Add Damages from Mechanical Inspection Stage
    click on    ${select_mechanical_inspection}
    sleep   10
    select frame   ${stage_frame}
    click on  ${ok_button}
Select Mechanical Inspection Stage
    click on    ${select_mechanical_inspection}
    sleep   10
    select frame   ${stage_frame}
    click on  ${ok_button}
Adding Damages
    click on  ${search_tasks}
    @{inspection_list}    create list        12     15
    @{dmg_list}    create list      17      20
    @{severity_list}    create list      21   24
    @{recommendation_list}    create list      25   28
    @{service_list}    create list      31   34
    @{shop_list}    create list     35   38
    @{laborrate_list}    create list    39    42
    FOR    ${inspection}    ${dmg}  ${severity}   ${recommendation}   ${service}   ${shop}   ${laborrate}  IN ZIP     ${inspection_list}     ${dmg_list}   ${severity_list}   ${recommendation_list}   ${service_list}    ${shop_list}   ${laborrate_list}
             Add Observations to items    ${inspection}     ${dmg}   ${severity}   ${recommendation}  ${service}  ${shop}   ${laborrate}
    END
    click on    ${complete_button}
    click on    ${yes_button}
    Unselect Frame

Add Observations to items
    [Arguments]  ${inspection_row}   ${dmg_row}   ${severity_row}   ${recommendation_row}   ${service_row}  ${shop_row}   ${laborrate_row}
    ${data_inspection}=    get excel value    ${DATA.EXCEL_US734800RP}      ${inspection_row}
    ${inspection_type}=  create element by text   ${data_inspection}
    input text  ${search_tasks}     ${data_inspection}
    press keys    ${search_tasks}    ENTER
    click on    ${inspection_type}
#    Add Tire measurements
    click on    ${mi_fail_button}

    ${data_dmg}=    get excel value    ${DATA.EXCEL_US734800RP}      ${dmg_row}
    ${damage_type}=  create element by text  ${data_dmg}
    click on    ${damage_type}${dmg_checkbox}
    click on    ${choose_severity_enabled}

    ${data_sever}=    get excel value    ${DATA.EXCEL_US734800RP}      ${severity_row}
    ${severity_type}=  create element by text     ${data_sever}
    click on    ${severity_type}
    sleep  2
    click on    ${choose_action_enabled}
    ${data_rec}=    get excel value    ${DATA.EXCEL_US734800RP}      ${recommendation_row}
    ${recommendation_type}=  create element by text     ${data_rec}
    click on    ${recommendation_type}
    sleep  2
    click on    ${save_button}

    sleep   9
    click on   ${labor_service_type}
    ${data_service_type}=    get excel value    ${DATA.EXCEL_US734800RP}      ${service_row}
    ${service_type}=  create element by text    ${data_service_type}
    click on    ${service_type}

     click on   ${shop}
    ${data_shop}=    get excel value    ${DATA.EXCEL_US734800RP}       ${shop_row}
    ${shop_type}=  create element by text    ${data_shop}
    click on    ${shop_type}

    click on    ${labor_rate}
    ${data_laborrate}=    get excel value    ${DATA.EXCEL_US734800RP}      ${laborrate_row}
    ${laborrate}=  create element by text     ${data_laborrate}
    click on    ${laborrate}
    click on   ${labor_time}
    sleep  3
    ${labor_time_dur} =  get excel value   ${DATA.EXCEL_US734800RP}    46
    input value     ${labor_time}    ${labor_time_dur}

    click on    ${save_button}
    click on    ${mi_top_link}
    click on   ${search_tasks}
    sleep   5
Verify Paint Needed Dialog is showed or not
    log to console   " Parts is checked or not"
    ${paint_button} =   Run Keyword And Return Status    checkbox should be selected    ${Parts_needed}
    log to console    ${paint_button}
    IF  '${paint_button}'=='True'
        click on    ${save_button}
        Log to console   ${Paint_labor}
        sleep  10
        wait element    ${Paint_labor_dialog}
        click on    ${Paint_labor}
    ELSE
        click on    ${save_button}
    END

Add Tire measurements
    log to console   " Adding Tire measurements "
    ${tire_dropdown} =   Run Keyword And Return Status    page should contain checkbox   ${select_measurement}
    log to console    ${tire_dropdown}
    IF  '${tire_dropdown}'=='True'
        click on    ${select_measurement}
        ${tire_value}=    get excel value    ${DATA.EXCEL_US734800RP}     16
        ${tire_measurement}=  create element by text     ${tire_value}
        click on    ${tire_measurement}
    END

NavigatetoMI
    wait element   ${select_mechanical_inspection}
    click on  ${select_mechanical_inspection}
    sleep  2
    Select Frame   ${stage_frame}
    wait element   ${ecr_iframe}
    click on  ${ok_button}
    click on    ${complete_button}
    click on    ${yes_button}
    Unselect Frame


Navigate to Mechanical Inspection Stage with loopback
    click on    ${select_mechanical_inspection}
    sleep   10
    select frame   ${stage_frame}


Complete Mechanical Inspection stage
    wait element   ${select_mechanical_inspection}
    click on  ${select_mechanical_inspection}
    sleep  2
    Select Frame   ${stage_frame}
    wait element   ${ecr_iframe}
    click on    ${complete_button}
    click on    ${yes_button}
    Unselect Frame


Verify Rejected message
    wait element  ${select_mechanical_inspection}
    click on    ${select_mechanical_inspection}
    sleep   10
    Select Frame   ${stage_frame}
    wait until element is visible   ${ecr_iframe}
    Click Element  ${click_ok_button}
    wait until element is visible  ${Reject_text}



