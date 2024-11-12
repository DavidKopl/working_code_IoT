
def initialize():
    """Načte kalibrační hodnoty z ecdata.txt nebo nastaví výchozí hodnoty."""
    global _kvalueLow, _kvalueHigh
    try:
        with open('ecdata.txt', 'r') as f:
            _kvalueLow = float(f.readline().strip('kvalueLow='))
            _kvalueHigh = float(f.readline().strip('kvalueHigh='))
    except:
        print("ecdata.txt ERROR! Please run reset function to create default settings.")
        sys.exit(1)