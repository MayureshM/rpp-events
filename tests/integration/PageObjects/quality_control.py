from common_elements import get_element_by_text

select_QualityControl = "xpath://a[contains(text(),'Quality Control')]"
div_WorkCompleted = "xpath://div[contains(text(),'Work Completed')]"
div_VehicleQualityControl = "xpath://div[contains(text(),'Vehicle Quality Control')]"
div_FinalQuestions = "xpath://div[contains(text(),'Final Questions')]"
div_DeclinedInApproval = "xpath://div[contains(text(),'Final Questions')]"
span_Pass_Damage1 = "xpath:(//span[contains(text(),'Pass')])[1]"
span_Pass_Damage2 = "xpath:(//span[contains(text(),'Pass')])[2]"
span_FinalQuestions_1 = "xpath:(//span[contains(text(),'Yes')])[1]"
span_FinalQuestions_2 = "xpath:(//span[contains(text(),'Yes')])[2]"
span_FinalQuestions_3 = "xpath:(//span[contains(text(),'Yes')])[3]"
span_FinalQuestions_4 = "xpath:(//span[contains(text(),'Yes')])[4]"
button_CompleteQCStage = "xpath://span[contains(text(),'Complete')]"
button_LoopBack_Observations = "xpath://span[contains(text(),'Add Observations')]"
button_LoopBack_Estimates = "xpath://span[contains(text(),'Update Estimates')]"
button_LoopBack_Repair = "xpath://span[contains(text(),'Return to Repair')]"
button_Back = "xpath://span[contains(text(),'Back')]"
select_quality_control = "xpath://a[contains(text(),'Quality Control')]"
work_completed_ribbon = "xpath:" + get_element_by_text('Work Completed')
pass_all = "xpath:" + get_element_by_text('Pass All')
emissions_passed = "xpath:(//*[text()= 'Yes'])[1]"
perform_a_full_firmware_update = "xpath:(//*[text()= 'Yes'])[2]"
state_safety_inspection_passed = "xpath:(//*[text()= 'Yes'])[3]"
vehicle_qualifies_as_certified = "xpath:(//*[text()= 'Yes'])[4]"
complete_qc = "xpath:(" + get_element_by_text('Complete') + ")[2]"
final_question = "xpath:" + get_element_by_text('Final Questions')
lf_pass = "xpath://*[text()='Replace LF Tire']/ancestor-or-self::div[7]/following-sibling::div//span[text()='Pass']"
lr_pass = "xpath://*[text()='Replace LR Tire']/ancestor-or-self::div[7]/following-sibling::div//span[text()='Pass']"
rf_pass = "xpath://*[text()='Replace RF Tire']/ancestor-or-self::div[7]/following-sibling::div//span[text()='Pass']"
rr_pass = "xpath://*[text()='Replace RR Tire']/ancestor-or-self::div[7]/following-sibling::div//span[text()='Pass']"
return_to_repair = "xpath:" + get_element_by_text('Return to Repair')
required_message = "xpath:(" + get_element_by_text('Please return to "Repair" and provide the required DOT TIN information')+")[1]"






