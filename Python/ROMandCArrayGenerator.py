# ROM/C array generator
# ALL CODE was 100% written by Caleb Cole (snowcoal)
# 
# inputs are various images with specific colors to denote locations of objects, or sprites
# for example, the script might detect red (0,0,255) and green (0,255,0) pixels and then use this information
# to convert dots or a pathway corner spot locations into a C array
#
# copyright Caleb Cole 2021



import cv2
import os


# generates the ROM that contains various ghost sprites, uses a 2-bit-per-pixel encoding format
def generateGhostROM():

    with open('output.txt', mode = 'w') as file:

        for img in os.listdir('inputs/'):
            inpath = "inputs/" + img

            img = cv2.imread(inpath)
            h,w, chn = img.shape

            
            # 00 = black, 01 = white, 10 = blue, 11 = "ghost color"
            for i in range(h):
                line = "32'b"
                for j in range(w):
                    pixel = img[i,j]
                    # BGR format
                    if(int(pixel[0]) + int(pixel[1]) + int(pixel[2]) < 10):
                        line += '00'
                        # line += ' '
                    elif(int(pixel[0]) > 240 and int(pixel[1]) > 240 and int(pixel[2]) > 240):
                        line += '01'
                        # line += ':'
                    elif(int(pixel[0]) > 200 and int(pixel[1]) < 100 and int(pixel[2]) < 100):
                        line += '10'
                        # line += '@'
                    else:
                        line += '11'
                        # line += '$'

                file.write(line + ",\n")

            file.write("// padding space\n")

