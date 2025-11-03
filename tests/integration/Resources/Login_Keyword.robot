*** Settings ***
Library     SeleniumLibrary
Variables  ../PageObjects/login.py
Variables  ../PageObjects/common_elements.py
Resource  ../Config/env_var.robot
Resource  ../Config/common.robot

*** Variables ***
*** Keywords ***
Login To RPP
    ${rpp_url}=     Switch Environment
    ${rpp_browser}=     Switch Browser
    open browser        ${rpp_url}  ${rpp_browser}
    maximize browser window

    wait element   ${spn_loginIn}
    input value  ${txt_loginUserName}    ${ACCOUNT.USER}
    input value  ${txt_loginPassword}    ${ACCOUNT.PASS}
    click on  ${spn_loginIn}
    wait element   ${img_Manheim_Logo}


Logout of Browser
    close browser