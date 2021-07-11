#!/usr/bin/env python3

import sys
import os
import os.path
import time
import shutil

## Frostbite 1 Texture Converter by Heico
## Requires Python 3.6.9! Other versions may not work.
## Use command line or drag n drop file onto the script to convert
## Supported file formats: .dds .itexture .ps3texture .xenontexture .terrainheightfield

def main():
    print("Frostbite 1 Texture Converter by Heico")

    if len(sys.argv) != 2:
        print("Wrong params! Usage: python3 fbone_txtcon.py sample.itexture")
        time.sleep(3)
        exit()

    file = sys.argv[1]

    if not os.path.exists(file):
        print("File does not exist! Make sure to enter the path correctly.")
        time.sleep(3)
        exit()

    if not file.endswith(".dds") and not file.endswith(".itexture") and not file.endswith(".ps3texture") and not file.endswith(".xenontexture") and not file.endswith(".terrainheightfield"):
        print("Wrong file format! Supported: .dds .itexture .ps3texture .xenontexture .terrainheightfield")
        time.sleep(3)
        exit()

    print("Converting file...")

    convertFile(file)

    print("DONE")

def convertFile(file: str):
    if file.endswith(".dds"):
        fileLocation = file.replace(".dds", ".itexture")

        shutil.copyfile(file, fileLocation)

        convertFileToITexture(fileLocation)
    elif file.endswith(".itexture"):
        fileLocation = file.replace(".itexture", ".dds")

        shutil.copyfile(file, fileLocation)

        convertFileToDDS(fileLocation, False)
    elif file.endswith(".ps3texture"):
        fileLocation = file.replace(".ps3texture", ".dds")

        shutil.copyfile(file, fileLocation)

        convertFileToDDS(fileLocation, True)
    elif file.endswith(".xenontexture"):
        fileLocation = file.replace(".xenontexture", ".dds")

        shutil.copyfile(file, fileLocation)

        convertFileToDDS(fileLocation, True)
    elif file.endswith(".terrainheightfield"):
        fileLocation = file.replace(".terrainheightfield", ".raw")

        shutil.copyfile(file, fileLocation)

        convertFileToRaw(fileLocation)

def convertFileToITexture(file: str):
    reader = open(file, "rb")
    dataMain = reader.read()
    reader.close()

    imgFormat = dataMain[87]
    imgWidth = int.from_bytes(dataMain[16:20], "little")
    imgHeight = int.from_bytes(dataMain[12:16], "little")
    mipmapCount = int.from_bytes(dataMain[28:32], "little")
    mipmapMinSize = 16
    headerLength = 128

    if imgFormat == 49:
        dataHeader = iTextureDXT1
        mipmapMinSize = 8
        imgFormat = "DXT1 BC1"
    elif imgFormat == 51:
        dataHeader = iTextureDXT3
        imgFormat = "DXT3 BC2"
    elif imgFormat == 53:
        dataHeader = iTextureDXT5
        imgFormat = "DXT5 BC3"
    elif imgFormat == 32:
        if dataMain[88] == 32:
            dataHeader = iTextureARGB
            imgFormat = "ARGB8888"
        elif dataMain[88] == 8:
            dataHeader = iTextureGray
            imgFormat = "Grayscale"

    if len(dataHeader) > 0:
        dataHeader[16] = dataMain[16]
        dataHeader[17] = dataMain[17]
        dataHeader[18] = dataMain[18]
        dataHeader[19] = dataMain[19]
        dataHeader[20] = dataMain[12]
        dataHeader[21] = dataMain[13]
        dataHeader[22] = dataMain[14]
        dataHeader[23] = dataMain[15]
        dataHeader[28] = dataMain[28]
        dataHeader[29] = dataMain[29]
        dataHeader[30] = dataMain[30]
        dataHeader[31] = dataMain[31]

        offset = 32

        mipmapSizes = calcMipMapSizes(imgHeight, imgWidth, mipmapCount, mipmapMinSize)

        for i in range(mipmapCount):
            size = mipmapSizes[i].to_bytes(4, "little")

            dataHeader[offset] = size[0]
            dataHeader[offset + 1] = size[1]
            dataHeader[offset + 2] = size[2]
            dataHeader[offset + 3] = size[3]

            offset += 4

        dataMain = dataMain[headerLength:]
        dataMain = dataHeader + dataMain

        writer = open(file, "wb")
        writer.write(dataMain)
        writer.close()
    else:
        if os.path.exists(file):
            os.remove(file)

