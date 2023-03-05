import datetime
from datetime import timedelta
import logging
import azure.functions as func

from healthrex_ml.deployers.label_extractors import LabComponentLabelExtractor

def main(mytimer: func.TimerRequest) -> None:
    """
    Triggers once a day to pair inferences to labels. Dates here hardcoded,
    in prod subtract from utc_timestamp for desired range. 
    """
     
    # For development only
    TEST_LOCAL=True

    # Get now
    utc_timestamp = datetime.datetime.utcnow()

    # Grab inference between these dates
    start_date = '2023-03-03'
    end_date = '2023-03-04'

    extractor = LabComponentLabelExtractor(
        base_name='HCT',
        inference_container_id='20230302_CBC_With_Differential',
        inference_date_from=start_date,
        inference_date_to=end_date,
        inference_partition_key='20230105_label_HCT_deploy.pkl',
        output_container_id='20230302_CBC_With_Differential_with_labels'
    )
    extractor()

    logging.info(f"Inference From: {start_date}")
    logging.info(f"Inference To: {end_date}")

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)

