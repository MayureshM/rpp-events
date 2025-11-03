from common_elements import get_element_by_text

admin_page = "xpath:" + get_element_by_text('Admin')
recon = "xpath:" + get_element_by_text('RECON')


# SITE CONFIG
# work_order_tab
link_site_config = "xpath://span[contains(text(),'Site Config')]"
select_site = "xpath://select[@name='siteDropdown']"
select_location = "xpath//option[contains(text(),'MANHEIM PLM1')]"
work_order_tab = "xpath://a[contains(text(),'Work Orders')]"
input_work_order = "xpath://input[@placeholder='Search']"
search = "xpath://i[@class='fa fa-search']"
delete_work_order = "xpath://button[contains(text(),'Delete')]"
delete_work_order_alert = "xpath://div[contains(text(),'Delete Work Order')]"
confirm_delete_work_order = "xpath://button[contains(text(),'Yes')]"
back_to_ip = "xpath://img[@class='image']"
no_wo_found = "xpath://td[text()='No data found']"

# site_customer_tab
site_customers_tab = "xpath://a[@class='nav-link active']"
customer_name = "xpath://input[@placeholder='Customer Name']"
seller_id = "xpath://input[@placeholder='Seller Id']"
customer_group = "xpath://input[@placeholder='Customer Group']"
workflow_type = "xpath://select[@name='wholesale']"
client_type = "xpath://select[@name='wholesaleClient']"
customer_edit = "xpath://tr[3]//td[6]//button[1]"
customer_add = "xpath://table[contains(@class,'recon-table table')]//button[@class='btn btn-secondary'][contains(text(),'Add')]"

# shops tab
shops_tab = "xpath://a[@class='nav-link active']"
shop_name = "xpath//input[@placeholder='Shop Name']"
shop_abbrevation = "xpath://input[@placeholder='Shop Abbrev']"
shop_clocking = "xpath://select[@name='shopLevelClocking']"
physical_shop = "xpath://input[@placeholder='Physical Shop']"
sublet = "xpath://input[@placeholder='Physical Shop']"
default_sublet_vendor = "xpath://select[@name='defaultSubletVendorId']"
shops_add = "xpath://table[contains(@class,'recon-table table')]//button[@class='btn btn-secondary'][contains(text(),'Add')]"
shops_edit = "xpath://tr[20]//td[7]//button[1]"
shops_delete = "xpath://tr[20]//td[8]//button[1]"

# CUSTOMER CONFIG
customer_config = "xpath://span[contains(text(),'Customer Config')]"
customer_config_location = "xpath://select[@name='siteDropdown']"
customer_dropdown = "//select[@name='customerDropdown']"

# USER CONFIG
user_config = "xpath://span[contains(text(),'User Config')]"
add_new_user = "xpath://button[contains(text(),'Add New User')]"
search_user = "xpath://input[@placeholder='Search']"
click_search = "xpath://i[@class='fa fa-search']"

user_information_tab = "xpath://a[contains(text(),'User Information')]"
enter_user_name = "xpath//input[@placeholder='User Name']"
enter_first_name = "xpath://input[@placeholder='First Name']"
enter_last_name = "xpath://input[@placeholder='Last Name']"
enter_email = "xpath:input[@placeholder='Email']"
enter_phone_no = "xpath://input[@name='phoneNumber']"

roles = "xpath//a[@class='nav-link'][contains(text(),'Roles')]"
available_roles = "xpath://h4[contains(text(),'Available Roles')]"
select_all_roles = "xpath://button[@class='btn btn-link']"

sites_tab = "xpath://a[@class='nav-link'][contains(text(),'Sites')]"
select_all_sites = "xpath://button[@class='btn btn-link']"

customers_tab = "xpath://a[@class='nav-link active'][contains(text(),'Customers')]"
all_wholesale_customers = "xpath://div[@class='xtime-list-selector']//div[1]//label[1]"
all_retail_customers = "xpath:///div[@class='select-all']//div[2]//label[1]"

notifications_tab = "xpath://a[contains(text(),'Notifications')]"
select_email_notification = "xpath:/input[@name='emailNotification']"
select_text_message = "xpath://input[@name='smsNotification']"

save_user_create = "xpath://button[contains(text(),'Save')]"
cancel_user_create = "xpath://button[contains(text(),'Cancel')]"


# AUTH CONFIG
auth_config = "xpath://span[contains(text(),'Auth Config')]"
roles_tab = "xpath://a[contains(text(),'Roles')]"
add_new_role = "xpath//button[contains(text(),'Add New Role')]"
role_information = "xpath://a[contains(text(),'Role Information')]"
role_name = "xpath://input[@placeholder='Role Name']"
save_role_create = "xpath://button[contains(text(),'Save')]"
cancel_role_create = "xpath://button[contains(text(),'Cancel')]"





































