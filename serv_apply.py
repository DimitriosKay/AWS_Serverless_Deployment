from sample.s3_bucket import S3_Create
from sample.lambda_function import Lambda_Create, User_Check, Arn_Check
from locators.client_locator import S3Client, IAMClient, LambdaClient, STSClient
import os, time, sys
from zipfile import ZipFile

s3_client = S3Client().get_client()
iam_client = IAMClient().get_client()
lambda_client = LambdaClient().get_client()
sts_client = STSClient().get_client()

s3_cli = S3_Create(s3_client)
iam_cli = Lambda_Create(iam_client)
lamb_cli = Lambda_Create(lambda_client)
sts_cli = User_Check(sts_client)

bucket_name = 'fresh-bucket-but-boto3-2020'
function_name = 'FancyLambdaFunction'
policy_name = 'LambdaPolicy'
role_name = 'LambdaRole'

def create_bucket():
    s3_cli.create_bucket(bucket_name)
    print (f'Bucket {bucket_name} was created')
    # print (bucket_creation_response['ResponseMetadata']['Location'])

def create_bucket_policy():
    bucket_policy_response = s3_cli.create_bucket_policy(bucket_name)
    print (f'Policy for {bucket_name} has been created')
    print (bucket_policy_response)
'''
def encypr ...
'''


def upload_files():
    upload_dir = os.path.dirname(os.path.abspath(__file__)) + '/docs/'
    print (upload_dir)

    docfiles = [f for f in os.listdir(upload_dir) if os.path.isfile(os.path.join(upload_dir, f))]
    print (docfiles)

    for file_name in docfiles:
        file_path = f'{upload_dir}{file_name}'
        s3_cli.upload_files(file_path, bucket_name, file_name)
        print (f'File "{file_name}" from "{file_path}" was uploaded to {bucket_name}')

def deploy_webpage():
    index_file = os.path.dirname(os.path.abspath(__file__)) + '/docs/index.html'
    print (index_file)
    error_file = os.path.dirname(__file__) + 'docs/error.html'
    print (error_file)

    s3_cli.host_website(index_file, error_file, bucket_name)

    print (f'Go to "{bucket_name}.s3-website.eu-west-2.amazonaws.com" to check out your website')

# # Creation of Lambda infrastructure # #

sts_response = sts_cli.get_caller()

def iam_setup():
    zeclass = Arn_Check()
    policy_arn = zeclass.get_arn(sts_response, policy_name)

    iam_cli.create_role(role_name)
    print (f'Role "{role_name}" created')
    iam_cli.create_policy(policy_name)
    print (f'Policy "{policy_name}" created')
    iam_cli.attach_policy(role_name, policy_arn)
    print (f'Policy attached to Role "{role_name}"')

def lambda_deploy():
    x = True

    print ('Waiting ...')
    while x:
        sys.stdout.write('[')
        sys.stdout.flush()
        for i in range(30,0,-1):
            sys.stdout.write(f'$')
            sys.stdout.flush()
            time.sleep(1)
        x = False
        print (']')
    
    # zip up that file
    file_dir = os.chdir('docs/')
    list_folder = os.listdir(file_dir)
    cwd = os.getcwd()
    
    #print (cwd)

    zipObj = ZipFile(f'{cwd}/function_test_hello.zip', 'w')

    if 'function_test_hello.py' in list_folder:
        #print ('Yas')
        zipObj.write('function_test_hello.py')
        zipObj.close()
    else:
        print ('Nah')

    # open file before sending it over
    with open(f'{cwd}/function_test_hello.zip', 'rb') as f:
        zipped_code = f.read()

    lamb_cli.create_lambda(zipped_code, function_name, sts_response)
    print ('Lambda Function created')
    lamb_cli.invoke_lambda(function_name)
    print ('Lambda Function invoked')

    os.remove(f'{cwd}/function_test_hello.zip')

if __name__ == "__main__":
    create_bucket()
    create_bucket_policy()
    
    upload_files()
    deploy_webpage()

    iam_setup()
    lambda_deploy()
