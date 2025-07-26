import os

from utils.utils import setup_logger

dataset_list = os.getenv("DATASET_LIST").split(",")
prefix = os.getenv("PREFIX")

def main():
    logger = setup_logger()

    # read xml as strings

    # read xsd as strings 

    # validate xml against xsd schemas 

    # validate xml quality checks

    # write db 

if __name__ == '__main__':
    main()