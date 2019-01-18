import sys
import traceback

def throws():
    3 / 0
    
def nested():
    try:
        throws()
    except Exception as original_error:
        try:
            raise
        finally:
            try:
                cleanup()
            except:
                pass # ignore errors in cleanup

def cleanup():
    raise RuntimeError('error from cleanup')

def main():
    try:
        nested()
        return 0
    except Exception as err:
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    main()