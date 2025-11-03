from common_elements import get_element_by_text


select_Approve = "xpath://a[contains(text(),'Approve')]"
button_ApproveAll = "xpath://div[@id='globalApproveAll']"
button_ApproveALl_OK = "xpath://span[contains(text(),'OK')]"
button_Decline_Labor = "xpath://div[contains(@class,'x-container x-unsized inspection-estimate x-paint-monitored')]/div[contains(@class,'x-inner inspection-estimate-inner')]/div[contains(@class,'x-container x-unsized estimate-labor-detail x-dataview')]/div[contains(@class,'x-inner x-dataview-inner')]/div[contains(@class,'x-unsized x-dataview-container')]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/button[2]"
button_Decline_Part = "xpath://div[contains(@class,'x-dataview-item x-item-selected x-item-pressed')]//div[contains(@class,'part')]//button[contains(@class,'')][contains(text(),'Decline')]"
button_Complete_ApproveStage = "xpath://span[contains(text(),'Complete')]"
div_Success_Approval = "xpath://div[contains(@class,'x-container x-unsized summary-batch-wrapper')]//div[contains(@class,'x-innerhtml')][contains(text(),'Success')]"

# Loop Back
button_ReEstimate = "xpath://span[text()='Re-Estimate']"
select_approve = "xpath://a[contains(text(),'Approve')]"
approve_all_items = "xpath://*[text()='Complete']/../../../../div//*[text()='Approve All']"


#Reject
select_Reject = "xpath:" + get_element_by_text('Reject')

#Reject Reason
reject_reason_dialog = "xpath://div[contains(text(),'Enter reason for rejection')]"
reject_reason_dropdown = "xpath://input[@type='text']/../div[1]"
reject_ok ="xpath://span[text()='OK']"