from setuptools import setup

if __name__ == "__main__":
    setup(
        name="PO Backend API",
        version="1.0",
        description="The P&O3 Parking garage Backend.",
        author="CW1B2",
        packages=["api", "core"],
        package_dir={"api": "src/api", "core": "src/core"},
    )
