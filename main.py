from typing import Dict
import user_manager
from remote.remote_manager import HostManager
import logging
import configparser
import io


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    config: configparser.ConfigParser = configparser.ConfigParser()
    config.read("config/hosts.ini")
    host_manager = HostManager(config)
    users: Dict[str, user_manager.User] = user_manager.load_from_ini("config/users.ini")

    for remote_host in host_manager.list:
        remote_host.user_list = [
            users[name.strip()]
            for name in config[remote_host.name]["managed_users"].split(",")
        ]

        for user in remote_host.user_list:
            home_dir = "{}/{}".format("" if user.name == "root" else "/home", user.name)
            auth_file_path = "{}/.ssh/authorized_keys".format(home_dir)
            try:
                io_obj = io.BytesIO()
                remote_host.get(auth_file_path, io_obj)
                content = io_obj.getvalue().decode("utf-8")
                authorized_list = [line.strip() for line in content.split("\n")]
                if user.key in authorized_list:
                    logger.info(
                        "{} already authed for {}".format(user.name, remote_host.name)
                    )
                    continue
            except:
                logger.info("{} not found on {}".format(user.name, remote_host.name))
                remote_host.run(
                    "useradd {} -m; mkdir {}/.ssh".format(user.name, home_dir)
                )
                # host.run("创建用户")
                # host.run("各种设置")

            remote_host.run("echo '{}' >> {}".format(user.key, auth_file_path))
            remote_host.run("chown -R {}:{} {}".format(user.name, user.name, home_dir))
            logger.info(
                "added ssh key for {} on {}".format(user.name, remote_host.name)
            )


if __name__ == "__main__":
    main()
