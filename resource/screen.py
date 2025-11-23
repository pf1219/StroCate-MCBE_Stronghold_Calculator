def read_coords():
    screen=pyautogui.screenshot()
    s=np.array(screen)
    shape=s.shape
    search_w=int(max(shape[1]/3,min(125,shape[1])))
    search_h=int(shape[0]/3)

    start_x=0
    start_y=0
    streak=0

    coords=[0,0,0]
    coordindex=0
    signed=False

    CM = {
        0b0111110: 0, 0b0000001: 1, 0b0100011: 2, 0b0100010: 3, 0b0001100: 4, 
        0b1110010: 5, 0b0011110: 6, 0b1100000: 7, 0b0110110: 8, 0b0110000: 9
    }
    white = np.array([255, 255, 255], dtype=np.uint8)

    for y in range(30,search_h):
        for x in range(8,search_w):
            if np.array_equal(s[y][x],white):
                if start_x==0:
                    start_x=x
                    start_y=y
                streak=streak+1
            elif streak<4:
                streak=0
            else:
                break
        if streak>=4:
            break


    if streak>=4:
        scale=int(streak/4)
        start_x=start_x+scale*44

        while start_x<search_w:
            cM=0b0
            for dy in range(7):
                cM <<= 1
                current_y=start_y+dy*scale
                if np.array_equal(s[current_y][start_x],white):
                    cM |= 0b1

            digit=-1
            if cM in CM:
                digit=CM[cM]
            elif cM==0b0001000:
                signed=True
            elif cM==0b0000011:
                if signed:
                    coords[coordindex]=coords[coordindex]*-1
                coordindex=coordindex+1
                signed=False
            else:
                if coordindex>=2:
                    break

            if digit!=-1:
                coords[coordindex] = coords[coordindex] * 10 + digit
            start_x=start_x+scale*6

        if signed and coordindex<3:
            coords[coordindex] *= -1
    else:
        coords=-1

    return(coords)
    
