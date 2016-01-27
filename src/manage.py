#!/usr/bin/env python
import logging
import os
import sys

from host_moniter import hostState

if __name__ == "__main__":
#     logger = logging.getLogger(__name__)
#     pid = os.fork()
#     if pid == 0:
#         logger.info("nagios starting...")
#         hostState.main()
#  
#     else:
#         logger.info("django starting...")
#         os.environ.setdefault("DJANGO_SETTINGS_MODULE", "host_moniter.settings")
#  
#         from django.core.management import execute_from_command_line
#          
#         execute_from_command_line(sys.argv)
                
                
    logging.info("django starting...")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "host_moniter.settings")
 
    from django.core.management import execute_from_command_line
     
    execute_from_command_line(sys.argv)
    