
# Opening file
helptxt = open('help-out.txt', 'r')

classes = {None: []} 
args = {None: ''}
activeArg = None
activeClass = None

count = 0
# Read in the file
for line in helptxt:
    lstr = line.strip()
    if(lstr[0:2] != "--"):
        args[activeArg] = args[activeArg] + lstr
        continue
    else: # New arg
        lstr = lstr[2:]
        left = lstr[0:75]
        right = lstr[75:]
        activeArg = left.split(' ',1)[0]
        activeClass = activeArg.split('.',1)
        if len(activeClass) == 1:
            activeClass = None
        else:
            activeClass = activeClass[0]
        
        if activeClass in classes.keys():
            classes[activeClass].append(activeArg)
        else:
            classes[activeClass] = [activeArg]

        activeArg = activeArg.split(' ',1)
        if len(activeArg) > 1:
            argDefaults = activeArg.split(' ',1)[1]
        else:
            argDefaults = ''
        activeArg = activeArg[0]

        if activeArg in args.keys():
            args[activeArg] = args[activeArg] + ' ' + right
        else:
            args[activeArg] = argDefaults + right

        count += 1
    # if count == 0:
    #     break

print(classes)

print(args)

# Closing files
helptxt.close()

out = open('help.txt', 'w')
out.write(".. code-block:: cfg\n\n")

for ioclass, iargs in classes.items():
    if(ioclass is None):
        l = 0
        pass
    else:
        out.write('  ['+ioclass+']'+'\n')
        l = len(ioclass)+1

    for arg in iargs:        
        out.write('  {:75}{}\n'.format(arg[l:], args[arg]))

    out.write('\n')

out.close()

# Writing to file
# file1 = open('myfile.txt', 'w')
# file1.writelines(L)
# file1.close()
 