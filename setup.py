import os
import shutil
import subprocess as sp

from setuptools import find_packages, setup
from setuptools.command.install import install

# ----------------------- #


class CustomInstall(install):
    def run(self):
        # 1. clone and build sdf c lib and py wrapper
        c_repo = "https://github.com/Warwick-Plasma/SDF_C"
        utils_repo = "https://github.com/Warwick-Plasma/SDF_utilities"

        sdf_dir = "./SDF"
        c_dir = os.path.join(sdf_dir, "C")
        utils_dir = os.path.join(sdf_dir, "utilities")

        build_path = os.path.join(utils_dir, "build")
        fixed_build_path = "./utils/fixed_sdf_build"

        if not os.path.exists(sdf_dir):
            os.makedirs(sdf_dir)

        sp.check_call(["git", "clone", c_repo, c_dir])
        sp.check_call(["git", "clone", utils_repo, utils_dir])

        os.remove(build_path)
        shutil.copy(fixed_build_path, build_path)

        sp.check_call(["make", "-C", c_dir])
        sp.check_call(["sh", build_path])

        # 2. continue with the installation
        install.run(self)

        # 3. rm the SDF directory
        shutil.rmtree(sdf_dir)


# ----------------------- #

setup(packages=find_packages(), cmdclass={"install": CustomInstall})
