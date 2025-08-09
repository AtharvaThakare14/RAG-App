"""
Lambda function to handle authentication operations.
"""
import os
import json
import boto3
import logging
import hmac
import hashlib
import base64
from datetime import datetime

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
cognito = boto3.client('cognito-idp')

# Get environment variables
USER_POOL_ID = os.environ.get('USER_POOL_ID')
CLIENT_ID = os.environ.get('CLIENT_ID')

def handler(event, context):
    """
    Lambda function to handle authentication operations.
    
    Supported operations:
    - register: Register a new user
    - login: Authenticate a user and return tokens
    - verify: Verify email with confirmation code
    - forgot_password: Initiate forgot password flow
    - confirm_forgot_password: Complete forgot password flow
    - refresh_token: Get new tokens using a refresh token
    
    Args:
        event (dict): API Gateway event containing auth operation details
        context (object): Lambda context
        
    Returns:
        dict: Response with status code and body
    """
    logger.info(f"Received event: {json.dumps(event)}")
    
    try:
        # Extract body from the request for API Gateway calls
        body = {}
        if 'body' in event:
            if isinstance(event.get('body'), str) and event.get('body'):
                try:
                    body = json.loads(event['body'])
                except json.JSONDecodeError:
                    body = {}
            elif isinstance(event.get('body'), dict):
                body = event.get('body')
                
        # Check if this is a health check request
        if event.get('action') == 'healthcheck' or body.get('action') == 'healthcheck':
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'message': 'Authentication service is healthy'
                })
            }
        
        # Get operation type
        operation = body.get('operation')
        
        if not operation:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'message': 'Operation is required'
                })
            }
        
        # Handle different operations
        if operation == 'register':
            return register_user(body)
        elif operation == 'login':
            return login_user(body)
        elif operation == 'verify':
            return verify_user(body)
        elif operation == 'forgot_password':
            return forgot_password(body)
        elif operation == 'confirm_forgot_password':
            return confirm_forgot_password(body)
        elif operation == 'refresh_token':
            return refresh_token(body)
        else:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'message': f'Unknown operation: {operation}'
                })
            }
            
    except Exception as e:
        logger.error(f"Error processing authentication: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': f"Error processing authentication: {str(e)}"
            })
        }

def register_user(params):
    """
    Register a new user in Cognito User Pool.
    
    Args:
        params (dict): Parameters including email, password, and attributes
        
    Returns:
        dict: Response with status code and body
    """
    email = params.get('email')
    password = params.get('password')
    name = params.get('name', '')
    
    if not email or not password:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Email and password are required'
            })
        }
    
    try:
        # User attributes
        user_attributes = [
            {
                'Name': 'email',
                'Value': email
            }
        ]
        
        if name:
            user_attributes.append({
                'Name': 'name',
                'Value': name
            })
        
        # Register user
        response = cognito.sign_up(
            ClientId=CLIENT_ID,
            Username=email,
            Password=password,
            UserAttributes=user_attributes
        )
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'User registered successfully. Please check your email for verification code.',
                'user_id': response['UserSub']
            })
        }
        
    except cognito.exceptions.UsernameExistsException:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'User with this email already exists.'
            })
        }
        
    except cognito.exceptions.InvalidPasswordException as e:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': str(e)
            })
        }
        
    except Exception as e:
        logger.error(f"Error registering user: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': f"Error registering user: {str(e)}"
            })
        }

def verify_user(params):
    """
    Verify a user's email with confirmation code.
    
    Args:
        params (dict): Parameters including email and confirmation_code
        
    Returns:
        dict: Response with status code and body
    """
    email = params.get('email')
    confirmation_code = params.get('confirmation_code')
    
    if not email or not confirmation_code:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Email and confirmation code are required'
            })
        }
    
    try:
        # Confirm sign up
        cognito.confirm_sign_up(
            ClientId=CLIENT_ID,
            Username=email,
            ConfirmationCode=confirmation_code
        )
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'User verified successfully.'
            })
        }
        
    except cognito.exceptions.CodeMismatchException:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Invalid verification code.'
            })
        }
        
    except cognito.exceptions.ExpiredCodeException:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Verification code has expired.'
            })
        }
        
    except Exception as e:
        logger.error(f"Error verifying user: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': f"Error verifying user: {str(e)}"
            })
        }

