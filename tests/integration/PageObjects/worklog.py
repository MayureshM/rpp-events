# Import Work Order - Dashboard page Elements
title = "xpath://span[@class='navbar-text title']"
work_orders_tab = "xpath://div[contains(text(),'Work Orders')]"
work_order_text = "xpath://label[contains(text(),'New Work Order')]"

btn_LocationMenu = "xpath://button[contains(text(),'SOUTHERN CALIFORNIA')]"
link_SetLocationPLM1 = "xpath://a[contains(text(),'PLM1')]"
txt_enterWorkOrder = "xpath://input[@id='new-work'] [@placeholder='Enter new Work Order']"
Add_WorkOrder  = "id:new-work-button"
loader = "xpath://i[@class='table-index-loader fa fa-circle-o-notch fa-spin']"
duplicate_work_order_error = "xpath://div[@class='window-header']"
accept_duplicate_work_order_error = "xpath://button[@class='btn btn-primary']"
Verify_WorkOrder = "xpath://html/body/recon-root/ng-component/div/div[2]/ng-component/div/div[2]/div[2]/recon-table/div/div[2]/div[4]/recon-cell/div"
verify_UserId = "xpath://button[contains(text(),'Recon Admin')]"
check_Work_Order = "xpath://a[contains(text(),'Vehicle Qualification')]"
check_Work_OrderMI = "xpath://a[contains(text(),'Mechanical Inspection')]"

# Search Work Order
txt_searchWorkOrder = "xpath://div[@class='col']//input[@id='new-work']"
search_work_order = "xpath://span[@class='sign-glyph glyphicon glyphicon-search']"
Search_Result = "xpath://html/body/recon-root/ng-component/div/div[2]/ng-component/div/div[2]/div[2]/recon-table/div/div[2]/div[4]/recon-cell/div"

no_wo_found = "xpath://div[contains(text(),'No Work Orders Found')]"
# headers
admin = "xpath://div[contains(text(),'Admin')]"

# Duplicate Work Order
alert_DuplicateWorkOrder = "xpath://div[contains(text(),'Error')]"
alert_AcceptError = "xpath://button[contains(text(),'OK')]"
# Delete
no_data_found = "xpath://td[contains(text(),'No data found')]"




