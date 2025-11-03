from common_elements import get_element_by_text

select_part_estimate = "xpath://a[contains(text(),'Parts Estimate')]"
repair_estimate_ribbon = "xpath:" + get_element_by_text('Repair Estimates')

add_part_icon = "/../../../../../../..//*[@class='icon add-part']"

part_name = "xpath://input[@name='partName']"
part_source = "xpath://*[@name='siteSourceId']/../div[1]"
part_num = "xpath://*[@name='partNum']"
part_quantity = "xpath://*[@name='quantity']"
part_unit_price = "xpath://*[@name='unitPrice']"
part_ext_price = "xpath://*[@name='partExtendedPrice']/../../div[1]"

repair_estimates_count = "xpath://div[@class='x-container x-unsized header-task-collapse']"
input_PartName = "xpath://input[@name='partName']"
input_PartNum = "xpath://input[@name='partNum']"
input_PartQuantity = "xpath://input[@name='quantity']"
input_PartUnitPrice = "xpath://input[@name='unitPrice']"
dropDown_PartSource = "xpath:(//form/div/div[2]/div[2]/div/div)[1]"
dropDown_SelectPartSource = "xpath://span[contains(text(),'AMERICAN TIRE DISTRIBUTORS')]"
add_labor = "xpath://div[@class='x-container x-unsized x-paint-monitored add-labor']"
add_part1 = "xpath:(//span[@title = 'Add Part'])[1]"
add_part2 = "xpath:(//span[@title = 'Add Part'])[2]"
button_BackFromPartsScreen = "xpath://span[(text() = 'Back')]"
button_CompletePartsEstimate = "xpath://span[contains(text(),'Complete')]"
button_SaveAddedParts = "xpath://span[(text() = 'Save')]"
