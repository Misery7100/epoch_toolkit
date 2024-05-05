import os
import shutil
import subprocess as sp

from setuptools import find_packages, setup
from setuptools.command.install import install


class CustomInstall(install):
    def run(self):
        sdf_dir = "./SDF"
        sdf_repo = "https://github.com/Warwick-Plasma/SDF"
        build_path = os.path.join(sdf_dir, "utilities/build")
        fixed_build_path = "./utils/fixed_sdf_build"

        if not os.path.exists(sdf_dir):
            sp.check_call(["git", "clone", "--recurse-submodules", sdf_repo, sdf_dir])

        os.remove(build_path)
        shutil.copy(fixed_build_path, build_path)

        sp.check_call(["make", "-C", os.path.join(sdf_dir, "C")])
        sp.check_call(["sh", build_path])
        install.run(self)

        shutil.rmtree(sdf_dir)


setup(packages=find_packages(), cmdclass={"install": CustomInstall})
