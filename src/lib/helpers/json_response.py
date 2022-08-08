import json
from src.lib.encoders.uuid_encoder import UUIDEncoder
from src.lib.encoders.datetime_encoder import DateTimeEncoder
from src.lib.encoders.decimal_encoder import DecimalEncoder
from src.lib.encoders.multiple_json_encoder import MultipleJsonEncoders

def success():
  return {
    'statusCode': 200,
    'headers': {
      'Content-Type': 'application/json'
    },
    'body': json.dumps({
      'status': {
        'code': 200,
        'error_detail': '',
        'message': 'OK'
      }
    })
  }

def list_objects(objects):
  object_array = []

  for obj in objects:
    object_array.append(obj.to_dict())  

  return {
    'statusCode': 200,
    'headers': {
      'Content-Type': 'application/json'
    },
    'body': json.dumps({
      'data': {
        'results': object_array
      },
      'status': {
        'code': 200,
        'error_detail': '',
        'message': 'OK'
      }
    }, cls=MultipleJsonEncoders(UUIDEncoder, DateTimeEncoder, DecimalEncoder))
  }

def with_object(object):
  return {
    'statusCode': 200,
    'headers': {
      'Content-Type': 'application/json'
    },
    'body': json.dumps({
      'data': {
        'result': object.to_dict()
      },
      'status': {
        'code': 200,
        'error_detail': '',
        'message': 'OK'
      }
    }, cls=MultipleJsonEncoders(UUIDEncoder, DateTimeEncoder, DecimalEncoder))
  }

def with_dict(dict):
  return {
    'statusCode': 200,
    'headers': {
      'Content-Type': 'application/json'
    },
    'body': json.dumps({
      'data': {
        'result': dict
      },
      'status': {
        'code': 200,
        'error_detail': '',
        'message': 'OK'
      }
    }, cls=MultipleJsonEncoders(UUIDEncoder, DateTimeEncoder, DecimalEncoder))
  }

def bad_request(object):
  return {
    'statusCode': 400,
    'headers': {
      'Content-Type': 'application/json'
    },
    'body': json.dumps({
      'status': {
        'code': object.code,
        'error_detail': object.message,
        'message': 'BAD REQUEST'
      }
    })
  }

def unauthorized(object):
  return {
    'statusCode': 401,
    'headers': {
      'Content-Type': 'application/json'
    },
    'body': json.dumps({
      'status': {
        'code': object.code,
        'error_detail': object.message,
        'message': 'UNAUTHORIZED'
      }
    })
  }

def not_found(object):
  return {
    'statusCode': 404,
    'headers': {
      'Content-Type': 'application/json'
    },
    'body': json.dumps({
      'status': {
        'code': object.code,
        'error_detail': object.message,
        'message': 'NOT FOUND'
      }
    })
  }

def unprocessable_entity(object):  
  return {
    'statusCode': 422,
    'headers': {
      'Content-Type': 'application/json'
    },
    'body': json.dumps({
      'status': {
        'code': object.code,
        'error_detail': object.message,
        'message': 'UNPROCESSABLE ENTITY'
      }
    })
  }

def unknown_errors(object):  
  return {
    'statusCode': 422,
    'headers': {
      'Content-Type': 'application/json'
    },
    'body': json.dumps({
      'status': {
        'code': 422,
        'error_detail': f"{object.__class__.__name__}: {str(object)}",
        'message': 'UNPROCESSABLE ENTITY'
      }
    })
  }