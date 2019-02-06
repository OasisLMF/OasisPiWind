
node {
    hasFailed = false
    sh 'sudo /var/lib/jenkins/jenkins-chown'
    deleteDir() // wipe out the workspace

    // Set Default Multibranch config
    try {
        auto_set_branch = CHANGE_BRANCH
    } catch (MissingPropertyException e) {
        auto_set_branch = BRANCH_NAME
    }

    properties([
      parameters([
        [$class: 'StringParameterDefinition',  name: 'BUILD_BRANCH', defaultValue: 'master'],
        [$class: 'StringParameterDefinition',  name: 'MODEL_NAME', defaultValue: 'PiWind'],
        [$class: 'StringParameterDefinition',  name: 'MODEL_BRANCH', defaultValue: auto_set_branch],
        [$class: 'StringParameterDefinition',  name: 'MODEL_VERSION', defaultValue: '0.0.0.1'],
        [$class: 'StringParameterDefinition',  name: 'KEYSERVER_VERSION', defaultValue: '0.0.0.1'],
        [$class: 'StringParameterDefinition',  name: 'RELEASE_TAG', defaultValue: "build-${BUILD_NUMBER}"],
        [$class: 'StringParameterDefinition',  name: 'BASE_TAG', defaultValue: 'latest'],
        [$class: 'StringParameterDefinition',  name: 'KEYSERVER_TESTS', defaultValue: 'case_0'],
        [$class: 'StringParameterDefinition',  name: 'MODELEXEC_TESTS', defaultValue: 'case_0 case_1 case_2'],
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

    //Model data vars
    String model_test_case = "case_0"
    String model_test_dir  = "${env.WORKSPACE}/${model_workspace}/tests/integration/${model_varient}"
    String model_vers = params.MODEL_VERSION
    String model_data = "${env.WORKSPACE}/${model_workspace}/model_data/PiWind"
    String keys_vers  = params.KEYSERVER_VERSION
    String keys_data  = "${env.WORKSPACE}/${model_workspace}/keys_data/PiWind"

    // Set Global ENV
    env.PIPELINE_LOAD =  script_dir + model_sh   // required for pipeline.sh calls

    env.TAG_BASE          = params.BASE_TAG       // Build TAG for base set of images
    env.TAG_RELEASE       = params.RELEASE_TAG    // Build TAG for TARGET image
    env.TAG_RUN_PLATFORM  = params.BASE_TAG       // Version of Oasis Platform to use for testing
    env.TAG_RUN_WORKER    = env.TAG_RUN_PLATFORM   // Version of Model to use for testing
    env.TAG_RUN_KEYSERVER = params.RELEASE_TAG    // Version of Model to use for testing

    env.IMAGE_WORKER     = "coreoasis/model_execution_worker"
    env.IMAGE_KEYSERVER  = "coreoasis/${model_func}_keys_server"

    env.MODEL_SUPPLIER   = model_name
    env.MODEL_VARIENT    = model_varient

    env.VERS_KEYS_DATA   = keys_vers              // keyserver version to run unittest againts
    env.VERS_MODEL_DATA  = model_vers             // keyserver version to run unittest againts

    env.PATH_MODEL_DATA  = model_data             // mount point used when running worker containers
    env.PATH_KEYS_DATA   = keys_data              // see above
    env.PATH_TEST_DIR    = model_test_dir         // Integration Test dir for model

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
                           println(getBinding().hasVariable("CHANGE_BRANCH"))
                           sh "git clone -b ${model_branch} --single-branch --no-tags ${model_git_url} ."
                        }
                    }
                }
            }
        )
        stage('Shell Env'){
            sh  PIPELINE + ' print_model_vars'
        }
        stage('Build: ' + model_func) {
            dir(model_workspace) {
                sh PIPELINE + " build_image  docker/Dockerfile.oasislmf_piwind_keys_server ${env.IMAGE_KEYSERVER} ${env.TAG_RELEASE} ${env.TAG_BASE}"
            }
        }
        stage('Run MDK: ' + model_func) {
            dir(build_workspace) {
                String MDK_BRANCH='master'
                String MDK_RUN='ri'

                sh 'docker build -f docker/Dockerfile.mdk-tester -t mdk-runner .'
                sh "docker run mdk-runner --model-repo-branch ${model_branch} --mdk-repo-branch ${MDK_BRANCH} --model-run-mode ${MDK_RUN}" 
            }
        }
        keys_server_tests = params.KEYSERVER_TESTS.split()
        for(int i=0; i < keys_server_tests.size(); i++) {
            stage("Keys_server: ${keys_server_tests[i]}"){
                dir(build_workspace) {
                    sh PIPELINE + " run_test keys_server ${keys_server_tests[i]}"
                }
            }
        }
        model_exec_tests = params.MODELEXEC_TESTS.split()
        for(int i=0; i < model_exec_tests.size(); i++) {
            stage("model_exec: ${model_exec_tests[i]}"){
                dir(build_workspace) {
                    sh PIPELINE + " run_test  model_exec ${model_exec_tests[i]}"
                }
            }
        }
        if (params.PUBLISH){
            stage ('Publish: ' + model_func) {
                dir(build_workspace) {
                    sh PIPELINE + " push_image ${env.IMAGE_KEYSERVER} ${env.TAG_RELEASE}"
                }
            }
        }
    } catch(hudson.AbortException | org.jenkinsci.plugins.workflow.steps.FlowInterruptedException buildException) {
        hasFailed = true
        error('Build Failed')
    } finally {
        //Docker house cleaning
        dir(build_workspace) {
            sh PIPELINE + " stop_docker ${env.COMPOSE_PROJECT_NAME}"
            if(params.PURGE){
                sh PIPELINE + " purge_image ${env.IMAGE_KEYSERVER} ${env.TAG_RELEASE}"
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
