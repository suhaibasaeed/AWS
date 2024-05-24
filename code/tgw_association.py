from functools import lru_cache

import json
import logging
import boto3

from pip._internal import main

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    try:
      """Get AWS region of new VPC attachment & it's ID from EventBridge Event. Get RGW RT IDs from SSM params and create tgw association & propagation """
        # Obtaining information from the event
        region = event['detail']['transitGatewayAttachmentArn'].split(':')[3]
        tgw_attachment = event['detail']['transitGatewayAttachmentArn'].split('/')[1]

        # Boto3 clients
        ssm = boto3.client('ssm', region_name=region)
        ec2 = boto3.client('ec2', region_name=region)

        # Obtaining the Transit Gateway route table IDs from Systems Manager Parameter Store
        tgw_inspection_rt = ssm.get_parameter(Name="tgw-inspection-rt")['Parameter']['Value']
        tgw_spoke_rt = ssm.get_parameter(Name="tgw-spoke-rt")['Parameter']['Value']

        # We create Transit Gateway association and propagation to the route table
        tgw_association = ec2.associate_transit_gateway_route_table(
            TransitGatewayRouteTableId=tgw_spoke_rt,
            TransitGatewayAttachmentId=tgw_attachment
        )['Association']['ResourceId']
        tgw_propagation = ec2.enable_transit_gateway_route_table_propagation(
            TransitGatewayRouteTableId=tgw_inspection_rt,
            TransitGatewayAttachmentId=tgw_attachment
        )['Propagation']['ResourceId']
            
        response = {
            'transitGatewayAssociationId': tgw_association,
            'transitGatewayPropagationId': tgw_propagation
        }

        return {
            'statusCode': 200,
            'body': json.dumps(response)
        }
    
    except Exception as e:
        # Printing the error in logs
        print(e)
        return {
            'statusCode': 500,
            'body': json.dumps('Something went wrong. Please check the logs.')
        }
