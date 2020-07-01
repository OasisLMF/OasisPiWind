
node {
    hasFailed = false
    sh 'sudo /var/lib/jenkins/jenkins-chown'
    deleteDir() // wipe out the workspace

    properties([
      parameters([
        [$class: 'StringParameterDefinition',  name: 'BUILD_BRANCH', defaultValue: 'master'],
        [$class: 'StringParameterDefinition',  name: 'MODEL_NAME', defaultValue: 'PiWind'],
        [$class: 'StringParameterDefinition',  name: 'MODEL_BRANCH', defaultValue: BRANCH_NAME],
        [$class: 'StringParameterDefinition',  name: 'MDK_BRANCH', defaultValue: 'develop'],
        [$class: 'StringParameterDefinition',  name: 'MODEL_VERSION', defaultValue: '0.0.0.1'],
        [$class: 'StringParameterDefinition',  name: 'KEYSERVER_VERSION', defaultValue: '0.0.0.1'],
        [$class: 'StringParameterDefinition',  name: 'TAG_RELEASE', defaultValue: BRANCH_NAME.split('/').last() + "-${BUILD_NUMBER}"],
        [$class: 'StringParameterDefinition',  name: 'BASE_TAG', defaultValue: 'latest'],
        [$class: 'StringParameterDefinition',  name: 'RUN_TESTS', defaultValue: '0_case 1_case 3_case 4_case control_set'],
        [$class: 'BooleanParameterDefinition', name: 'BUILD_WORKER', defaultValue: Boolean.valueOf(false)],
        [$class: 'BooleanParameterDefinition', name: 'PURGE', defaultValue: Boolean.valueOf(true)],
        [$class: 'BooleanParameterDefinition', name: 'PUBLISH', defaultValue: Boolean.valueOf(false)],
        [$class: 'BooleanParameterDefinition', name: 'SLACK_MESSAGE', defaultValue: Boolean.valueOf(false)]
      ])
    ])

    // Build vars
    String build_repo = 'git@github.com:OasisLMF/build.git'
    String build_branch = params.BUILD_BRANCH
    String build_workspace = 'oasis_build'

    // Model vars
    String model_varient   = params.MODEL_NAME
    String model_branch    = params.MODEL_BRANCH
    String model_name      = 'OasisLMF'
    String model_mnt_path  = '/mnt/efs'
    String model_git_url   = "git@github.com:OasisLMF/OasisPiWind.git"
    String model_workspace = 'piwind_workspace'
    String model_func      = "${model_varient}".toLowerCase()   // function name reference <function>_<model>_<varient>
    String model_sh        = '/buildscript/utils.sh'                       //path to model build script
    String script_dir = env.WORKSPACE + "/" + build_workspace
    String PIPELINE = script_dir + "/buildscript/pipeline.sh"
    String git_creds = "1335b248-336a-47a9-b0f6-9f7314d6f1f4"

    // Update MDK branch based on model branch
    if (model_branch.matches("master") || model_branch.matches("hotfix/(.*)")){
        MDK_BRANCH='master'
    } else {
        MDK_BRANCH=params.MDK_BRANCH
    }

    //Model data vars
    String model_test_dir  = "${env.WORKSPACE}/${model_workspace}/tests/"
    String model_test_ini  = "test-config.ini"
    String model_vers = params.MODEL_VERSION
    String model_data = "${env.WORKSPACE}/${model_workspace}/model_data/PiWind"
    String keys_vers  = params.KEYSERVER_VERSION
    String keys_data  = "${env.WORKSPACE}/${model_workspace}/keys_data/PiWind"

    String MDK_RUN='ri'
    String MDK_MODEL = model_branch

    // Set Global ENV
    env.PIPELINE_LOAD =  script_dir + model_sh                          // required for pipeline.sh calls
    env.TAG_BASE             = params.BASE_TAG                          // Build TAG for base set of images
    env.TAG_RELEASE          = params.TAG_RELEASE                       // Build TAG for TARGET image
    env.TAG_RUN_PLATFORM     = params.BASE_TAG                          // Version of Oasis Platform to use for testing
    env.TAG_RUN_WORKER       = params.BASE_TAG
    env.OASIS_MODEL_DATA_DIR = "${env.WORKSPACE}/${model_workspace}"    // Model Repositry base, mounted in worker image

    env.IMAGE_WORKER     = "coreoasis/model_worker"                     // Docker image for worker

    env.TEST_MAX_RUNTIME = '190'
    env.MODEL_SUPPLIER   = model_name
    env.MODEL_VARIENT    = model_varient
    env.MODEL_ID         = '1'

    env.VERS_KEYS_DATA   = keys_vers              // keyserver version to run unittest againts
    env.VERS_MODEL_DATA  = model_vers             // keyserver version to run unittest againts
    env.PATH_MODEL_DATA  = model_data             // mount point used when running worker containers
    env.PATH_KEYS_DATA   = keys_data              // see above
    env.TEST_DATA_DIR    = model_test_dir         // Integration Test dir for model
    env.MULTI_PERIL      = '1'                    // Set the GUL alloc rule to 1 in compose

    env.COMPOSE_PROJECT_NAME = UUID.randomUUID().toString().replaceAll("-","")

    try {
        parallel(
            clone_build: {
                stage('Clone: ' + build_workspace) {
                    dir(build_workspace) {
                       git url: build_repo, credentialsId: git_creds, branch: build_branch
                    }
                }
            },
            clone_model: {
                stage('Clone: ' + model_func) {
                    sshagent (credentials: [git_creds]) {
                        dir(model_workspace) {
                            sh "git clone --recursive ${model_git_url} ."
                            if (model_branch.matches("PR-[0-9]+")){
                                sh "git fetch origin pull/$CHANGE_ID/head:$BRANCH_NAME"
                                sh "git checkout $CHANGE_TARGET"
                                sh "git merge $BRANCH_NAME"

                            } else {
                                // Checkout branch
                                sh "git checkout ${model_branch}"
                            }
                        }
                    }
                }
            }
        )

        if (params.BUILD_WORKER){
            env.TAG_RUN_WORKER = params.TAG_RELEASE
            stage('Build Worker'){
                dir(build_workspace) {
                    sh  "docker build --no-cache -f docker/Dockerfile.worker-git --pull --build-arg BRANCH=${MDK_BRANCH} -t coreoasis/model_worker:${params.TAG_RELEASE} ."
                }
            }
        } else {
            sh "curl https://api.github.com/repos/OasisLMF/OasisPlatform/tags | jq -r '( first ) | .name' > last_release_tag"
            env.LAST_RELEASE_TAG = readFile('last_release_tag').trim()
            env.TAG_RUN_WORKER = env.LAST_RELEASE_TAG
        }

        stage('Shell Env'){
            sh  PIPELINE + ' print_model_vars'
        }
        stage('Run MDK Py3.6: ' + model_func) {
            dir(build_workspace) {
                sh "sed -i 's/FROM.*/FROM python:3.6/g' docker/Dockerfile.mdk-tester"
                sh 'docker build -f docker/Dockerfile.mdk-tester -t mdk-runner:3.6 .'
                sh "docker run mdk-runner:3.6 --model-repo-branch ${MDK_MODEL} --mdk-repo-branch ${MDK_BRANCH} --model-run-mode ${MDK_RUN}"

            }
        }

        api_server_tests = params.RUN_TESTS.split()
        for(int i=0; i < api_server_tests.size(); i++) {
            stage("Run : ${api_server_tests[i]}"){
                dir(build_workspace) {
                    sh PIPELINE + " run_test --test-output --config /var/oasis/test/${model_test_ini} --test-case ${api_server_tests[i]}"
                }
            }
        }
    } catch(hudson.AbortException | org.jenkinsci.plugins.workflow.steps.FlowInterruptedException buildException) {
        hasFailed = true
        error('Build Failed')
    } finally {
        //Docker house cleaning
        dir(build_workspace) {
            sh 'docker-compose -f compose/oasis.platform.yml -f compose/model.worker.yml logs server-db      > ./stage/log/server-db.log '
            sh 'docker-compose -f compose/oasis.platform.yml -f compose/model.worker.yml logs server         > ./stage/log/server.log '
            sh 'docker-compose -f compose/oasis.platform.yml -f compose/model.worker.yml logs celery-db      > ./stage/log/celery-db.log '
            sh 'docker-compose -f compose/oasis.platform.yml -f compose/model.worker.yml logs rabbit         > ./stage/log/rabbit.log '
            sh 'docker-compose -f compose/oasis.platform.yml -f compose/model.worker.yml logs worker         > ./stage/log/worker.log '
            sh 'docker-compose -f compose/oasis.platform.yml -f compose/model.worker.yml logs worker-monitor > ./stage/log/worker-monitor.log '
            sh PIPELINE + " stop_docker ${env.COMPOSE_PROJECT_NAME}"

            if(params.PURGE){
                //sh PIPELINE + " purge_image mdk-runner-3.6"
                //sh PIPELINE + " purge_image mdk-runner-2.7"
            }
        }
        //Notify on slack
        if(params.SLACK_MESSAGE && (params.PUBLISH || hasFailed)){
            def slackColor = hasFailed ? '#FF0000' : '#27AE60'
            SLACK_GIT_URL = "https://github.com/OasisLMF/${model_name}/tree/${model_branch}"
            SLACK_MSG = "*${env.JOB_NAME}* - (<${env.BUILD_URL}|${env.RELEASE_TAG}>): " + (hasFailed ? 'FAILED' : 'PASSED')
            SLACK_MSG += "\nBranch: <${SLACK_GIT_URL}|${model_branch}>"
            SLACK_MSG += "\nMode: " + (params.PUBLISH ? 'Publish' : 'Build Test')
            SLACK_CHAN = (params.PUBLISH ? "#builds-release":"#builds-dev")
            slackSend(channel: SLACK_CHAN, message: SLACK_MSG, color: slackColor)
        }
        //Git tagging
        if(! hasFailed && params.PUBLISH){
            sshagent (credentials: [git_creds]) {
                dir(model_workspace) {
                    sh PIPELINE + " git_tag ${env.TAG_RELEASE}"
                }
            }
        }
        //Store logs
        dir(build_workspace) {
            archiveArtifacts artifacts: 'stage/log/**/*.*', excludes: '*stage/log/**/*.gitkeep'
            archiveArtifacts artifacts: "stage/output/**/*.*"
        }
    }
}