def convertFileToDDS(file: str, isConsoleTexture: bool):
    reader = open(file, "rb")
    dataMain = reader.read()
    reader.close()

    res = dataMain[:3].decode("ascii")

    headerLength = 92

    if res == "RES":
        headerLength = 156

    if isConsoleTexture:
        dataMain = reverseHeader(dataMain, headerLength)

    imgFormat = int.from_bytes(dataMain[8:12], "little")

    if res == "RES":
        imgFormat = int.from_bytes(dataMain[72:76], "little")

    if imgFormat == 0 or imgFormat == 18:
        dataHeader = ddsDXT1
        imgFormat = "DXT1 BC1"
    elif imgFormat == 1:
        dataHeader = ddsDXT3
        imgFormat = "DXT3 BC2"
    elif imgFormat == 2 or imgFormat == 19 or imgFormat == 20 or imgFormat == 13:
        dataHeader = ddsDXT5
        imgFormat = "DXT5 BC3"
    elif imgFormat == 9:
        dataHeader = ddsARGB
        imgFormat = "ARGB8888"
    elif imgFormat == 10:
        dataHeader = ddsGray
        imgFormat = "Grayscale"

    if len(dataHeader) > 0:
        if res == "RES":
            dataHeader[16] = dataMain[80]
            dataHeader[17] = dataMain[81]
            dataHeader[18] = dataMain[82]
            dataHeader[19] = dataMain[83]
            dataHeader[12] = dataMain[84]
            dataHeader[13] = dataMain[85]
            dataHeader[14] = dataMain[86]
            dataHeader[15] = dataMain[87]
            dataHeader[28] = dataMain[92]
            dataHeader[29] = dataMain[93]
            dataHeader[30] = dataMain[94]
            dataHeader[31] = dataMain[95]
            dataHeader[20] = dataMain[96]
            dataHeader[21] = dataMain[97]
            dataHeader[22] = dataMain[98]
            dataHeader[23] = dataMain[99]
        else:
            dataHeader[16] = dataMain[16]
            dataHeader[17] = dataMain[17]
            dataHeader[18] = dataMain[18]
            dataHeader[19] = dataMain[19]
            dataHeader[12] = dataMain[20]
            dataHeader[13] = dataMain[21]
            dataHeader[14] = dataMain[22]
            dataHeader[15] = dataMain[23]
            dataHeader[28] = dataMain[28]
            dataHeader[29] = dataMain[29]
            dataHeader[30] = dataMain[30]
            dataHeader[31] = dataMain[31]
            dataHeader[20] = dataMain[32]
            dataHeader[21] = dataMain[33]
            dataHeader[22] = dataMain[34]
            dataHeader[23] = dataMain[35]

        dataMain = dataMain[headerLength:]
        dataMain = dataHeader + dataMain

        writer = open(file, "wb")
        writer.write(dataMain)
        writer.close()
    else:
        if os.path.exists(file):
            os.remove(file)

def convertFileToRaw(file: str):
    reader = open(file, "rb")
    data = reader.read()
    reader.close()

    headerLength = 49

    if data[0] != 0:
        headerLength = 45

    data = data[headerLength:]

    writer = open(file, "wb")
    writer.write(data)
    writer.close()

def calcMipMapSizes(height, width, mipmapCount, minSize):
    mipmapSize = int(max(1, ((width + 3) / 4))) * int(max(1, ((height + 3) / 4))) * minSize

    mipmaps = [mipmapSize]

    for i in range(mipmapCount - 1):
        if mipmapSize != minSize:
            mipmapSize /= 4

        mipmaps.append(int(mipmapSize))

    return mipmaps

def reverseHeader(data, length):
    offset = 0

    while (True):
        if offset >= length:
            break

        data = reverseFourByteBlock(data, offset)

        offset += 4
    
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

ddsDXT1 = bytearray.fromhex("444453207C00000007100A00000400000004000000000800000000000B000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000020000000040000004458543100000000000000000000000000000000000000000810400000000000000000000000000000000000")
ddsDXT3 = bytearray.fromhex("444453207C00000007100A00000200000004000000000800000000000B000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000020000000040000004458543300000000000000000000000000000000000000000810400000000000000000000000000000000000")
ddsDXT5 = bytearray.fromhex("444453207C00000007100A00000200000002000000000400000000000A000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000020000000040000004458543500000000000000000000000000000000000000000810400000000000000000000000000000000000")
ddsGray = bytearray.fromhex("444453207C00000007100200000200000002000000000000000000000A000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000020000000020000002020202008000000FF0000000000000000000000000000000810400000000000000000000000000000000000")
ddsARGB = bytearray.fromhex("444453207C00000007100A0000010000000100000000040000000000090000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000200000004100000020202020200000000000FF0000FF0000FF000000000000FF0810400000000000000000000000000000000000")

iTextureDXT1 = bytearray.fromhex("030000000000000000000000010000000004000000040000000000000B000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000")
iTextureDXT3 = bytearray.fromhex("030000000000000001000000030000000004000000020000000000000B000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000")
iTextureDXT5 = bytearray.fromhex("030000000000000002000000010000000004000000020000000000000B000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000")
iTextureGray = bytearray.fromhex("03000000000000000A000000020000000002000000020000000000000A000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000")
iTextureARGB = bytearray.fromhex("0300000000000000090000000100000080000000400000000000000001000000008000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000")

main()