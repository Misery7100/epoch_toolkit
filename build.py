import os
import shutil
import subprocess as sp


def build_sdf():
    c_repo = "https://github.com/Warwick-Plasma/SDF_C"
    utils_repo = "https://github.com/Warwick-Plasma/SDF_utilities"

    sdf_dir = "./SDF"
    c_dir = os.path.join(sdf_dir, "C")
    utils_dir = os.path.join(sdf_dir, "utilities")

    build_path = os.path.join(utils_dir, "build")
    fixed_build_path = "./utils/fixed_sdf_build"

    if os.path.exists(sdf_dir):
        shutil.rmtree(sdf_dir)

    os.makedirs(sdf_dir)

    sp.check_call(["git", "clone", c_repo, c_dir])
    sp.check_call(["git", "clone", utils_repo, utils_dir])

    os.remove(build_path)
    shutil.copy(fixed_build_path, build_path)

    sp.check_call(["make", "-C", c_dir])
    sp.check_call(["sh", build_path])

    shutil.rmtree(sdf_dir)


if __name__ == "__main__":
    build_sdf()
