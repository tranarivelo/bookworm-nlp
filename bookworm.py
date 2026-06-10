#!/usr/bin/env python3
import sys

if '--web' in sys.argv:
    from bookworm.server import run_server
    run_server()
else:
    from bookworm.cli import main
    main()
