#!/bin/bash

set -o errexit -o pipefail -o noclobber -o nounset

OPTIONS=ipbd
LONGOPTS=install,pre_build,build,deploy

! PARSED=$(getopt --options=$OPTIONS --longoptions=$LONGOPTS --name "$0" -- "$@")

if [[ ${PIPESTATUS[0]} -ne 0 ]]; then
    # e.g. return value is 1
    #  then getopt has complained about wrong arguments to stdout
    exit 2
fi

eval set -- "$PARSED"

i=0 p=0 b=0 d=0 env=0

while true; do
    case "$1" in
        -i|--install)
            i=1
            shift
            ;;
        -p|--pre_build)
            p=1
            shift
            ;;
        -b|--build)
            env=1
            b=1
            shift
            ;;
        -d|--deploy)
            env=1
            d=1
            shift
            ;;
        --)
            shift
            break
            ;;
        *)
            ;;
    esac
done

if [[ $env -eq 1 ]]; then
  source env.sh
fi

if [[ $i -eq 1 ]]; then
  mkdir -p build
  cp -r src/* build/
  pip install --quiet --upgrade pip
  pip install --quiet --upgrade awscli
  pip install --quiet -t build/ -r src/requirements.txt --upgrade  --extra-index-url https://pip.reconmvs.com
fi

if [[ $p -eq 1 ]]; then
  find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf
  pip install --quiet --upgrade -r src/requirements.txt --extra-index-url https://pip.reconmvs.com
  pylint src --output-format=colorized --disable=C0111,W0142,W0201,R0903,R0924,E1101,R0801,R0201,C0103,W0102,W0613
fi

if [[ $b -eq 1 ]]; then
  sed "s/@Environment@/${CODEBUILD_GIT_BRANCH}/g" swaggerSpec.yaml | sed "s/@Account@/${AWS_ACCOUNT}/g" | sed "s/@Authorizer@/${AUTHORIZER}/g" > $CODEBUILD_GIT_BRANCH-rpp-events-swagger.yaml
  cp $CODEBUILD_GIT_BRANCH-rpp-events-swagger.yaml swaggerSpec.yaml
  cat swaggerSpec.yaml
  aws cloudformation package \
    --template-file template.yml \
    --s3-bucket $FUNCTION_BUCKET \
    --output-template-file rpp-events-cf-deploy.cf.yml
  cat rpp-events-cf-deploy.cf.yml
fi

if [[ $d -eq 1 ]]; then
  aws cloudformation deploy \
    --template-file rpp-events-cf-deploy.cf.yml \
    --stack-name $CODEBUILD_GIT_BRANCH-rpp-events \
    --capabilities CAPABILITY_NAMED_IAM \
    --parameter-overrides \
    EnvironmentName=$CODEBUILD_GIT_BRANCH \
    LogLevel=$LOG_LEVEL
  aws s3 cp $CODEBUILD_GIT_BRANCH-rpp-events-swagger.yaml s3://$API_BUCKET
fi
