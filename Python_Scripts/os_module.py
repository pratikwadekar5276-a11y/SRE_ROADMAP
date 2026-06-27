import os as f

f.getcwd()
if f.path.exists('/Users/pratikwadekar/Desktop/python_automation1'):
    print('Path exists')
else:
    print('Path does not exist')
#f.chdir('/Users/pratikwadekar/Desktop/python_automation')
#f.mkdir('new_directory')
#f.rmdir('new_directory')
#f.remove('new_directory')
#f.rename('new_directory', 'new_directory_renamed')

print(f.listdir('/Users/pratikwadekar/Desktop'))