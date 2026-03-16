import logging
import os

def setup_logging(log_file='pipeline.log'):
    os.makedirs('logs', exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO, # Do not log anything below this level of severity
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f'logs/{log_file}'),
            logging.StreamHandler()
        ],
        force=True  # Override pre-existing config
    )