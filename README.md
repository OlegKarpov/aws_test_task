# README #

### Basic setup ###
#### Python dependencies and aws cli setup

1. Install python requirements (in case you don't have it installed yet).
    In the terminal:
    ```
    pip install -r requirements.txt
    ```

2. Set awscli credentials (Public key, Private key):
    ```
    aws configure
    ```
    
3. Generate template (lambda.json):
    ```
    python generate_cloudformation_template.py
    ```
    
4. Stack operations:
    ```
    sceptre create dev
    ```
    If you need to delete stack:
    ```
    sceptre delete dev
    ```