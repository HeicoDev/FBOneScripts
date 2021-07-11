###############################
#      Created by Acewell     #
###############################
#       Edited by Heico       #
###############################

from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Frostbite 1 [X360]", ".xenontexture")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadRGBA(handle, noepyLoadRGBA)
    #noesis.logPopup()
    return 1

#check if it's this type based on the data
def noepyCheckType(data):
    bs = NoeBitStream(data, NOE_BIGENDIAN)
    Magic = bs.readBytes(4)
    print(Magic, ":magic")
    if Magic != b'RES\x02':
        if Magic != b'\x00\x00\x00\x03':
            return 0
    return 1
	
def noepyLoadRGBA(data, texList):
    bs = NoeBitStream(data, NOE_BIGENDIAN)
    check = bs.readBytes(4)
    print(check, ":check")
    if check == b'\x00\x00\x00\x03':
        bs.seek(0x8, NOESEEK_ABS)
    else:
        bs.seek(0x48, NOESEEK_ABS)
    imgFmt = bs.readInt() #???
    print(imgFmt, ":format")
    unk = bs.readInt() #???
    imgWidth = bs.readInt()            
    imgHeight = bs.readInt()           
    bs.seek(0x8, NOESEEK_REL)
    datasize = bs.readInt()
    bs.seek(0x38, NOESEEK_REL)        
    data = bs.readBytes(datasize)      
    #DXT1
    if imgFmt == 0x0:
        data = rapi.imageUntile360DXT(rapi.swapEndianArray(data, 2), imgWidth, imgHeight, 8)
        texFmt = noesis.NOESISTEX_DXT1
    #DXT5
    elif imgFmt == 0x2 or imgFmt == 0x12:
        data = rapi.imageUntile360DXT(rapi.swapEndianArray(data, 2), imgWidth, imgHeight, 16)
        texFmt = noesis.NOESISTEX_DXT5
    #raw
    elif imgFmt == 0x9:
        data = rapi.imageUntile360Raw(data, imgWidth, imgHeight, 4)
        data = rapi.imageDecodeRaw(data, imgWidth, imgHeight, "a8r8g8b8")
        texFmt = noesis.NOESISTEX_RGBA32
    #ATI1
    elif imgFmt == 0x3:
        data = rapi.imageUntile360DXT(rapi.swapEndianArray(data, 2), imgWidth, imgHeight, 8)
        data = rapi.imageDecodeDXT(data, imgWidth, imgHeight, noesis.FOURCC_ATI1)
        texFmt = noesis.NOESISTEX_RGBA32
    #unknown, not handled
    else:
        print("WARNING: Unhandled image format " + repr(imgFmt) + " - " + repr(imgWidth) + "x" + repr(imgHeight) + " - " + repr(len(data)))
        return None
    texList.append(NoeTexture(rapi.getInputName(), imgWidth, imgHeight, data, texFmt))
    return 1