from common_elements import get_element_by_text

select_parts = "xpath://a[contains(text(),'Parts')]"
part_items = "xpath:" + get_element_by_text('Part Available')
button_Order_Sent = "xpath://span[contains(text(),'Order Sent')]"
button_Order_Received = "xpath://span[contains(text(),'Order Received')]"

