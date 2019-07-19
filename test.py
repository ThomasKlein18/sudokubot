

def function(zahl):
    if zahl >= 0:
        return 2 * function(zahl-1)
    else:
        return 1

if __name__ == "__main__":
    print(function(5))