*** Settings ***
Library  SeleniumLibrary
Library  ExcelLibrary
Variables   constants.yaml


*** Variables ***
${env}     None
${brow}     None


*** Keywords ***

Switch Environment
      FOR    ${i}    IN RANGE    2
        IF    '${env}' == 'dev'
        ${current_url}    Set Variable    ${DEV.URL}
        ELSE IF   '${env}' == 'uat'
        ${current_url}    Set Variable    ${UAT.URL}
        END
      END
      [Return]  ${current_url}

Switch Site
      FOR    ${i}    IN RANGE    2
        IF    '${env}' == 'dev'
        ${site_id}     Set Variable    ${DEV.SITE}
        ELSE IF   '${env}' == 'uat'
        ${site_id}     Set Variable    ${UAT.SITE}
        END
      END
      [Return]  ${site_id}

Switch Auction
      FOR    ${i}    IN RANGE    2
        IF    '${env}' == 'dev'
        ${auction}     Set Variable    ${DEV.AUCTION}
        ELSE IF   '${env}' == 'uat'
        ${auction}     Set Variable    ${UAT.AUCTION}
        END
      END
      [Return]  ${auction}

Switch Browser
      FOR    ${i}    IN RANGE    2
        IF    '${brow}' == 'chrome'
        ${current_browser}    Set Variable    ${BROWSER.CHROME}
        ELSE IF   '${brow}' == 'firefox'
        ${current_browser}    Set Variable    ${BROWSER.FIREFOX}
        END
      END
      [Return]  ${current_browser}

Switch Data
      FOR    ${i}    IN RANGE    2
        IF    '${env}' == 'dev'
        ${col_num}   set variable    3
        ELSE IF   '${env}' == 'uat'
        ${col_num}   set variable    4
        END
      END
      [Return]  ${col_num}

Switch Excel Row
      FOR    ${i}    IN RANGE    2
        IF    '${env}' == 'dev'
        ${row_num}   set variable    3
        ELSE IF   '${env}' == 'uat'
        ${row_num}   set variable    2
        END
      END
      [Return]  ${row_num}


