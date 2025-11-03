def get_element_by_text(arg):
    return f"//*[text()= '{arg}']"


save_button = "xpath:" + get_element_by_text('Save')
cancel_button = "xpath:" + get_element_by_text('Cancel')
yes_button = "xpath:" + get_element_by_text('Yes')
no_button = "xpath:" + get_element_by_text('No')
ok_button = "xpath:" + get_element_by_text('OK')
back_button = "xpath:" + get_element_by_text('Back')
edit_button = "xpath:" + get_element_by_text('Edit')
complete_button = "xpath:(" + get_element_by_text('Complete') + ")[1]"
stage_frame = "xpath://iframe[@id='extApp']"

wo_left_menu_repair = "xpath://*[@class='description' and contains(text(),'Repair')]"
wo_left_menu_quality_control = "xpath://*[@class='description' and contains(text(),'Quality Control')]"
wo_left_menu_audit = "xpath://*[@class='description' and contains(text(),'Audit')]"
