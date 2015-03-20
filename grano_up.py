import os, json
from sys import argv, exit

from dutils.conf import DUtilsKey, DUtilsKeyDefaults, build_config, BASE_DIR, append_to_config, save_config, __load_config
from dutils.dutils import build_dockerfile, build_routine

def init_grano(with_config):
	conf_keys = [
		DUtilsKeyDefaults['USER_PWD'],
		DUtilsKeyDefaults['USER'],
		DUtilsKeyDefaults['IMAGE_NAME'],
		DUtilsKey("POSTGRES_PWD", "Postgres Password: ", "grano", "grano", None)
	]

	config = build_config(conf_keys, with_config)
	config['USER'] = config['USER'].replace("-", "").replace("_", "")

	from dutils.dutils import get_docker_exe, get_docker_ip, validate_private_key, build_bash_profile

	docker_exe = get_docker_exe()
	if docker_exe is None:
		return False

	save_config(config, with_config=with_config)

	WORKING_DIR = BASE_DIR if with_config is None else os.path.dirname(with_config)
	if not validate_private_key(os.path.join(WORKING_DIR, "%s.privkey" % config['IMAGE_NAME']), with_config):
		return False
	
	res, config = append_to_config({
		'DOCKER_EXE' : docker_exe, 
		'DOCKER_IP' : get_docker_ip()
	}, return_config=True, with_config=with_config)

	if not res:
		return False

	directives = [
		"export GRANO_SETTINGS=/home/%(USER)s/grano/settings.py" % config,
		"source ~/grano/env/bin/activate"
	]

	build_bash_profile(directives, dest_d=os.path.join(BASE_DIR, "src"))

	with open(os.path.join(BASE_DIR, "src", ".pgpass"), 'wb+') as PGPASS:
		PGPASS.write("localhost:5432:*:%(USER)s:%(POSTGRES_PWD)s" % config)

	pg_init = [
		"sudo -u postgres psql -c \"create user %(USER)s PASSWORD '%(POSTGRES_PWD)s'\" postgres" % config,
		"sudo -u postgres psql -c \"alter user %(USER)s with createdb\" postgres" % config
	]

	build_routine(pg_init, to_file=os.path.join(BASE_DIR, "src", "pg_init.sh"))

	from fabric.api import settings, local
	with settings(warn_only=True):
		if not os.path.exists(os.path.join(BASE_DIR, "src", ".ssh")):
			local("mkdir %s" % os.path.join(BASE_DIR, "src", ".ssh"))
	
		local("cp %s %s" % (config['SSH_PUB_KEY'], os.path.join(BASE_DIR, "src", ".ssh", "authorized_keys")))
	
	print "CONFIG JSONS WRITTEN."
	print config

	from dutils.dutils import generate_init_routine
	return build_dockerfile("Dockerfile.init", config) and generate_init_routine(config, with_config=with_config)


def build_grano(with_config):
	print "Step 2: build (config %s)" % with_config
	res, config = append_to_config({'COMMIT_TO' : "grano_up"}, return_config=True, with_config=with_config)
	
	if not res:
		return False

	print config

	from dutils.dutils import generate_build_routine
	return (build_dockerfile("Dockerfile.build", config) and generate_build_routine(config, with_config=with_config))
	

def commit_grano(with_config):
	try:
		config = __load_config(with_config=with_config)
	except Exception as e:
		print "commit_grano Error:"
		print e, type(e)

	if config is None:
		return False

	from dutils.dutils import generate_run_routine, generate_shutdown_routine, finalize_assets
	return (generate_run_routine(config, src_dirs=["grano"], with_config=with_config) and generate_shutdown_routine(config, with_config=with_config) and finalize_assets(with_config=with_config))

def finish_grano(with_config):
	try:
		config = __load_config(with_config=with_config)
	except Exception as e:
		print "commit_grano Error:"
		print e, type(e)

	if config is None:
		return False

	# you have to start up the thing to finish installation!?
	routine = [
		"%(DOCKER_EXE)s run --name %(IMAGE_NAME)s -iPt %(IMAGE_NAME)s:latest ./setup.sh",
		"%(DOCKER_EXE)s commit %(IMAGE_NAME)s %(IMAGE_NAME)s:latest",
		"%(DOCKER_EXE)s rm %(IMAGE_NAME)s"
	]

	return build_routine([r % config for r in routine])

def update_grano(with_config):
	return build_dockerfile("Dockerfile.update", __load_config(with_config=with_config))

if __name__ == "__main__":
	res = False
	with_config = None if len(argv) == 2 else argv[2]

	if argv[1] == "init":
		res = init_grano(with_config)
	elif argv[1] == "build":
		res = build_grano(with_config)
	elif argv[1] == "commit":
		res = commit_grano(with_config)
	elif argv[1] == "finish":
		res = finish_grano(with_config)
	elif argv[1] == "update":
		res = update_grano(with_config)
	
	print "RESULT: ", argv[1], res 
	exit(0 if res else -1)