import os
import sys

# Ensure src directory is in sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from main import Main

if __name__ == '__main__':
    app = Main()
    app.mainloop()
