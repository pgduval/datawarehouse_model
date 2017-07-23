import git
import os
import subprocess
import shutil

# Settings
TEMP_DEPLOY_PATH = "/home/elmaster/project/_tempdeploy"
TEMP_DEPLOY_MODEL_PATH = os.path.join(TEMP_DEPLOY_PATH, "model")
TEMP_DEPLOY_ETL_PATH = os.path.join(TEMP_DEPLOY_PATH, "etl")

# Repository setting
REPO_MODEL = "https://github.com/pgduval/datawarehouse_model"
REPO_ETL = "https://github.com/pgduval/datawarehouse"

MAP_REPO_FOLDER = {"model": {"repo": REPO_MODEL,
                             "folder": TEMP_DEPLOY_MODEL_PATH
                             },
                   "etl": {"repo": REPO_ETL,
                           "folder": TEMP_DEPLOY_ETL_PATH
                           }
                   }

PDI_PATH = "/home/elmaster/pentaho/data-integration"
PDI_JNDI_PATH = os.path.join(PDI_PATH, "simple-jndi", "jdbc.properties")


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
    print("JNDI deployed to location: {}".format(PDI_JNDI_PATH))


def generate_deploy_structure():
    """
    Generate folder structre
    """

    for t in ['model', 'etl']:
        folder = MAP_REPO_FOLDER[t]['folder']
        print("Generating deploy structure for {}".format(t))
        if not os.path.exists(folder):
            os.makedirs(folder)


def clean_deploy():

    print("Deleting temporary deploy folder...")
    shutil.rmtree(TEMP_DEPLOY_PATH)
    print("Done!")


def git_clone(git_type):
    """
    Clone the current verion of the model repository
    in the temporary structure.
    """
    # Clone
    repo = MAP_REPO_FOLDER[git_type]['repo']
    folder = MAP_REPO_FOLDER[git_type]['folder']
    print("Cloning repository type: {}\n".format(git_type))
    git.Repo.clone_from(repo, folder)


def git_checkout(git_type, branche='master'):
    """
    Checkout branche of the repo
    """
    print("Checking out branche: {} for type: {}\n".format(branche, git_type))
    folder = MAP_REPO_FOLDER[git_type]['folder']
    git_repo = git.Git(folder)
    git_repo.checkout(branche)


def run_etl(db_target):

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



generate_deploy_structure()

git_clone(git_type="model")
git_clone(git_type="etl")

git_checkout(git_type="model", branche="master")
git_checkout(git_type="etl", branche="master")

db_target = 'dw_preprod'
reset_db(script_path=TEMP_DEPLOY_MODEL_PATH, db_target=db_target)
generate_jndi(db_target)
run_etl(db_target)

generate_build_artifact()
clean_deploy()