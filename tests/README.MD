# rpp-events automation

## TDMInventoryAPI documentation
https://manheimtestdata-internal.tdm.manheim.com//api_docs/swagger_docs/v3

## Run automation from terminal

* Set virtual env for python3
* Install robotframework -> pip3 install robotframework
* Run -> pip3 install -r requirements.txt
* From AWS ALKS console, copy the authentication for the environment and paste it in your terminal 
* cd tests/integration and then run the test cases with the below command with your information
* python3 -m robot --variable requested_by:maheswari.manoharan@coxautoinc.com --variable auction_code:PLM1 --variable number_of_items:1 --variable vehicle_status:RC --variable seller_number:4995396 --variable capture_and_condition:CaptureOnly --pythonpath . --output ./output/output.xml --report ./output/report.html --log ./output/log.html ./test_capture_event.robot
