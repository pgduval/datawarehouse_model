import git
import os
import subprocess
import shutil
import time

# --- Settings ----

# Temporary deploy location
TEMP_DEPLOY_PATH = "/home/elmaster/project/_tempdeploy"
TEMP_DEPLOY_MODEL_PATH = os.path.join(TEMP_DEPLOY_PATH, "model")
TEMP_DEPLOY_ETL_PATH = os.path.join(TEMP_DEPLOY_PATH, "etl")

# Path to autodoc tool
KETTLE_COOKBOOK_PATH = "/home/elmaster/project/kettle-cookbook"

# Repository setting
REPO_MODEL = "https://github.com/pgduval/datawarehouse_model"
REPO_ETL = "https://github.com/pgduval/datawarehouse"

# Kettle path
PDI_PATH = "/home/elmaster/pentaho/data-integration"
PDI_JNDI_PATH = os.path.join(PDI_PATH, "simple-jndi", "jdbc.properties")

# --------------------

MAP_REPO_FOLDER = {"model": {"repo": REPO_MODEL,
                             "folder": TEMP_DEPLOY_MODEL_PATH
                             },
                   "etl": {"repo": REPO_ETL,
                           "folder": TEMP_DEPLOY_ETL_PATH
                           }
                   }


def generate_jndi(db_target):
    """
    Generate the JNDI for the given db_target
    """

    print("Generate JNDI for environnement: {}...\n".format(db_target))
    jndi_file = """bdtarget/type=javax.sql.DataSource
bdtarget/driver=com.mysql.jdbc.Driver
bdtarget/url=jdbc:mysql://localhost:3306/{db_target}
bdtarget/user={db_target}
bdtarget/password={db_target}
""".format(db_target=db_target)
    print(jndi_file)
    with open(PDI_JNDI_PATH, "w") as text_file:
        text_file.write(jndi_file)
    time.sleep(1)
    print("JNDI deployed to location: {}".format(PDI_JNDI_PATH))


def generate_deploy_structure():
    """
    Generate temporary folder structure for deploy
    """
    for t in ['model', 'etl']:
        folder = MAP_REPO_FOLDER[t]['folder']
        print("Generating deploy structure for {}".format(t))
        if not os.path.exists(folder):
            os.makedirs(folder)


def clean_deploy():
    """
    Destroy temporary folder created for the build
    """
    print("Deleting temporary deploy folder...")
    shutil.rmtree(TEMP_DEPLOY_PATH)
    print("Done!")


def git_clone(git_type):
    """
    Clone the current verion of the model repository
    in the temporary structure.
    """
    repo = MAP_REPO_FOLDER[git_type]['repo']
    folder = MAP_REPO_FOLDER[git_type]['folder']
    print("Cloning repository type: {}\n".format(git_type))
    git.Repo.clone_from(repo, folder)
    print("Done!")


def git_checkout(git_type, branche='master'):
    """
    Checkout branche of the repo
    """
    print("Checking out branche: {} for type: {}\n".format(branche, git_type))
    folder = MAP_REPO_FOLDER[git_type]['folder']
    git_repo = git.Git(folder)
    git_repo.checkout(branche)


def run_etl(db_target):
    """
    Call Kitchen executor
    """

    # Prepare JNDI for the target database
    generate_jndi(db_target)

    # Start Kitchen execution
    print("Starting ETL execution to load target {}\n".format(db_target))
    commands = '''
    cd {pdi_path}
    ./kitchen.sh -rep=datawarehouse -file={etl_path}
    '''.format(pdi_path=PDI_PATH,
               etl_path=os.path.join(TEMP_DEPLOY_ETL_PATH, "jb_load_warehouse.kjb")).encode("utf8")

    process = subprocess.Popen('/bin/bash',
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               shell=True)
    out, err = process.communicate(commands)
    print(out)


def generate_etl_documentation():
    """
    Execute the Kettle-Cookbook autodoc
    """
    print("Starting ETL Documentation process\n".format(db_target))
    commands = '''
    cd {pdi_path}
    ./kitchen.sh -file={cookbook}/pdi/document-folder.kjb -param:"INPUT_DIR"={input} -param:"OUTPUT_DIR"={output}
    '''.format(pdi_path=PDI_PATH,
               cookbook=KETTLE_COOKBOOK_PATH,
               input=os.path.join(TEMP_DEPLOY_ETL_PATH),
               output=os.path.join(TEMP_DEPLOY_ETL_PATH, 'documentation', 'output')).encode("utf8")

    process = subprocess.Popen('/bin/bash',
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               shell=True)
    out, err = process.communicate(commands)
    print(out)


def generate_build_artifact():
    print("not implemented")
    pass


# Main execution

generate_deploy_structure()

git_clone(git_type="model")
git_clone(git_type="etl")

git_checkout(git_type="model", branche="master")
git_checkout(git_type="model", branche="develop")

git_checkout(git_type="etl", branche="master")

db_target = 'dw_preprod'
reset_db(script_path=TEMP_DEPLOY_MODEL_PATH, db_target=db_target)

run_etl(db_target)

generate_etl_documentation()

generate_build_artifact()
clean_deploy()
