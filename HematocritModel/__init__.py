import logging
import os
import traceback

import azure.functions as func
from healthrex_ml.deployers import SklearnDeployer

from utils import cosmos

import pdb

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    CSN = req.params.get('CSN')
    if not CSN:
        return func.HttpResponse(
            'This function executed unsuccessfully. No patient id provided.',
            status_code=400
        )

    try:
        model_path = '20230105_label_HCT_deploy.pkl'
        deployer = SklearnDeployer(
            filepath=f"HematocritModel/{model_path}",
            credentials={'username' : os.environ['secretID'],
                        'password' : os.environ['secretpass']},
            csn=CSN,
            env=os.environ['EPIC_ENV'],
            client_id=os.environ['EPIC_CLIENT_ID'],
        )
        inference = deployer()
        cosmos.cosmoswrite(
            patient=deployer.patient_dict,
            container_id='20230302_CBC_With_Differential',
            partition_key=model_path)
        score_success = True
    except Exception as e:
        deployer.get_patient_identifiers()
        error_dict = {
            'FHIR STU3' : deployer.patient_dict['FHIR STU3'],
            'Error': traceback.format_exc(),
            'model': model_path
        }
        cosmos.cosmoswrite(patient=error_dict,
                           container_id='20230302_CBC_With_Differential',
                           partition_key= model_path)
        score_success = False
    
    if score_success:   
        return func.HttpResponse(
            f"Successful inference: {inference}",
            status_code=200)
    else:
        return func.HttpResponse(
             "Inference not succesful",
             status_code=400
        )