def login_user(params):
    """
    Authenticate a user and return tokens.
    
    Args:
        params (dict): Parameters including email and password
        
    Returns:
        dict: Response with status code and body
    """
    email = params.get('email')
    password = params.get('password')
    
    if not email or not password:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Email and password are required'
            })
        }
    
    try:
        # Authenticate user
        response = cognito.initiate_auth(
            ClientId=CLIENT_ID,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': email,
                'PASSWORD': password
            }
        )
        
        # Extract tokens
        auth_result = response['AuthenticationResult']
        access_token = auth_result.get('AccessToken')
        id_token = auth_result.get('IdToken')
        refresh_token = auth_result.get('RefreshToken')
        expires_in = auth_result.get('ExpiresIn', 3600)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Login successful.',
                'access_token': access_token,
                'id_token': id_token,
                'refresh_token': refresh_token,
                'expires_in': expires_in,
                'token_type': 'Bearer'
            })
        }
        
    except cognito.exceptions.UserNotConfirmedException:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'User is not confirmed. Please verify your email first.',
                'error_code': 'UserNotConfirmed'
            })
        }
        
    except cognito.exceptions.NotAuthorizedException:
        return {
            'statusCode': 401,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Incorrect username or password.'
            })
        }
        
    except Exception as e:
        logger.error(f"Error logging in user: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': f"Error logging in user: {str(e)}"
            })
        }

def forgot_password(params):
    """
    Initiate forgot password flow.
    
    Args:
        params (dict): Parameters including email
        
    Returns:
        dict: Response with status code and body
    """
    email = params.get('email')
    
    if not email:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Email is required'
            })
        }
    
    try:
        # Initiate forgot password
        cognito.forgot_password(
            ClientId=CLIENT_ID,
            Username=email
        )
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Password reset initiated. Please check your email for the confirmation code.'
            })
        }
        
    except cognito.exceptions.UserNotFoundException:
        # For security reasons, still return a success message
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'If a user with this email exists, a password reset code has been sent.'
            })
        }
        
    except Exception as e:
        logger.error(f"Error initiating forgot password: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': f"Error initiating forgot password: {str(e)}"
            })
        }

def confirm_forgot_password(params):
    """
    Complete forgot password flow.
    
    Args:
        params (dict): Parameters including email, confirmation_code, and new_password
        
    Returns:
        dict: Response with status code and body
    """
    email = params.get('email')
    confirmation_code = params.get('confirmation_code')
    new_password = params.get('new_password')
    
    if not email or not confirmation_code or not new_password:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Email, confirmation code, and new password are required'
            })
        }
    
    try:
        # Confirm forgot password
        cognito.confirm_forgot_password(
            ClientId=CLIENT_ID,
            Username=email,
            ConfirmationCode=confirmation_code,
            Password=new_password
        )
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Password has been reset successfully.'
            })
        }
        
    except cognito.exceptions.CodeMismatchException:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Invalid confirmation code.'
            })
        }
        
    except cognito.exceptions.ExpiredCodeException:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Confirmation code has expired.'
            })
        }
        
    except cognito.exceptions.InvalidPasswordException as e:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': str(e)
            })
        }
        
    except Exception as e:
        logger.error(f"Error confirming forgot password: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': f"Error confirming forgot password: {str(e)}"
            })
        }

def refresh_token(params):
    """
    Get new tokens using a refresh token.
    
    Args:
        params (dict): Parameters including refresh_token
        
    Returns:
        dict: Response with status code and body
    """
    refresh_token = params.get('refresh_token')
    
    if not refresh_token:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Refresh token is required'
            })
        }
    
    try:
        # Refresh tokens
        response = cognito.initiate_auth(
            ClientId=CLIENT_ID,
            AuthFlow='REFRESH_TOKEN_AUTH',
            AuthParameters={
                'REFRESH_TOKEN': refresh_token
            }
        )
        
        # Extract tokens
        auth_result = response['AuthenticationResult']
        access_token = auth_result.get('AccessToken')
        id_token = auth_result.get('IdToken')
        expires_in = auth_result.get('ExpiresIn', 3600)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Tokens refreshed successfully.',
                'access_token': access_token,
                'id_token': id_token,
                'expires_in': expires_in,
                'token_type': 'Bearer'
            })
        }
        
    except cognito.exceptions.NotAuthorizedException:
        return {
            'statusCode': 401,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Refresh token is invalid or expired.'
            })
        }
        
    except Exception as e:
        logger.error(f"Error refreshing tokens: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': f"Error refreshing tokens: {str(e)}"
            })
        }