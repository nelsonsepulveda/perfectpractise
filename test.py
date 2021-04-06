def generate_list():
    return [1,2,3,4,5]
    
def print_list(a):
    print(a)
    
def generate_dict():
    return {'a':1, 'b':2, 'c':3, 'd':4}
    
def print_dict(d):
    print(d)
    

if __name__ == "__main__":
#    print_list(generate_list())
#    print_dict(generate_dict())
    
    for x, y, z in zip([1,2,3], [4,5,6], [7,8,9,10]):
        print(x, y, z)
    print("----------------------")
