FROM public.ecr.aws/lambda/python:3.9

RUN pip install -U pip
RUN pip install pipenv 

COPY [ "Pipfile", "./" ]

RUN pipenv install --system --deploy

COPY [ "drift_lambda.py", "helperFunctions.py", "./" ]

CMD [ "drift_lambda.lambda_handler" ]