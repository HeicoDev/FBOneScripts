#!/usr/bin/env python3.9

import sys
import os
import os.path
import time
import shutil

## Frostbite 1 File Porter by Heico (experimental) (WIP)
## Ports files from Frostbite 1 games (console) to BFBC2 (PC) 
## Requires Python 3.9.6! Other versions may not work.
## Use command line or drag n drop file onto the script to convert
## Supported file formats: .terrainheightfield .watermesh .visualwater .ps3texture .xenontexture

def main():
    print("Frostbite 1 File Porter by Heico (experimental) (WIP)")

    #if len(sys.argv) != 2:
    #    print("Wrong params! Usage: python3 fbone_fileporter.py sample.watermesh")
    #    time.sleep(3)
    #    exit()

    file = "/home/nico/Documents/VSCodeProjects/FBOneScripts/test.visualwater" #sys.argv[1]

    if not os.path.exists(file):
        print("File does not exist! Make sure to enter the path correctly.")
        time.sleep(3)
        exit()
 
    global fileExtension
    fileExtension = os.path.splitext(file)[1]

    if not fileExtension == ".ps3texture" and not fileExtension == ".xenontexture" and not fileExtension == ".terrainheightfield" and not fileExtension == ".watermesh" and not fileExtension == ".visualwater":
        print("Wrong file format! Supported: .terrainheightfield .watermesh .visualwater .ps3texture .xenontexture")
        time.sleep(3)
        exit()

    print("Converting file...")

    convertFile(file)

    print("DONE")

def convertFile(file: str):

    print(fileExtension)

    reader = open(file, "rb")
    data = reader.read()
    reader.close()

    if fileExtension == ".terrainheightfield":
        data = convertTerrainHeightField(file)
    elif fileExtension == ".watermesh":
        data = convertWaterMesh(file)
    elif fileExtension == ".visualwater":
        data = convertVisualWater(file)
    elif fileExtension == ".terrainmaterialmap":
        data = convertTerrainMaterialMap(file)
    elif fileExtension == ".visualterrain":
        data = convertVisualTerrain(file)
    elif fileExtension == ".ps3texture" or fileExtension == ".xenontexture":
        data = convertTexture(file)

    outputFile = os.path.dirname(file) + "/output" + fileExtension
    
    if os.path.exists(outputFile):
        os.remove(outputFile)

    writer = open(file, "wb")
    writer.write(data)
    writer.close()

def convertTerrainHeightField(data):
    #Return unmodified data if PC header (4 zero bytes at position 41). The console files of BFBC2 also have 4 zero bytes at position 41.           
    #TODO: Porting the heightmaps of BFBC2 from console to PC is probably unnecessary, but I will still try to look for a better check.
    if data[41] == 0 and data[42] == 0 and data[43] == 0 and data[44] == 0:
        return data

    #Extend header by 4 zero bytes at position 41 to fit the structure and size of the PC header (TODO: Do only if BFBC or BF1943 file)
    dataHeader = data[:49]

    dataHeader[45] = dataHeader[41]
    dataHeader[46] = dataHeader[42]
    dataHeader[47] = dataHeader[43]
    dataHeader[48] = dataHeader[44]
    dataHeader[41] = 0
    dataHeader[42] = 0
    dataHeader[43] = 0
    dataHeader[44] = 0

    data = data[45:]
    data = dataHeader + data

    offset = 0
    dataLength = len(data)

    #reverse header
    while (True):
        if offset >= 49:
            break

        #skip one unknown zero byte at position 36
        if offset == 36:
            offset += 1

        data = reverseFourByteBlock(data, offset)

        offset += 4

    #reverse first data chunk
    while (True):
        if offset >= 8388653:
            break

        data = reverseTwoByteBlock(data, offset)

        offset += 2

    #reverse second data chunk
    while (True):
        if offset >= dataLength:
            break

        data = reverseFourByteBlock(data, offset)

        offset += 4

    bloatAmount = 10485760 - dataLength

    bloat = bytes(bloatAmount)

    for i in range(len(bytes)):
        bloat[i] = 0

    data = data + bloat 

    return data

def convertWaterMesh(data):
    offset = 0
    dataLength = len(data)

    #Whole file including header can be reversed in 4 byte blocks
    while (True):
        if offset >= dataLength:
            break

        data = reverseFourByteBlock(data, offset)

        offset += 4

    return data 

def convertVisualWater(data):
    pass

def convertTerrainMaterialMap(data):
    pass

def convertVisualTerrain(data):
    pass

def convertTexture(data):
    pass

def reverseTwoByteBlock(data, offset):
    temp0 = data[offset]
    temp1 = data[offset + 1]

    data[offset] = temp1
    data[offset + 1] = temp0

    return data

def reverseFourByteBlock(data, offset):
    temp0 = data[offset]
    temp1 = data[offset + 1]
    temp2 = data[offset + 2]
    temp3 = data[offset + 3]

    data[offset] = temp3
    data[offset + 1] = temp2
    data[offset + 2] = temp1
    data[offset + 3] = temp0

    return data

main()