# generates the ROM that contains the game board. The game board is intentionally 320 px wide so it fits
# nicely into a 32-bit wide ROM.
def generateBoardROM():

    with open('output2.txt', mode = 'w') as file:

        img = cv2.imread("pacman board wide.png")
        h,w, chn = img.shape

        cpy_img = img.copy()
        count = 0
        # 00 = black, 01 = white, 10 = blue, 11 = "ghost color"

        for j in range(w//32):
            for i in range(h):

                line = "32'b"

                for k in range(32):
                    pixel = img[i,j*32 + k]
                    # BGR format
                    if(int(pixel[0]) + int(pixel[1]) + int(pixel[2]) < 100):
                        line += "0"
                    else:
                        line += "1"
            
                file.write(line + ",\n")
                count += 1
            # file.write("// padding space\n")

        for i in range(4096-count):
            file.write("32'b00000000000000000000000000000000,\n")
        

        # test to see what output looks like:

        for i in range(h):
            for j in range(w):
                pixel = img[i,j]
                # BGR format
                if(int(pixel[0]) + int(pixel[1]) + int(pixel[2]) < 100):
                    cpy_img[i,j] = [255,255,255]
                else:
                    cpy_img[i,j] = [0,0,255]

        cv2.imwrite("output.png", cpy_img)

# generates module instantiations, wire instantiations, and a giant "OR" gate for all the wires
# all this is for the small dots only (4 large dots done manually)
def generateDotStuff():

    with open('output3.txt', mode = 'w') as file:

        img = cv2.imread("pacman board dot locations.png")
        h,w, chn = img.shape

        coordList = []
        count = 0

        for i in range(h):
            # line = "32'b"
            for j in range(w):
                pixel = img[i,j]
                # if pixel is clearly red
                if(int(pixel[0]) < 10 and int(pixel[1]) < 10 and int(pixel[2]) > 200):
                    coordList.append((j,i))
                    count+=1

        count = 0
        for coord in coordList:
            posX = coord[0] + 200
            posY = coord[1] + 32
            r_i0 = count // 32
            r_i1 = count % 32

            line = "sm_dot sm" + str(count) + "(.DrawX, .DrawY, .posX(" + str(posX) + "), .posY(" + str(posY) + "), .reg_input(c[" + str(r_i0) + "][" + str(r_i1) + "]), .draw(d_dot" + str(count) + "));"

            file.write(line + "\n")

            count += 1

        file.write("\n\n\n\n\n\n")

        count = 0
        for i in range(len(coordList) // 15):
            line = ""
            for j in range(15):
                line += ("d_dot" + str(count) + ", ")
                count += 1
            line += "\n"
            file.write(line)

        file.write("\n\n\n\n\n\n")

        count = 0
        for i in range(len(coordList) // 15):
            line = ""
            for j in range(15):
                line += ("d_dot" + str(count) + " || ")
                count += 1
            line += "\n"
            file.write(line)


        # print(coordList, count)


# generates C array initializations for the set of corner spots (the entire board was too big to fit in the program)
# generates C array initializations for the set of dots and their respective coordinates (the coords line up with the Verilog instantiations)
def generateCStuff():
    with open('output4.txt', mode = 'w') as file:

        img = cv2.imread("pacman board dot locations AND lines.png")
        h,w, chn = img.shape


        # OLD CODE to generate entire board:

        # output = "unsigned char board[" + str(h) + "][" + str (w) + "] = {\n"

        # for i in range(h):
        #     line = "{"
        #     for j in range(w):
        #         pixel = img[i,j]
        #         #BGR
        #         # if pixel is clearly red
        #         if(int(pixel[0]) < 10 and int(pixel[1]) < 10 and int(pixel[2]) > 200):
        #             line += "0x02"
        #         # if green
        #         elif(int(pixel[0]) < 10 and int(pixel[1]) > 200 and int(pixel[2]) < 10):
        #             line += "0x01"
        #         # if white
        #         elif(int(pixel[0]) > 200 and int(pixel[1]) > 200 and int(pixel[2]) > 200):
        #             line += "0x03"
        #         else:
        #             line += "0x00"
                
        #         # add comma (or not)
        #         if(j != w-1):
        #             line += ","
                
        #     if(i != h-1):
        #         line += "},\n"
        #     else:
        #         line += "}\n};"

        #     output += line

        output = "intersection ints[66] = {\n"
        line_count = 0

        for i in range(1,h-1):
            for j in range(1,w-1):
                pixel = img[i,j]

                # only check pixels that are red or green
                if((int(pixel[0]) < 10 and int(pixel[1]) < 10 and int(pixel[2]) > 200) or (int(pixel[0]) < 10 and int(pixel[1]) > 200 and int(pixel[2]) < 10)):
                    line = "{"
                    # top bottom left right
                    neighbors = [img[i-1,j], img[i+1,j], img[i,j-1], img[i,j+1]]
                    neighbors_out = ["0x00","0x00","0x00","0x00"]

                    count = 0
                    n_count = 0
                    for n in neighbors:
                        # if pixel is clearly red
                        if(int(n[0]) < 10 and int(n[1]) < 10 and int(n[2]) > 200):
                            neighbors_out[count] = "0x02"
                            n_count += 1
                        # if green
                        elif(int(n[0]) < 10 and int(n[1]) > 200 and int(n[2]) < 10):
                            neighbors_out[count] = "0x01"
                            n_count += 1
                        count += 1

                    # skip any in same line or less than 2 neighbors
                    if(n_count < 2):
                        continue
                    elif(n_count == 2):
                        if((neighbors_out[0] == "0x00" and neighbors_out[1] == "0x00") or (neighbors_out[2] == "0x00" and neighbors_out[3] == "0x00")):
                            continue
                    
                    line_count += 1

                    # add coords to line
                    line += (str(j) + "," + str(i) + ",")

                    # add neighbor info to line
                    for n in range(len(neighbors_out)):
                        line += neighbors_out[n]
                        if(n != len(neighbors_out) - 1):
                            line += ","
                    
                    if(line_count < 66):
                        line += '},\n'
                    else:
                        line += '}\n};'

                    output += line

        file.write(output)

        file.write("\n\n\n")

        output = "dot dots[240] = {\n"
        line_count = 0
        for i in range(h):
            for j in range(w):
                pixel = img[i,j]
                if(int(pixel[0]) < 10 and int(pixel[1]) < 10 and int(pixel[2]) > 200):
                    line_count += 1
                    output += "{1," + str(j) + "," + str(i) + "}"
                    if(line_count < 240):
                        output += ",\n"
                    else:
                        output += "\n};"

        file.write(output)


# generates ROM for scared ghosts
def generateScaredGhostROM():

    with open('output5.txt', mode = 'w') as file:
        for img in os.listdir("scared ghosts/"):
            inpath = "scared ghosts/" + img

            img = cv2.imread(inpath)
            h,w, chn = img.shape

            
            # 00 = black, 01 = white, 10 = blue, 11 = "ghost color"
            for i in range(h):
                line = "32'b"
                for j in range(w):
                    pixel = img[i,j]
                    # BGR format
                    # black
                    if(int(pixel[0]) + int(pixel[1]) + int(pixel[2]) < 10):
                        line += '00'
                    # white
                    elif(int(pixel[0]) > 240 and int(pixel[1]) > 240 and int(pixel[2]) > 240):
                        line += '01'
                    # blue
                    elif(int(pixel[0]) > 200 and int(pixel[1]) < 100 and int(pixel[2]) < 100):
                        line += '10'
                    # red
                    elif(int(pixel[0]) < 100 and int(pixel[1]) < 100 and int(pixel[2]) > 200):
                        line += '11'
                    else:
                        print("error decoding pixel")

                file.write(line + ",\n")

            file.write("// padding space\n")




# run all 4 functions
generateBoardROM()
generateGhostROM()
generateDotStuff()
generateCStuff()
generateScaredGhostROM()