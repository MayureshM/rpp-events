*** Settings ***
Library  SeleniumLibrary

Variables  ../PageObjects/common_elements.py
*** Variables ***
${Global_Timeout}  30
${jobid}    None
*** Keywords ***
wait element
    [Arguments]  ${element}
    wait until element is visible   ${element}     ${Global_Timeout}
    log to console  "Please wait..."

wait page has
    [Arguments]  ${element}
    Wait Until Page Contains  ${element}    ${Global_Timeout}
    log to console  "Waiting for the page has element":      ${element}

click on
    [Arguments]  ${element}
    wait element    ${element}
    sleep   1
    click element   ${element}
    sleep   2
    log to console  "Clicked on" ${element}

input value
    [Arguments]  ${element}    ${value}
    wait element    ${element}
    clear element text  ${element}
    input text  ${element}    ${value}
    sleep   1
    log to console  "Inputed the text "
    log to console  "into field"

select from list
    [Arguments]  ${element}    ${value}
    wait element    ${element}
    select from list by label  ${element}  ${value}
    log to console  "Selected the value":  ${value}

get excel value
    [Arguments]     ${file}     ${row_num}
    ${col_num}=     Switch Data
    Open Excel Document     ${file}   doc_id=docid
    ${value}=  Read Excel Cell     row_num=${row_num}	col_num=${col_num}
    sleep   2
    ${converted_value}=   convert to string     ${value}
    FOR   ${i}  IN RANGE    2
        IF  '${converted_value}'== 'None'
        ${converted_value}=    set variable  ${EMPTY}
        END
    END
    log to console      "Getting Test Data": ${file}
    log to console      "Test Data": ${converted_value}
    Close Current Excel Document
    [Return]  ${converted_value}

go to page
    [Arguments]     ${link}
    go to   ${link}
    log to console  "Navigating to": ${link} ...

create element by text
    [Arguments]     ${text}
    ${ele}=  evaluate  common_elements.get_element_by_text("${text}")  modules=common_elements
    [Return]    ${ele}

check text in string
    [Arguments]     ${str}        ${txt}
    ${match}  ${value}  Run Keyword And Ignore Error  Should Contain  ${str}     ${txt}
    [Return]    ${match}


Read Workorder sblu auctionid from excel
    [Arguments]     ${wosblu_row}
    log to console  Reading WO with sblu and auctionid..
    ${wo_sblulauc}=   get excel value    ${DATA.EXCEL_WORKORDER}      ${wosblu_row}
    Set Global Variable   ${wo_sblulauc}
    log to console   ${wo_sblulauc}

    [Return]   ${wo_sblulauc}

get work order number
    ${wo}=      evaluate        tdm.get_wo("${jobid}")      modules=tdm
    log to console  "Getting Work Order from TDM..."
    [Return]  ${wo}

get workorder sblu auction
    ${wosbluauc}=   evaluate      tdm.get_wo_sblu("${job_id}")     modules=tdm
    log to console  "Got the WO, SBLU and Auction.."
    [Return]    ${wosbluauc}

get validate vehicleAPI status with TDM WO
    ${wosbluauc}=  get workorder sblu auction
    sleep  30
    ${wostatus}=   evaluate    dynamoDB.get_latest_record("${wosbluauc}")     modules=dynamoDB
    log to console  "Getting the staus of the WO from Dynamo with TDM.."
    [Return]    ${wostatus}

get validate vehicleAPI status with excel data WO

    ${wo_slu_exc}=  evaluate    dynamoDB.get_latest_record_excel("${wo_sblulauc}")      modules=dynamoDB
    sleep  2
    Set Global Variable    ${wo_slu_exc}
    log to console  "Got the vehicleAPI staus of the WO from Dynamo with Excel source.."
    log to console    ${wo_slu_exc}
    [Return]    ${wo_slu_exc}

get repairprocessorder status from rpp-auto-integrate table
    sleep  2
    ${wo_po_status}=   evaluate    dynamoDB.process_repair_order("${wo_sblulauc}")       modules=dynamoDB
    Set Global Variable    ${wo_po_status}
    sleep  20
    log to console   "Got the repair status of the given WO SBLU and auction .."
    log toconsole   ${wo_po_status}
    [Return]    ${wo_po_status}


delete records from rpp-auto-integrate table
    sleep  2
    evaluate    dynamoDB.delete_records("${wo_sblulauc}")       modules=dynamoDB
    sleep  20
    log to console   "Deleted the records for the given WO SBLU and auction .."
    log to console   ${wo_sblulauc}
